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
import time

import argparse

from cache import bf
from writer import Writer
import config
import site_init
import util

logging.basicConfig()
logger = logging.getLogger("blogofile")
bf.logger = logger


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
    parser.version = "Blogofile {0} -- http://www.blogofile.com".format(
            __version__)
    subparsers = parser.add_subparsers()

    p_help = subparsers.add_parser("help", help="Show help for a command.",
                                   add_help=False, parents=[parser_template])
    p_help.add_argument("command", help="a Blogofile subcommand e.g. build",
                        nargs="*", default="none")
    p_help.set_defaults(func=do_help)

    p_build = subparsers.add_parser("build", help="Build the site from source.",
                                    parents=[parser_template])
    p_build.set_defaults(func=do_build)

    p_init = subparsers.add_parser("init", help="Create a new Blogofile site from "
                                   "an existing template.",
                                   parents=[parser_template])
    p_init.add_argument("SITE_TEMPLATE", nargs="?",
                        help="The site template to initialize")
    p_init.set_defaults(func=do_init)
    p_init.extra_help = site_init.do_help

    p_serve = subparsers.add_parser("serve", help="Host the _site dir with "
                                    "the builtin webserver. Useful for quickly testing "
                                    "your site. Not for production use, please use "
                                    "Apache instead ;)",
                                    parents=[parser_template])
    p_serve.add_argument("PORT", nargs="?", default="8080",
                         help="TCP port to use")
    p_serve.add_argument("IP_ADDR", nargs="?", default="127.0.0.1",
                         help="IP address to bind to. Defaults to loopback only "
                         "(127.0.0.1). 0.0.0.0 binds to all network interfaces, "
                         "please be careful!")
    p_serve.set_defaults(func=do_serve)

    p_info = subparsers.add_parser("info", help="Show information about the "
                                   "Blogofile installation and the current site.",
                                   parents=[parser_template])
    p_info.set_defaults(func=do_info)

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
    sys.path.insert(0, os.curdir)

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
            #TODO: consider switching to new-style print syntax?
            print >>sys.stderr, "{0} - {1}".format(
                    subcommand, helptext[subcommand])
            parser = subparsers.choices[subcommand]
            parser.print_help()
            print >>sys.stderr, "\n"
            #Perform any extra help tasks:
            if hasattr(parser, "extra_help"):
                parser.extra_help()

def config_init(args):
    try:
        # Always load the _config.py from the current directory.
        # We already changed to the directory specified with --src-dir
        config.init("_config.py")
    except config.ConfigNotFoundException: #pragma: no cover
        print >>sys.stderr, \
                "No configuration found in source dir: {0}".format(args.src_dir)
        parser.exit(1, "Want to make a new site? Try `blogofile init`\n")
 

def do_serve(args): #pragma: no cover
    config_init(args)
    import server
    bfserver = server.Server(args.PORT, args.IP_ADDR)
    bfserver.start()
    while not bfserver.is_shutdown:
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            bfserver.shutdown()

def do_build(args, load_config=True):
    if load_config:
        config_init(args)
    output_dir = util.path_join("_site", util.fs_site_path_helper())
    writer = Writer(output_dir=output_dir)
    logger.debug("Running user's pre_build() function...")
    config.pre_build()
    writer.write_site()
    logger.debug("Running user's post_build() function...")
    config.post_build()


def do_init(args):
    site_init.do_init(args)


def do_debug():
    """Run inside winpdb if the environment variable BLOGOFILE_DEBUG is set to
    anything other than 0"""
    try:
        if os.environ['BLOGOFILE_DEBUG'] != "0":
            print("Running in debug mode. Enter a password for Winpdb to use.")
            import rpdb2
            rpdb2.start_embedded_debugger_interactive_password()
    except KeyError:
        pass #Not running in debug mode

def do_info(args):
    """Print some information about the Blogofile installation and the current site"""
    print("This is Blogofile (version {0}) -- http://www.blogofile.com".\
        format(__version__))
    print("")
    ### Show _config.py paths
    print("Default config file: {0}".format(config.default_config_path()))
    print("(Override these default settings in your own _config.py, don't edit "
          "the file above.)")
    print("")
    if os.path.isfile("_config.py"):
        print("Found site _config.py: {0}".format(os.path.abspath("_config.py")))
    else:
        print("The specified directory has no _config.py")
    
    
if __name__ == "__main__":
    main()
