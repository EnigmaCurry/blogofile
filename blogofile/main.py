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
import shutil
import sys
import time
import platform

from . import __version__
from . import server
from . import config
from . import util
from . import filter as _filter
from . import plugin
from .cache import bf
from .writer import Writer


locale.setlocale(locale.LC_ALL, '')

logging.basicConfig()
logger = logging.getLogger("blogofile")
bf.logger = logger


def main(argv=[]):
    """Blogofile entry point.

    Set up command line parser, parse args, and dispatch to
    appropriate function. Print help and exit if there are too few args.

    :arg argv: List of command line arguments. Non-empty list facilitates
               integration tests.
    :type argv: list
    """
    do_debug()
    argv = argv or sys.argv
    parser, subparsers = setup_command_parser()
    if len(argv) == 1:
        parser.print_help()
        parser.exit(2)
    else:
        args = parser.parse_args(argv[1:])
        set_verbosity(args)
        if args.func == do_help:
            do_help(args, parser, subparsers)
        else:
            args.func(args)


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


def setup_command_parser():
    """Set up the command line parser, and the parsers for the sub-commands.
    """
    parser_template = _setup_parser_template()
    parser = argparse.ArgumentParser(parents=[parser_template])
    subparsers = parser.add_subparsers(title='sub-commands')
    _setup_help_parser(subparsers)
    _setup_init_parser(subparsers)
    _setup_build_parser(subparsers)
    _setup_serve_parser(subparsers)
    _setup_info_parser(subparsers)
    _setup_plugins_parser(subparsers, parser_template)
    _setup_filters_parser(subparsers)
    return parser, subparsers


def _setup_parser_template():
    """Return the parser template that other parser are based on.
    """
    parser_template = argparse.ArgumentParser(add_help=False)
    parser_template.add_argument(
        "--version", action="version",
        version="Blogofile {0} -- http://www.blogofile.com -- {1} {2}"
        .format(__version__, platform.python_implementation(),
                platform.python_version()))
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


def _setup_help_parser(subparsers):
    """Set up the parser for the help sub-command.
    """
    parser = subparsers.add_parser(
        "help", add_help=False,
        help="Show help for a command.")
    parser.add_argument(
        "command", nargs="*",
        help="a Blogofile subcommand e.g. build")
    parser.set_defaults(func=do_help)
    defaults = {
        'command': None,
        'func': do_help,
    }
    parser.set_defaults(**defaults)


def _setup_init_parser(subparsers):
    """Set up the parser for the init sub-command.
    """
    parser = subparsers.add_parser(
        "init",
        help="Create a new blogofile site.")
    parser.add_argument(
        "src_dir",
        help="""
            Your site's source directory.
            It will be created if it doesn't exist, as will any necessary
            parent directories.
            """)
    parser.add_argument(
        "plugin", nargs="?",
        help="""
            Plugin to initialize site from.
            The plugin must already be installed;
            use `blogofile plugins list` to get the list of installed plugins.
            If omitted, a bare site directory will be created.
            """)
    defaults = {
        "plugin": None,
        "func": do_init,
    }
    parser.set_defaults(**defaults)


def _setup_build_parser(subparsers):
    """Set up the parser for the build sub-command.
    """
    parser = subparsers.add_parser(
        "build",
        help="Build the site from source.")
    parser.add_argument(
        "-s", "--src-dir", dest="src_dir", metavar="DIR",
        help="Your site's source directory (default is current directory)")
    defaults = {
        "src_dir": os.curdir,
        "func": do_build,
    }
    parser.set_defaults(**defaults)


def _setup_serve_parser(subparsers):
    """Set up the parser for the serve sub-command.
    """
    parser = subparsers.add_parser(
        "serve",
        help="""
            Host the _site dir with the builtin webserver.
            Useful for quickly testing your site.
            Not for production use!
            """)
    parser.add_argument(
        "PORT", nargs="?",
        help="TCP port to use; defaults to %(default)s")
    parser.add_argument(
        "IP_ADDR", nargs="?",
        help="""
            IP address to bind to. Defaults to loopback only
            (%(default)s). 0.0.0.0 binds to all network interfaces,
            please be careful!.
            """)
    parser.add_argument(
        "-s", "--src-dir", dest="src_dir", metavar="DIR",
        help="Your site's source directory (default is current directory)")
    defaults = {
        "PORT": "8080",
        "IP_ADDR": "127.0.0.1",
        "src_dir": os.curdir,
        "func": do_serve,
    }
    parser.set_defaults(**defaults)


def _setup_info_parser(subparsers):
    """Set up the parser for the info sub-command.
    """
    parser = subparsers.add_parser(
        "info",
        help="""
            Show information about the
            Blogofile installation and the current site.
            """)
    parser.add_argument(
        "-s", "--src-dir", dest="src_dir", metavar="DIR",
        help="Your site's source directory (default is current directory)")
    defaults = {
        "src_dir": os.curdir,
        "func": do_info,
    }
    parser.set_defaults(**defaults)


def _setup_plugins_parser(subparsers, parser_template):
    """Set up the parser for the plugins sub-command.
    """
    parser = subparsers.add_parser(
        "plugins",
        help="Plugin tools")
    plugin_subparsers = parser.add_subparsers()
    plugins_list = plugin_subparsers.add_parser(
        "list",
        help="List all of the plugins installed")
    plugins_list.set_defaults(func=plugin.list_plugins)
    for p in plugin.iter_plugins():
        # Setup the plugin command parser, if it has one
        try:
            plugin_parser_setup = p.__dist__['command_parser_setup']
        except KeyError:
            continue
        plugin_parser = subparsers.add_parser(
            p.__dist__['config_name'],
            help="Plugin: " + p.__dist__['description'])
        plugin_parser.add_argument(
            "--version", action="version",
            version="{name} plugin {version} by {author} -- {url}"
            .format(**p.__dist__))
        plugin_parser_setup(plugin_parser, parser_template)


def _setup_filters_parser(subparsers):
    """Set up the parser for the filters sub-command.
    """
    parser = subparsers.add_parser(
        "filters",
        help="Filter tools")
    filter_subparsers = parser.add_subparsers()
    filters_list = filter_subparsers.add_parser(
        "list",
        help="List all the filters installed")
    filters_list.set_defaults(func=_filter.list_filters)


def set_verbosity(args):
    """Set verbosity level for logging as requested on command line.
    """
    if args.verbose:
        logger.setLevel(logging.INFO)
        logger.info("Setting verbose mode")
    if args.veryverbose:
        logger.setLevel(logging.DEBUG)
        logger.info("Setting very verbose mode")


def do_help(args, parser, subparsers):
    if "commands" in args.command:
        args.command = sorted(subparsers.choices.keys())

    if not args.command:
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


def do_init(args):
    """Initialize a new blogofile site.
    """
    # Look before we leap because _init_plugin_site uses
    # shutil.copytree() which requires that the src_dir not already
    # exist
    if os.path.exists(args.src_dir):
        print(
            "{0.src_dir} already exists; initialization aborted"
            .format(args),
            file=sys.stderr)
        sys.exit(1)
    if args.plugin is None:
        _init_bare_site(args.src_dir)
    else:
        _init_plugin_site(args)


def _init_bare_site(src_dir):
    """Initialize the site directory as a bare (do-it-yourself) site.

    Write a minimal _config.py file and a message to the user.
    """
    bare_site_config = [
        "# -*- coding: utf-8 -*-\n",
        "# This is a minimal blogofile config file.\n",
        "# See the docs for config options\n",
        "# or run `blogofile help init` to learn how to initialize\n",
        "# a site from a plugin.\n",
    ]
    os.makedirs(src_dir)
    new_config_path = os.path.join(src_dir, '_config.py')
    with open(new_config_path, 'wt') as new_config:
        new_config.writelines(bare_site_config)
    print("_config.py for a bare (do-it-yourself) site "
          "written to {0}\n"
          "If you were expecting more, please see `blogofile init -h`"
          .format(src_dir))


def _init_plugin_site(args):
    """Initialize the site directory with the approprate files from an
    installed blogofile plugin.

    Copy everything except the _controllers, _filters, and _templates
    directories from the plugin's site_src directory.
    """
    p = plugin.get_by_name(args.plugin)
    if p is None:
        print("{0.plugin} plugin not installed; initialization aborted\n\n"
              "installed plugins:".format(args),
              file=sys.stderr)
        plugin.list_plugins(args)
        return
    plugin_path = os.path.dirname(os.path.realpath(p.__file__))
    site_src = os.path.join(plugin_path, 'site_src')
    ignore_dirs = shutil.ignore_patterns(
        '_controllers', '_filters')
    shutil.copytree(site_src, args.src_dir, ignore=ignore_dirs)
    print("{0.plugin} plugin site_src files written to {0.src_dir}"
          .format(args))


def do_build(args, load_config=True):
    _validate_src_dir(args.src_dir)
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


def _validate_src_dir(src_dir):
    """Confirm that `src_dir` exists, and contains a `_config.py` file.

    If so, make `src_dir` the working directory.
    """
    if not os.path.isdir(src_dir):
        print("source dir does not exist: {0}".format(src_dir))
        sys.exit(1)
    if not os.path.isfile(os.path.join(src_dir, "_config.py")):
        print("source dir does not contain a _config.py file")
        sys.exit(1)
    os.chdir(src_dir)


def do_serve(args):
    _validate_src_dir(args.src_dir)
    config.init_interactive(args)
    bfserver = server.Server(args.PORT, args.IP_ADDR)
    bfserver.start()
    while not bfserver.is_shutdown:
        try:
            time.sleep(0.5)
        except KeyboardInterrupt:
            bfserver.shutdown()


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
    print(("Default config file: {0}".format(config.default_config_path)))
    if os.path.isfile(os.path.join(args.src_dir, "_config.py")):
        print("Found site _config.py: {0}"
              .format(os.path.abspath("_config.py")))
    else:
        print(
            "The specified directory has no _config.py, and cannot be built.")
