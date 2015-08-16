import re
import cgi
from server import SocketServer, WSGIRefServer

def return_response():
    return """ HTTP/1.1 200 OK\r\n\r\nHello, World!"""

class App:
    def __init__(self):
        self.simple_routes = {}
        self.variable_routes = {}

    def WSGIhandler(self, env, start_response):
        print env
        status = '200 OK'
        response_headers = [('Content-Type','text/html')]
        start_response(status, response_headers)
        output = self.match_request(env)
        return output

    def post_request(self, environ):
        print '**POST DATA**'
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        request_body = environ['wsgi.input'].read(request_body_size)
        data = cgi.parse_qs(request_body)
        print data
        #fp = env['wsgi.input']
        #data = cgi.FieldStorage(fp=fp, environ=env)
        #print data
        #print type(data)
        for key, value in data.items():
            print key, value

    def route(self, path, **kwargs):
        def route_decorator(func):
            self.add_route(path, func, **kwargs)
            return func
        return route_decorator

    def make_path(self, path):
        path = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)$', path)
        return path

    def add_route(self, path, func, method="GET"):
        if re.match(r'^/(\w+/)*\w*$', path):
            self.simple_routes.setdefault(method, {})[path] = func
        else:
            path = self.make_path(path)
            self.variable_routes.setdefault(method, {})[path] = func

    def match_request(self, env):
        path = env.get('PATH_INFO','/').strip()
        method =  env.get("REQUEST_METHOD",'/')
        
        if method == 'POST': 
            self.post_request(env)
        
        func = self.simple_routes.get(method, {}).get(path, None)
        if func:
            return func()
        
        routes = self.variable_routes.get(method, {})
        for key, value in routes.items():
            match = re.match(key, path)
            if match:
                args = match.groupdict()
                return value(**args)
         
        return "HTTP/1.0 404 \r\n\r\n404 Error"

    def run(self, server=SocketServer, host='localhost', port=8000):
        srv = server(host, port)
        print "Watermelon is running on %s:%d" %(host, port)
        srv.run(self.WSGIhandler)


def read_template(template):
    tmp = open(template)
    txt = tmp.read()
    tmp.close()
    return txt
    
def render_template(template, **kwargs):
    txt = read_template(template)
    variables = kwargs
    for key, value in variables.items():
        txt = re.sub(r'{{(\s)*'+key+'(\s)*}}', value, txt)
    return txt

