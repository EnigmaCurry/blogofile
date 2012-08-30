# -*- coding: utf-8 -*-
from __future__ import print_function
import logging
import os
import sys
import threading
try:
    from urllib.parse import urlparse   # For Python 2
except ImportError:
    from urlparse import urlparse       # For Python 3; flake8 ignore # NOQA
from six.moves import SimpleHTTPServer
from six.moves import socketserver
from blogofile import config
from blogofile import util
from .cache import bf

bf.server = sys.modules['blogofile.server']

logger = logging.getLogger("blogofile.server")


class Server(threading.Thread):
    def __init__(self, port, address="127.0.0.1"):
        self.port = int(port)
        self.address = address
        if self.address == "0.0.0.0":
            # Bind to all addresses available
            address = ""
        threading.Thread.__init__(self)
        self.is_shutdown = False
        server_address = (address, self.port)
        HandlerClass = BlogofileRequestHandler
        HandlerClass.protocol_version = "HTTP/1.0"
        ServerClass = socketserver.TCPServer
        self.httpd = ServerClass(server_address, HandlerClass)
        self.sa = self.httpd.socket.getsockname()

    def run(self):
        print("Blogofile server started on {0}:{1} ..."
              .format(self.sa[0], self.sa[1]))
        self.httpd.serve_forever()

    def shutdown(self):
        print("\nshutting down webserver...")
        self.httpd.shutdown()
        self.httpd.socket.close()
        self.is_shutdown = True


class BlogofileRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    error_template = """
<head>
<title>Error response</title>
</head>
<body>
<h1>404 Error</h1>
Your Blogofile site is configured for a subdirectory, maybe you were looking
for the root page? : <a href="{0}">{1}</a>
</body>"""

    def __init__(self, *args, **kwargs):
        path = urlparse(config.site.url).path
        self.BLOGOFILE_SUBDIR_ERROR = self.error_template.format(path, path)
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(
            self, *args, **kwargs)

    def translate_path(self, path):
        site_path = urlparse(config.site.url).path
        if(len(site_path.strip("/")) > 0 and
                not path.startswith(site_path)):
            self.error_message_format = self.BLOGOFILE_SUBDIR_ERROR
            # Results in a 404
            return ""
        p = SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(
            self, path)
        if len(site_path.strip("/")) > 0:
            build_path = os.path.join(
                os.getcwd(),
                util.path_join(site_path.strip("/")))
        else:
            build_path = os.getcwd()
        build_path = p.replace(build_path, os.path.join(os.getcwd(), "_site"))
        return build_path

    def log_message(self, format, *args):
        pass
