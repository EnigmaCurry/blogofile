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

import os
import sys
import shlex

import pygments.formatters
import pygments.styles

import post
from writer import Writer
import config
import skeleton_init

def get_options(cmd=None):
    from optparse import OptionParser
    parser = OptionParser(version="Blogofile "+__version__+
                          " -- http://www.blogofile.com")
    parser.add_option("-c","--config-file",dest="config_file",
                      help="The config file to load (default './_config.py')",
                      metavar="FILE", default="./_config.py")
    parser.add_option("-b","--build",dest="do_build",
                      help="Build the blog again from source",
                      default=False, action="store_true")
    parser.add_option("--init",dest="do_init",
                      help="Create a minimal blogofile configuration in the "\
                      "current directory",
                      default=False, action="store_true")
    parser.add_option("--serve",dest="do_serve",
                      help="Host the _site dir with the builtin webserver. Don't"\
                          "use this outside of a firewall!",
                      metavar="PORT")
    parser.add_option("--include-drafts",dest="include_drafts",
                      default=False, action="store_true",
                      help="Writes permapages for drafts "
                      "(but not in feeds or chronlogical blog)")
    parser.add_option("-v","--verbose",dest="verbose",default=False,
                      action="store_true",
                      help="Enable extra verboseness")
    if not cmd:
        (options, args) = parser.parse_args()
    else:
        args = shlex.split(cmd)
        (options, args) = parser.parse_args(args)
    return (parser, options, args)

def main(cmd=None):
    (parser, options, args) = get_options(cmd)
    
    if options.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info("Setting DEBUG mode")

    options.config_dir = os.path.split(os.path.abspath(options.config_file))[0]
    if not os.path.isdir(options.config_dir):
        print("config dir does not exist : %s" % options.config_dir)
        sys.exit(1)
    os.chdir(options.config_dir)
    
    if options.do_build:
        do_build(options)
    elif options.do_init:
        do_init(options)
    elif options.do_serve:
        do_serve(options)
    else:
        parser.print_help()
        sys.exit(1)

def do_serve(options):
    os.chdir("_site")
    import SimpleHTTPServer
    sys.argv = [None, options.do_serve]
    SimpleHTTPServer.test()

def do_build(options):
    #load config
    try:
        config.init(options.config_file)
    except config.ConfigNotFoundException:
        print("No configuration found at : %s" % options.config_file)
        print("If you want to make a new site, try --init")
        return

    logger.info("Running user's pre_build() function..")
    config.pre_build()
    posts = post.parse_posts("_posts")
    if options.include_drafts:
        drafts = post.parse_posts("_drafts", config)
        for p in drafts:
            p.draft = True
    else:
        drafts = None
    writer = Writer(output_dir="_site")
    writer.write_blog(posts, drafts)
    logger.info("Running user's post_build() function..")
    config.post_build()

def do_init(options):
    skeleton_init.do_init(options)

if __name__ == '__main__':
    main()
