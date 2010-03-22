import SimpleHTTPServer
import BaseHTTPServer
import logging
import os
import re
from urlparse import urlparse

from blogofile import config, util

logger = logging.getLogger("blogofile.server")

class Server:
    def __init__(self, port):
        self.port = int(port)
    def start(self):
        #We're guaranteed to be in the blogofile root after main runs
        #So change to the _site dir that should be built directly beneath it:
        os.chdir("_site")
        server_address = ('',self.port)
        HandlerClass = BlogofileRequestHandler
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
        
BLOGOFILE_SUBDIR_ERROR = """\
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
