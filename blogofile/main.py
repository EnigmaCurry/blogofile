#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is Blogofile -- http://www.Blogofile.com

Definition: Blogophile --
 A person who is fond of or obsessed with blogs or blogging.

Definition: Blogofile  --
 A static file blog engine/compiler, inspired by Jekyll.

Blogofile transforms a set of templates into an entire blog consisting of
static HTML files. All categories, tags, RSS/Atom feeds are automatically
maintained by Blogofile. This blog can be hosted on any HTTP web server. Since
the blog is just HTML, CSS, and Javascript, no CGI environment, or database is
required.  With the addition of a of third-party comment and trackback provider
(like Disqus or IntenseDebate) a modern and interactive blog can be hosted very
inexpensively.

Please take a moment to read LICENSE.txt. It's short.
"""

__author__  = "Ryan McGuire (ryan@enigmacurry.com)"
from blogofile import __version__ 

import logging
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

logging.basicConfig()
logger = logging.getLogger("main")

def get_args(cmd=None):
    global parser, subparsers
    parser = argparse.ArgumentParser()
    parser.version = "Blogofile " + __version__ + " -- http://www.blogofile.com"
    subparsers = parser.add_subparsers()
    parser.add_argument("-c", "--config-file", dest="config_file",
                        help="config file to load (default './_config.py')",
                        metavar="FILE", default="./_config.py")
    parser.add_argument("-V", "--version", action="version")
    parser.add_argument("-v", "--verbose", dest="verbose", default=False,
                        action="store_true", help="Enable extra verboseness")

    p_help = subparsers.add_parser("help", help="Show help for a command",
                                   add_help=False)
    p_help.add_argument("command", help="a blogofile subcommand e.g. build",
                        nargs="*", default="none")
    p_help.set_defaults(func=do_help)

    p_build = subparsers.add_parser("build", help="Build the blog from source")
    p_build.add_argument("--include-drafts", dest="include_drafts",
                         default=False, action="store_true",
                         help="Writes permapages for drafts "
                         "(but not in feeds or chronlogical blog)")
    p_build.set_defaults(func=do_build)

    p_init = subparsers.add_parser("init", help="Create a minimal blogofile "
                                   "configuration in the current directory")
    p_init.set_defaults(func=do_init)

    p_serve = subparsers.add_parser("serve", help="Host the _site dir with "
                                    "the builtin webserver. Don't use this "
                                    "outside of a firewall!")
    p_serve.add_argument("PORT", help="port on which to serve")
    p_serve.set_defaults(func=do_serve)

    if not cmd:
        if len(sys.argv) <= 1:
            parser.print_help()
            parser.exit(1)
        args = parser.parse_args()
    else:
        args = shlex.split(cmd)
        args = parser.parse_args(args)
    return (parser, args)

def main(cmd=None):
    parser, args = get_args(cmd)

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info("Setting DEBUG mode")

    args.config_dir = os.path.split(os.path.abspath(args.config_file))[0]
    if not os.path.isdir(args.config_dir):
        print("config dir does not exist : %s" % args.config_dir)
        sys.exit(1)
    os.chdir(args.config_dir)

    args.func(args)

def do_help(args):
    if "commands" in args.command:
        args.command = sorted(subparsers.choices.keys())

    if "none" in args.command:
        parser.print_help()
    else:
        # Where did the subparser help text go? Let's get it back.
        # Certainly there is a better way to retrieve the helptext than this...
        helptext = {}
        for subcommand in args.command:
            for action in subparsers._choices_actions:
                if action.dest == subcommand:
                    helptext[subcommand] = action.help
                    break
            else:
                helptext[subcommand] = ""
        # Print help for each subcommand requested.
        for subcommand in args.command:
            print >>sys.stderr, "%s - %s" % (subcommand, helptext[subcommand])
            subparsers.choices[subcommand].print_help()
            print >>sys.stderr, "\n"

def do_serve(args):
    os.chdir("_site")
    import SimpleHTTPServer
    sys.argv = [None, args.PORT]
    SimpleHTTPServer.test()

def do_build(args):
    #load config
    try:
        config.init(args.config_file)
    except config.ConfigNotFoundException:
        print >>sys.stderr, ("No configuration found: %s" % args.config_file)
        parser.exit(1, "Want to make a new site? Try `blogofile init`\n")

    logger.info("Running user's pre_build() function..")
    writer = Writer(output_dir="_site")
    if config.blog_enabled == True:
        config.pre_build()
        posts = post.parse_posts("_posts")
        if args.include_drafts:
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

def do_init(args):
    skeleton_init.do_init(args)

if __name__ == "__main__":
    main()
