import os
import re
import cgi
import pdb
from server import WatermelonServer, WSGIRefServer
import threading
import traceback
from template import process_template
import reloader

HTTP_CODES = {
    200: 'OK', 
    404: 'NOT FOUND',
    500: 'INTERNAL SERVER ERROR'
}

# Ensures that values for each request
# are specific to that request
request = threading.local()

# Exceptions
class WatermelonException(Exception):
    pass


class NotFound(WatermelonException):
    pass


# Classes
class App:
    """ 
    The Watermelon App class holds the routes for the framework, handles
    the WSGI interaction between watermelon and the server, and runs watermelon
    as a web server.
    """
    def __init__(self):
        self.simple_routes = {}
        self.variable_routes = {}

    def WSGIhandler(self, env, start_response):
        setup_thread(request, Request(env))
        try: 
            response = self.match_request(request)
        except NotFound:
            response = Response()
            response.status_code = 404
            response.txt = 'Route could not be found'
        except Exception as e: 
            response = Response()
            response.status_code = 500
            response.txt = traceback.format_exc().replace('\n','<br>')
        print response.status
        print type(response.status)
        start_response(response.status, response.headers)
        return response.txt

    def route(self, path, **kwargs):
        def route_decorator(func):
            self.add_route(path, func, **kwargs)
            return func
        return route_decorator

    def make_path(self, path):
        path = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)$', path)
        return path

    def add_route(self, path, func, method="GET"):
        if isinstance(method, list):
            for item in method:
                self.create_route(path, func, item)
        elif isinstance(method, str):
            self.create_route(path, func, method)
        else:
            raise TypeError

    def create_route(self, path, func, method):
        if re.match(r'^/(\w+/)*\w*$', path):
            self.simple_routes.setdefault(method, {})[path] = func
        else:
            path = self.make_path(path)
            self.variable_routes.setdefault(method, {})[path] = func

    def check_response_type(self, route_response):
        if isinstance(route_response, Response):
            return route_response
        else:
            response = Response()
            response.txt = route_response
            return response

    def match_request(self, request):
        func = self.simple_routes.get(request.method, {}).get(request.path, None)
        if func:
            route_response = func()
            return self.check_response_type(route_response)
            
        routes = self.variable_routes.get(request.method, {})
        for key, value in routes.items():
            match = re.match(key, request.path)
            if match:
                args = match.groupdict()
                route_response = value(**args)
                return self.check_response_type(route_response)
         
        raise NotFound()

    def run(self, server=WatermelonServer, host='localhost', port=8000, reload_on=True):
        """ Runs watermelon as a web server, with its own built-in server as a default
        You may also chooose to use Python's wsgiref server, or a different server"""

        srv = server(host, port)
        
        print "Watermelon is running on %s:%d" %(host, port)
        if reload_on:
            reloader.run_with_reloader(srv.run, self.WSGIhandler)
        else:
            srv.run(self.WSGIhandler)
        


class Request:
    """
    Represents a single request as an object. The Request object is binded to 
    a thread local using setup_thread inside the WSGIhandler.
    """
    def __init__(self, env):
        self.path = env.get('PATH_INFO','/').strip()
        self.method = env.get('REQUEST_METHOD', '/')
        self.args = self.parse_data(env)

    def parse_data(self, env):
        if self.method == 'POST':
            args = self.parse_post_data(env)
        elif self.method == 'GET':
            args = self.parse_get_data(env)
        else:
            raise ValueError
        args = self.fix_args_array(args)
        return args
    
    def fix_args_array(self, args):
        for key, value in args.items():
            if len(value) == 1:
                args[key] = value[0]
        return args 
    
    def parse_post_data(self, env):
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
        if request_body_size == 0:
            request_body = env['wsgi.input'].read() 
        else:
            request_body = env['wsgi.input'].read(request_body_size)
        data = cgi.parse_qs(request_body)
        return data

    def parse_get_data(self, env):
        return cgi.parse_qs(env['QUERY_STRING'])


class Response:
    """
    Represents a response to a request as an object. Allows the user to add
    headers to the response
    """
    def __init__(self):
        self.status_code = 200
        self.header_dict = {'Content-Type': 'text/html'}
        self.txt = ''
    
    @property
    def status (self):
        status_text = HTTP_CODES[self.status_code]
        return '%d %s' % (self.status_code, status_text)
    
    def add_header_item(self, key, value):
        self.header_dict[key] = value

    @property
    def headers (self):
        return list(self.header_dict.items())


#binds the environment of the request to the request holder
def setup_thread(holder, request):
    for name, value in request.__dict__.items():
        setattr(holder, name, value)


class Template:
    """ 
    Creates a cache for all the templates being read. When a template needs
    to be rendered in the response, watermelon will first check if this template
    is already in the template cache before rebuilding the template
    """

    def __init__(self):
        self.template_cache = {}

    def read_template(self, filename):
        tmp = open(filename)
        txt = tmp.read()
        tmp.close()
        return txt

    def template_cache_get(self, filename):
        return self.template_cache.get(filename, (None, None))

    def cache_template(self, filename, template, mtime):
        self.template_cache[filename] = (template, mtime)
        
    def render(self, filename, scope):
        f_mtime = os.stat(filename).st_mtime
        print 'f_time', f_mtime
        template, mtime = self.template_cache_get(filename)
        if not template and f_mtime != mtime:
            txt = self.read_template(filename)
            template = process_template(txt, scope)
            self.cache_template(filename, template, mtime)
        return template.render(scope)


template_cache = Template()
def render_template(filename, **kwargs):
    """ Reads and renders a file using the watermelon template-engine """
    scope = kwargs
    template = template_cache.render(filename, scope)
    print template_cache.template_cache
    return template
