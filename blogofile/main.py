# -*- coding: utf-8 -*-
"""This is Blogofile -- http://www.Blogofile.com

Please take a moment to read LICENSE.txt. It's short.
"""
from __future__ import print_function

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"

import argparse
import locale
import logging
import os
import sys
import time
import platform

from . import __version__
from . import server
from . import config
from . import util
from . import filter as _filter
from . import plugin
from . import site_init
from .cache import bf
from .exception import SourceDirectoryNotFound
from .writer import Writer


locale.setlocale(locale.LC_ALL, '')

logging.basicConfig()
logger = logging.getLogger("blogofile")
bf.logger = logger


def _build_parser_template():
    """Return the parser template that other parser are based on.
    """
    parser_template = argparse.ArgumentParser(add_help=False)
    parser_template.add_argument(
        "--version", action="version",
        version="Blogofile {0} -- http://www.blogofile.com -- {1} {2}"
        .format(__version__, platform.python_implementation(),
                platform.python_version()))
    parser_template.add_argument(
        "-s", "--src-dir", dest="src_dir", metavar="DIR",
        help="Your site's source directory (default is current directory)")
    parser_template.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true",
        help="Be verbose")
    parser_template.add_argument(
        "-vv", "--veryverbose", dest="veryverbose", action="store_true",
        help="Be extra verbose")
    defaults = {
        "src_dir": os.curdir,
        "verbose": False,
        "veryverbose": False,
    }
    parser_template.set_defaults(**defaults)
    return parser_template


def setup_command_parser():
    parser_template = _build_parser_template()
    parser = argparse.ArgumentParser(parents=[parser_template])
    subparsers = parser.add_subparsers()

    p_help = subparsers.add_parser("help", help="Show help for a command.",
                                   add_help=False)
    p_help.add_argument("command", help="a Blogofile subcommand e.g. build",
                        nargs="*", default="none")
    p_help.set_defaults(func=do_help)

    p_build = subparsers.add_parser(
        "build", help="Build the site from source.")
    p_build.set_defaults(func=do_build)

    p_init = subparsers.add_parser(
        "init", help="Create a new Blogofile site from an existing template.")
    p_init.set_defaults(func=do_init)
    p_init.extra_help = site_init.do_help
    init_parsers = p_init.add_subparsers()
    for site in site_init.available_sites:
        site_parser = init_parsers.add_parser(site[0], help=site[1])
        site_parser.set_defaults(func=do_init, SITE_TEMPLATE=site[0])

    p_serve = subparsers.add_parser(
        "serve",
        help="""
            Host the _site dir with the builtin webserver.
            Useful for quickly testing your site.
            Not for production use!
            """)
    p_serve.add_argument(
        "PORT", nargs="?", default="8080", help="TCP port to use")
    p_serve.add_argument(
        "IP_ADDR", nargs="?", default="127.0.0.1",
        help="""
            IP address to bind to. Defaults to loopback only
            (127.0.0.1). 0.0.0.0 binds to all network interfaces,
            please be careful!.
            """)
    p_serve.set_defaults(func=do_serve)

    p_info = subparsers.add_parser(
        "info",
        help="""
            Show information about the
            Blogofile installation and the current site.
            """)
    p_info.set_defaults(func=do_info)

    p_plugin = subparsers.add_parser("plugin", help="Plugin tools")
    p_plugin_subparsers = p_plugin.add_subparsers()
    p_plugin_list = p_plugin_subparsers.add_parser(
        "list", help="List all the plugins installed")
    p_plugin_list.set_defaults(func=plugin.list_plugins)

    for p in plugin.iter_plugins():
        try:
            plugin_parser_setup = p.__dist__['command_parser_setup']
        except KeyError:
            continue
        # Setup the plugin subcommand parser
        plugin_parser = subparsers.add_parser(
            p.__dist__['config_name'],
            help="Plugin: " + p.__dist__['description'])
        plugin_parser.version = (
            "{name} plugin {version} by {author} -- {url}"
            .format(**p.__dist__))
        plugin_parser_setup(plugin_parser, parser_template)

    p_filter = subparsers.add_parser("filter", help="Filter tools")
    p_filter_subparsers = p_filter.add_subparsers()
    p_filter_list = p_filter_subparsers.add_parser(
        "list", help="List all the filters installed")
    p_filter_list.set_defaults(func=_filter.list_filters)

    return parser, subparsers


def find_src_root(path=os.curdir):
    """Find the root src directory.

    peel away directories until we find a _config.py.

    Raises SourceDirectoryNotFound if we can't find one.
    """
    path = os.path.abspath(path)
    while True:
        if os.path.isfile(os.path.join(path, "_config.py")):
            return path
        parts = os.path.split(path)
        if len(parts[1]) == 0:
            raise SourceDirectoryNotFound
        path = parts[0]


def main():
    """Blogofile entry point.

    Set up command line parser, parse args, and dispatch to
    appropriate function. Print help and exit if there are too few args.
    """
    do_debug()
    parser, subparsers = setup_command_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit(2)
    else:
        args = parser.parse_args()
        set_verbosity(args)
        if args.func == do_help:
            do_help(args, parser, subparsers)
        else:
            args.func(args)


def set_verbosity(args):
    """Set verbosity level for logging as requested on command line.
    """
    if args.verbose:
        logger.setLevel(logging.INFO)
        logger.info("Setting verbose mode")
    if args.veryverbose:
        logger.setLevel(logging.DEBUG)
        logger.info("Setting very verbose mode")


def set_src_dir(args, parser):
    # Find the right source directory location:
    if args.func == do_init and not args.src_dir:
        args.src_dir = os.curdir
    elif not args.src_dir:
        try:
            args.src_dir = find_src_root()
        except SourceDirectoryNotFound:
            args.src_dir = os.path.abspath(os.curdir)
    if not args.src_dir or not os.path.isdir(args.src_dir):
        parser.exit(2, "source dir does not exit: {0.src_dir}\n".format(args))
    os.chdir(args.src_dir)
    # The src_dir, which is now the current working directory, should
    # already be on the sys.path, but let's make this explicit.
    sys.path.insert(0, os.curdir)


def do_help(args, parser, subparsers):
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
            sys.stderr.write("{0} - {1}\n"
                             .format(subcommand, helptext[subcommand]))
            parser = subparsers.choices[subcommand]
            parser.print_help()
            sys.stderr.write("\n")
            # Perform any extra help tasks:
            if hasattr(parser, "extra_help"):
                parser.extra_help()


def do_serve(args):
    config.init_interactive(args)
    bfserver = server.Server(args.PORT, args.IP_ADDR)
    bfserver.start()
    while not bfserver.is_shutdown:
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            bfserver.shutdown()


def do_build(args, load_config=True):
    if load_config:
        config.init_interactive(args)
    output_dir = util.path_join("_site", util.fs_site_path_helper())
    writer = Writer(output_dir=output_dir)
    logger.debug("Running user's pre_build() function...")
    config.pre_build()
    try:
        writer.write_site()
        logger.debug("Running user's post_build() function...")
        config.post_build()
    except:
        logger.error(
            "Fatal build error occured, calling bf.config.build_exception()")
        config.build_exception()
        raise
    finally:
        logger.debug("Running user's build_finally() function...")
        config.build_finally()


def do_init(args):
    site_init.do_init(args)


def do_debug():
    """Run blogofile in debug mode depending on the BLOGOFILE_DEBUG environment
    variable:
    If set to "ipython" just start up an embeddable ipython shell at bf.ipshell
    If set to anything else besides 0, setup winpdb environment
    """
    try:
        if os.environ['BLOGOFILE_DEBUG'] == "ipython":
            from IPython.Shell import IPShellEmbed
            bf.ipshell = IPShellEmbed()
        elif os.environ['BLOGOFILE_DEBUG'] != "0":
            print("Running in debug mode, waiting for debugger to connect. "
                  "Password is set to 'blogofile'")
            import rpdb2
            rpdb2.start_embedded_debugger("blogofile")
    except KeyError:
        # Not running in debug mode
        pass


def do_info(args):
    """Print some information about the Blogofile installation and the
    current site.
    """
    print("This is Blogofile (version {0}) -- http://www.blogofile.com"
          .format(__version__))
    print("You are using {0} {1} from {2}".format(
        platform.python_implementation(), platform.python_version(),
        sys.executable))
    print("Blogofile is installed at: {0}".format(os.path.split(__file__)[0]))
    # Show _config.py paths
    print(("Default config file: {0}".format(config.default_config_path())))
    if os.path.isfile("_config.py"):
        print("Found site _config.py: {0}"
              .format(os.path.abspath("_config.py")))
    else:
        print(
            "The specified directory has no _config.py, and cannot be built.")
