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

import post
from writer import Writer
import config
import site_init
import util

logging.basicConfig()
logger = logging.getLogger("blogofile")

def get_args(cmd=None):

    ##parser_template to base other parsers on
    parser_template = argparse.ArgumentParser(add_help=False)
    parser_template.add_argument("-s", "--src-dir", dest="src_dir",
                        help="Your site's source directory "
                                 "(default is current directory)",
                        metavar="DIR", default=os.curdir)
    parser_template.add_argument("--version", action="version")
    parser_template.add_argument("-v", "--verbose", dest="verbose",
                                 default=False, action="store_true",
                                 help="Be verbose")
    parser_template.add_argument("-vv", "--veryverbose", dest="veryverbose",
                                 default=False, action="store_true",
                                 help="Be extra verbose")

    global parser, subparsers
    parser = argparse.ArgumentParser(parents=[parser_template])
    parser.version = "Blogofile " + __version__ + " -- http://www.blogofile.com"
    subparsers = parser.add_subparsers()

    p_help = subparsers.add_parser("help", help="Show help for a command",
                                   add_help=False, parents=[parser_template])
    p_help.add_argument("command", help="a blogofile subcommand e.g. build",
                        nargs="*", default="none")
    p_help.set_defaults(func=do_help)

    p_build = subparsers.add_parser("build", help="Build the site from source",
                                    parents=[parser_template])
    p_build.set_defaults(func=do_build)

    p_init = subparsers.add_parser("init", help="Create a minimal blogofile "
                                   "configuration in the current directory",
                                   parents=[parser_template])
    p_init.add_argument("SITE_TEMPLATE", nargs="?",
                        help="The site template to initialize")
    p_init.set_defaults(func=do_init)
    p_init.extra_help = site_init.do_help

    p_serve = subparsers.add_parser("serve", help="Host the _site dir with "
                                    "the builtin webserver. This is for DEV "
                                    "work only, don't use this outside of a "
                                    "firewall!",
                                    parents=[parser_template])
    p_serve.add_argument("PORT", nargs="?", default="8080",
                         help="port on which to serve")
    p_serve.set_defaults(func=do_serve)

    if not cmd: #pragma: no cover
        if len(sys.argv) <= 1:
            parser.print_help()
            parser.exit(1)
        args = parser.parse_args()
    else:
        args = shlex.split(cmd)
        args = parser.parse_args(args)
    return (parser, args)

def main(cmd=None):
    do_debug()   
    parser, args = get_args(cmd)

    if args.verbose: #pragma: no cover
        logger.setLevel(logging.INFO)
        logger.info("Setting verbose mode")
    if args.veryverbose: #pragma: no cover
        logger.setLevel(logging.DEBUG)
        logger.info("Setting very verbose mode")

    if not os.path.isdir(args.src_dir): #pragma: no cover
        print("source dir does not exist : %s" % args.src_dir)
        sys.exit(1)
    os.chdir(args.src_dir)

    #The src_dir, which is now the current working directory,
    #should already be on the sys.path, but let's make this explicit:
    sys.path.insert(0,os.curdir)

    args.func(args)

def do_help(args): #pragma: no cover
    global parser
    if "commands" in args.command:
        args.command = sorted(subparsers.choices.keys())

    if "none" in args.command:
        parser.print_help()
        print("\nSee 'blogofile help COMMAND' for more information"
              " on a specific command.")
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
            parser = subparsers.choices[subcommand]
            parser.print_help()
            print >>sys.stderr, "\n"
            #Perform any extra help tasks:
            if hasattr(parser,"extra_help"):
                parser.extra_help()

def do_serve(args): #pragma: no cover
    import server
    bfserver = server.Server(args.PORT)
    bfserver.start()
    
def do_build(args, load_config=True):
    if load_config:
        try:
            # Always load the _config.py from the current directory.
            # We already changed to the directory specified with --src-dir
            config.init("_config.py")
        except config.ConfigNotFoundException: #pragma: no cover
            print >>sys.stderr, ("No configuration found in source dir: %s" % args.src_dir)
            parser.exit(1, "Want to make a new site? Try `blogofile init`\n")
    writer = Writer(output_dir=util.path_join("_site",util.fs_site_path_helper()))
    logger.debug("Running user's pre_build() function..")
    config.pre_build()
    writer.write_site()
    logger.debug("Running user's post_build() function..")
    config.post_build()

def do_init(args):
    site_init.do_init(args)

def do_debug():
    """Run inside winpdb if the environment variable BLOGOFILE_DEBUG is set to
    anything other than 0"""
    try:
        if os.environ['BLOGOFILE_DEBUG'] != "0":
            print("Running in debug mode. Enter a password for Winpdb to use.")
            import rpdb2; rpdb2.start_embedded_debugger_interactive_password()
    except KeyError:
        pass #Not running in debug mode
    
if __name__ == "__main__":
    main()
