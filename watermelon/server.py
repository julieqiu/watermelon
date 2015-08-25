from StringIO import StringIO
from urlparse import urlparse
import threading
import socket
import struct


class ServerAdapter(object):
    def __init__(self, host='localhost', port=8000, **kwargs):
        self.host = host
        self.port = int(port)
        self.options = kwargs

    def __repr__(self):
        return "%s (%s:%d)" % (self.__class__.__name__, self.host, self.port)

    def run (self, handler):
        pass


class WSGIRefServer(ServerAdapter):
    """ Python's built-in wsgiref server """
    def run(self, handler):
        from wsgiref.simple_server import make_server
        srv = make_server(self.host, self.port, handler)
        srv.serve_forever()


class Connection:
    """ Establishes a connection to the client for the watermelon server """
    def __init__(self, socket, wsgi_handler):
        self.socket = socket
        self.wsgi_handler = wsgi_handler

    def timeout(self, timeout=10):
        sec = int(timeout)
        usec = int((timeout - sec) * 1e6)
        timeval = struct.pack('ll', sec, usec)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)

    def start_response(self, status, headers):
        self.socket.sendall('HTTP/1.1 ')
        self.socket.sendall(status+'\n')
        for key, value in headers:
            if key.lower() == 'connection':
                continue
            if key.lower() == 'content-length':
                self.content_length_set = True
            self.socket.sendall(key+': '+value+'\n')
        self.socket.sendall('Connection: keep-alive\n')

    def serve(self):
        self.timeout() 
        try:
            while True: 
                self.content_length_set = False
                env = self.get_env()
                output = self.wsgi_handler(env, self.start_response)
                if not self.content_length_set:
                    content_length = -1
                    if isinstance(output, str):
                        content_length = str(len(output))
                    if hasattr(output, '__len__') and len(output) == 1:
                        for item in output:
                            content_length = str(len(item))
                    if content_length != -1:
                        self.socket.sendall('Content-Length: '+content_length+'\n')
                self.socket.sendall('\n')
                self.socket.sendall(output)
                if not self.content_length_set and content_length == -1:
                    break
        finally:
            self.socket.close()
            
    def parse_request(self, first_line):
        first_line = first_line.rstrip('\r\n')
        return first_line.split()
    
    def socket_readline(self):
        c = ''
        line = ''
        while c != '\n':
            c = self.socket.recv(1)
            line += c
        return line

    def recv_exact(self, count):
        line = ""
        while count != 0:
            chunk = self.socket.recv(count)
            line += chunk
            count -= len(chunk)
        return line

    def get_env(self):
        env = {}
        line = self.socket_readline()
        request_method, url, request_version = self.parse_request(line)
        result = urlparse(url) 
        env['REQUEST_METHOD'] = request_method
        env['PATH_INFO'] = result.path
        env['QUERY_STRING'] = result.query
        env['SERVER_PROTOCOL'] = request_version

        while True:
            line = self.socket_readline().rstrip('\r\n') 
            if line == "":
                content_length = int(env.get('HTTP_CONTENT-LENGTH', 0))
                line = self.recv_exact(content_length) 
                env['wsgi.input'] = StringIO(line)
                break
            else:
                line = line.split(':', 1)
                env['HTTP_'+line[0].upper()] = line[1]
        print env
        return env



class WatermelonServer(ServerAdapter):
 
    def run(self, wsgi_handler):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(10)
        
        while True:
            c, addr = s.accept()
            conn = Connection(c, wsgi_handler) 
            t = threading.Thread(target=conn.serve, args=()) 
            t.setDaemon(True)
            t.start()
