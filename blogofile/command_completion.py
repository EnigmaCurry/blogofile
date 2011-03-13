import sys
import shlex

from . import argparse

bash_bootstrap = """
_blogofile_completion() {
    local cur prev
    COMPREPLY=()
    cur=`_get_cword`
    prev=${COMP_WORDS[COMP_CWORD-1]}
    COMMAND=${COMP_WORDS[@]:1}
    COMPREPLY=( $( BLOGOFILE_COMPLETION_MODE=true blogofile $COMMAND 2>/dev/null) )
    return 0
} &&
complete -F _blogofile_completion blogofile
"""

def get_subparsers(parser):
    if parser._subparsers:
        subparsers = list(parser._subparsers._group_actions[0].choices.items())
    else:
        subparsers = []
    return subparsers
    
def get_positional_args(parser):
    args = parser._positionals._actions
    return args

def print_completions(parser, command, current_word):
    """Print all the possible completions of command
    given the current_word being completed.

    Returns the total number of completions possible"""
    #First turn off the default exit on error behaviour of argparse:
    argparse.EXIT_ON_ERROR = False
    num_completions = 0
    try:
        #Get the parser for the subcommand:
        subparser = parser.parse_args(command)._parser
        #Get all the subparser names:
        for name, sub_subparser in get_subparsers(subparser):
            if name.startswith(current_word):
                if name != current_word:
                    print(name + " ")
                    num_completions += 1
    finally:
        #Turn back on the default exit on error behaviour of argparse:
        argparse.EXIT_ON_ERROR = True
    return num_completions
        
def complete(parser, command):
    "Generate all the possible completions for a given command"
    if command is None:
        command = sys.argv[1:]
    else:
        command = shlex.split(command)
    if len(command) > 0:
        current_word = command[-1]
        cmd = command[:-1]
    else:
        current_word = ""
        cmd = command
    num_completions = print_completions(parser, cmd, current_word)
    if num_completions == 0:
        print_completions(parser, command, "")
