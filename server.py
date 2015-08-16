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
    def run(self, handler):
        from wsgiref.simple_server import make_server
        srv = make_server(self.host, self.port, handler)
        srv.serve_forever()


class SocketServer(ServerAdapter):
    def run(self, wsgi_handler):
        import socket
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(10)
        
        while True:
            c, addr = s.accept()
            request = c.recv(1000)
            env = self.get_env(request)
            response = wsgi_handler(env, self.start_response)
            c.sendall(response)
            #response = return_response() 
            #print response
            #c.send(response)
            
            c.close()
    
    def start_response(self, status, response_headers):
        pass
    
    def parse_request(self, request):
        msg = request[:]
        msg = msg.split('\r\n')
        first_line = msg[0].split(' ')
        request_line = request.splitlines()[0]
        request_line = request_line.rstrip('\r\n')
        return request_line.split() 
    
    def get_env(self, request):
        env = {}
        request_method, path, request_version = self.parse_request(request)
        env['REQUEST_METHOD'] = request_method
        env['PATH_INFO'] = path
        env['SERVER_PROTOCOL'] = request_version
        
        print env
        return env

class HTTPConnector(ServerAdapter):
    def run(self):
        from socket import socket
        s = socket()
        s.connect((self.host, self.port))
        return s

