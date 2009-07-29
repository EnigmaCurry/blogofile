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
Blogofile. This blog can be hosted on any HTTP web server. Since the blog is
just HTML, CSS, and Javascript, no CGI environment, or database is required.
With the addition of a of third-party comment and trackback provider (like
Disqus or IntenseDebate) a modern and interactive blog can be hosted very
inexpensively.

Please take a moment to read LICENSE.txt. It's short.
"""

__author__  = "Ryan McGuire (ryan@enigmacurry.com)"
from blogofile import __version__ 

import logging
logging.basicConfig()
logger = logging.getLogger('main')

import ConfigParser
import os
import sys
import pygments.formatters
import pygments.styles

import post
from writer import Writer
        
def parse_config(config_file_path):
    return config

def main():
    from optparse import OptionParser
    parser = OptionParser(version="Blogofile "+__version__+
                          " -- http://www.blogofile.com")
    parser.add_option("-c","--config-file",dest="config_file",
                      help="The config file to load (default './_config.cfg')",
                      metavar="FILE", default="./_config.cfg")
    parser.add_option("-b","--build",dest="do_build",
                      help="Build the blog again from source",
                      default=False, action="store_true")
    parser.add_option("--init",dest="do_init",
                      help="Create a minimal blogofile configuration in the "\
                      "current directory",
                      default=False, action="store_true")
    parser.add_option("--include-drafts",dest="include_drafts",
                      default=False, action="store_true",
                      help="Writes permapages for drafts "
                      "(but not in feeds or chronlogical blog)")
    parser.add_option("--debug",dest="debug",default=False,
                      action="store_true",
                      help="Enable extra debugging in log")
    (options, args) = parser.parse_args()

    if options.debug:
        logger.setLevel(logging.DEBUG)
        logger.info("Setting DEBUG mode")

    options.config_dir = os.path.split(os.path.abspath(options.config_file))[0]
    if not os.path.isdir(options.config_dir):
        print("config dir does not exist : {0}".format(options.config_dir))
        sys.exit(1)
    os.chdir(options.config_dir)
    
    if options.do_build:
        do_build(options)
    elif options.do_init:
        do_init(options)
    else:
        parser.print_help()
        sys.exit(1)

def do_build(options):
    #load config
    config = ConfigParser.ConfigParser()
    if os.path.isfile(options.config_file):
        config.read(options.config_file)
    else:
        print("No configuration found at : {0} ".format(options.config_file))
        print("If you want to make a new site, try --init")
        return

    try:
        config.html_formatter = pygments.formatters.HtmlFormatter(
            style=config.get('syntax-highlighting','style'))
    except ConfigParser.NoSectionError:
        pass
                   
    posts = post.parse_posts("_posts", config)
    if options.include_drafts:
        drafts = post.parse_posts("_drafts", config)
        for p in drafts:
            p.draft = True
    else:
        drafts = None
    writer = Writer(output_dir=os.path.join(config_dir,"_site"), config=config)
    writer.write_blog(posts, drafts)

def do_init(options):
    if len(os.listdir(options.config_dir)) > 0 :
        print("This directory is not empty, will not attempt to initialize here : {0}".format(options.config_dir))
        return
    print("Building a minimal blogofile site at : {0}".format(options.config_dir))
    os.mkdir("_posts")
    print("This is a stub, this isn't complete yet.")
    
if __name__ == '__main__':
    main()
