import SimpleHTTPServer
import BaseHTTPServer
import logging
import os

logger = logging.getLogger("blogofile.server")

class Server:
    def __init__(self, port):
        self.port = int(port)
    def start(self):
        #We're guaranteed to be in the blogofile root after main runs
        #So change to the _site dir that should be built directly beneath it:
        os.chdir("_site")
        server_address = ('',self.port)
        HandlerClass = SimpleHTTPServer.SimpleHTTPRequestHandler
        ServerClass = BaseHTTPServer.HTTPServer
        HandlerClass.protocol_version="HTTP/1.0"
        self.httpd = ServerClass(server_address, HandlerClass)
        sa = self.httpd.socket.getsockname()
        print("Blogofile server started on port %s ..." % sa[1])
        self.httpd.serve_forever()
    def shutdown(self):
        print("shutting down..")
        self.httpd.shutdown()
        #TODO: why doesn't this actually shut it down?
        
