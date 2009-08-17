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

import argparse
import pygments.formatters
import pygments.styles

import post
from writer import Writer
import config
import skeleton_init

def get_options(cmd=None):
    parser = argparse.ArgumentParser()
    parser.version = "Blogofile " +__version__+ " -- http://www.blogofile.com"
    parser.add_argument("-c","--config-file",dest="config_file",
                        help="config file to load (default './_config.py')",
                        metavar="FILE", default="./_config.py")
    parser.add_argument("-V","--version",action="version")
    parser.add_argument("-v","--verbose",dest="verbose",default=False,
                        action="store_true", help="Enable extra verboseness")
    subparsers = parser.add_subparsers()

    parser_build = subparsers.add_parser('build',
                                         help="Build the blog from source")
    parser_build.add_argument("--include-drafts", dest="include_drafts",
                              default=False, action="store_true",
                              help="Writes permapages for drafts "
                              "(but not in feeds or chronlogical blog)")
    parser_build.set_defaults(func=do_build)

    parser_init = subparsers.add_parser('init',
                                        help="Create a minimal blogofile "
                                        "configuration in the current "
                                        "directory")
    parser_init.set_defaults(func=do_init)

    parser_serve = subparsers.add_parser("serve",
                                         help="Host the _site dir with the "
                                         "builtin webserver. Don't use this "
                                         "outside of a firewall!")
    parser_serve.add_argument("PORT", help="port on which to serve")
    parser_serve.set_defaults(func=do_serve)

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    if not cmd:
        args = parser.parse_args()
    else:
        args = shlex.split(cmd)
        (options, args) = parser.parse_args(args)
    return (parser, args)

def main(cmd=None):
    (parser, args) = get_options(cmd)
    options = args

    if options.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info("Setting DEBUG mode")

    options.config_dir = os.path.split(os.path.abspath(options.config_file))[0]
    if not os.path.isdir(options.config_dir):
        print("config dir does not exist : %s" % options.config_dir)
        sys.exit(1)
    os.chdir(options.config_dir)

    args.func(options)

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
        print("If you want to make a new site, try `blogofile init`")
        return

    logger.info("Running user's pre_build() function..")
    writer = Writer(output_dir="_site")
    if config.blog_enabled == True:
        config.pre_build()
        posts = post.parse_posts("_posts")
        if options.include_drafts:
            drafts = post.parse_posts("_drafts", config)
            for p in drafts:
                p.draft = True
        else:
            drafts = None
        writer.write_blog(posts, drafts)
    else:
        #Build the site without a blog
        writer.write_site()
    logger.info("Running user's post_build() function..")
    config.post_build()

def do_init(options):
    skeleton_init.do_init(options)

if __name__ == '__main__':
    main()
