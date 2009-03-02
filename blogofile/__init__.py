#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is Blogofile -- http://www.Blogofile.com

Definition: Blogophile --
 A person who is fond of or obsessed with blogs or blogging.

Definition: Blogofile  --
 A static file blog engine/compiler, inspired by Jekyll.

Blogofile transforms a set of templates into an entire blog consisting of static
HTML files. All categories, tags, RSS/Atom feeds are automatically maintained by
Blogofile. This blog can be hosted on any HTTP web server. Since the blog is just
HTML, CSS, and Javascript, no CGI environment, or database is required. With the
addition of a of third-party comment and trackback provider (like Disqus or
IntenseDebate) a modern and interactive blog can be hosted very inexpensively.

Please take a moment to read LICENSE.txt. It's short.
"""

__author__  = "Ryan McGuire (ryan@enigmacurry.com)"
__date__    = "Tue Feb  3 12:52:52 2009"
__version__ = "0.1"

import ConfigParser
import os
import sys

import post
from writer import Writer

def parse_config(config_file_path):
    return config

def main():
    from optparse import OptionParser
    parser = OptionParser(version="Blogofile "+__version__+" -- http://www.blogofile.com")
    parser.add_option("-c","--config-file",dest="config_file",
                      help="The config file to load (default './_config.cfg')",
                      metavar="FILE", default="./_config.cfg")
    parser.add_option("-b","--build",dest="do_build",
                      help="Build the blog again from source",
                      default=False, action="store_true")
    (options, args) = parser.parse_args()
    
    #load config
    config = ConfigParser.ConfigParser()
    config.read(options.config_file)
    config_dir = os.path.split(os.path.abspath(options.config_file))[0]
    os.chdir(config_dir)

    if not options.do_build:
        parser.print_help()
        sys.exit(1)

    posts = post.parse_posts("_posts", timezone=config.get("blogofile","timezone"))
    writer = Writer(output_dir=os.path.join(config_dir,"_site"), config=config)
    writer.write_blog(posts)
    
if __name__ == '__main__':
    main()
