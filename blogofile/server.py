import SimpleHTTPServer
import BaseHTTPServer
import logging
import os
import re
from urlparse import urlparse
<<<<<<< HEAD:blogofile/server.py
import threading
=======
>>>>>>> built-in webserver now correctly handles sites built inside subdirectories.:blogofile/server.py

from blogofile import config, util

logger = logging.getLogger("blogofile.server")

class Server(threading.Thread):
    def __init__(self, port):
        self.port = int(port)
        threading.Thread.__init__(self)
        self.is_shutdown = False
        server_address = ('',self.port)
        HandlerClass = BlogofileRequestHandler
        ServerClass = BaseHTTPServer.HTTPServer
        HandlerClass.protocol_version="HTTP/1.0"
        self.httpd = ServerClass(server_address, HandlerClass)
        self.sa = self.httpd.socket.getsockname()
    def run(self):
        print("Blogofile server started on port %s ..." % self.sa[1])
        self.httpd.serve_forever()
    def shutdown(self):
        print("\nshutting down webserver...")
        self.httpd.shutdown()
        self.httpd.socket.close()
        self.is_shutdown = True
        #TODO: why doesn't this actually shut it down?
<<<<<<< HEAD:blogofile/server.py

class BlogofileRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.BLOGOFILE_SUBDIR_ERROR = """\
=======
        
BLOGOFILE_SUBDIR_ERROR = """\
>>>>>>> built-in webserver now correctly handles sites built inside subdirectories.:blogofile/server.py
<head>
<title>Error response</title>
</head>
<body>
<h1>404 Error</h1>
Your Blogofile site is configured for a subdirectory, maybe you were looking
for the root page? : <a href='"""+\
    urlparse(config.site_url).path + "'>"+urlparse(config.site_url).path+\
    "</a>\n"+\
    "</body>"
<<<<<<< HEAD:blogofile/server.py
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self, *args, **kwargs)
    def translate_path(self, path):
        site_path = urlparse(config.site_url).path
        if(len(site_path.strip("/")) > 0 and
           not path.startswith(site_path)):
            self.error_message_format = self.BLOGOFILE_SUBDIR_ERROR
            return "" #Results in a 404
        p = SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(
            self, path)
        if len(site_path.strip("/")) > 0:
            build_path = os.path.join(
                os.getcwd(),
                util.path_join(site_path.strip("/")))
        else:
            build_path = os.getcwd()
        build_path = re.sub(build_path, os.path.join(os.getcwd(),"_site"), p)
        return build_path
    
    def log_message(self, format, *args):
        pass
=======

class BlogofileRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # If the site is configured to be hosted in a subdirectory
        # override the SimpleHTTPServer default translate_path method
        if len(urlparse(config.site_url).path.strip("/")) > 0:
            return self.do_subdir_translate(path)
        return SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(
            self, path)
    def do_subdir_translate(self, path):
        site_path = urlparse(config.site_url).path
        if(not path.startswith(site_path)):
            self.error_message_format = BLOGOFILE_SUBDIR_ERROR
            return "" #Results in a 404
        p = SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(
            self, path)
        build_path = os.path.join(
            os.getcwd(),
            util.path_join(site_path.strip("/")))
        p = re.sub(build_path, os.getcwd(), p)
        return p
>>>>>>> built-in webserver now correctly handles sites built inside subdirectories.:blogofile/server.py
