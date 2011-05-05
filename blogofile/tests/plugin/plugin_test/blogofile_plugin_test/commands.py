import shutil
import sys
import os, os.path
import imp

import blogofile.main
from blogofile import argparse

## These are commands that are installed into the blogofile
## command-line utility. You can turn these off entirely by removing
## the command_parser_setup parameter in the module __dist__ object.

def setup(parent_parser, parser_template):
    from . import __dist__
    #Add additional subcommands under the main parser:
    cmd_subparsers = parent_parser.add_subparsers()

    #command1
    command1 = cmd_subparsers.add_parser(
        "command1", help="Example Command 1", parents=[parser_template])
    command1.add_argument("--extra-coolness",action="store_true",
                          help="Run with extra coolness")
    command1.set_defaults(func=do_command1)

    #command2
    command2 = cmd_subparsers.add_parser(
        "command2", help="Example Command 2", parents=[parser_template])
    command2.add_argument("ARG1",help="Required ARG1")
    command2.add_argument("ARG2",help="Optional ARG2",
                          nargs="?",default="Default")
    command2.set_defaults(func=do_command2)

    
#These are the actual command actions:
    
def do_command1(args):
    print("")
    print("This is command1.")
    if args.extra_coolness:
        print("It's as cool as can be.")
    else:
        print("It could be cooler though with --extra-coolness")
        
def do_command2(args):
    print("")
    print("This is command2.")
    print("Required ARG1 = {0}".format(args.ARG1))
    print("Optional ARG2 = {0}".format(args.ARG2))
