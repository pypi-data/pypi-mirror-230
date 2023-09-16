#! /usr/bin/env python3

'''
ARGPARSE Enhancement

USAGE:
      argparse_enh.py

'''

import argparse
import json
from functools import wraps

import argparse_enh.argparse_dumper as apd


def __getOptActions__(parser):
    'Returns a dict - mapping option strings to actions of given parser/sub_parser'

    if parser is None:
        return {}

    optActions = {}
    for action in parser.__dict__['_actions']:
        for opt in action.option_strings:
            optActions[opt.strip('-')] = action

    return optActions


def __getArgs__(k, v, action):
    'Returns a list of arguments from the given key-value-pair from kwargs'

    # We access argparse actions
    # pylint: disable=protected-access

    args = []

    # If value is None, option is assumed as not given
    if v is None:
        return args

    # Add the option
    args.append(f'{"--" if len(k) > 1 else "-"}{k}')

    if isinstance(action, argparse._HelpAction):
        # Nothing to do for help action, irrespective of value add help option to list
        pass

    elif isinstance(action, argparse._StoreAction):
        if action.nargs in ('+', '*'):
            args.extend(v)
        else:
            args.append(str(v))

    elif isinstance(action, argparse._ExtendAction):
        args.extend(map(str, v))

    elif isinstance(action, argparse._StoreTrueAction):
        if not v:
            args.pop()

    elif isinstance(action, argparse._StoreFalseAction):
        if v:
            args.pop()

    else:
        assert False, f'{isinstance(action)} is not handled here'

    return args


def __showJson__(data):
    'Prints the given data struct in JSON format'

    print(json.dumps(data, indent=4, default=str))


def getSubParser(parser, name):
    '''
    Returns the subparser with given name if one exists - looks only one level deep
    Returns None, if the subparser with given name does not exist
    '''

    if '_subparsers' not in parser.__dict__:
        return None

    if parser.__dict__['_subparsers'] is None:
        return None

    assert name in parser.__dict__['_subparsers'].__dict__['_group_actions'][0].choices, f'''
        The {name} missing in subParser's actions
    '''

    return parser.__dict__['_subparsers'].__dict__['_group_actions'][0].choices[name]


def prepareArgs(parser, functionName, **kwargs):
    'Returns a list of arguments to pass to argparse from the given kwargs'

    args = []
    subParserArgs = []

    # Gather opt action pairs
    optActions = __getOptActions__(parser)
    subParserOptActions = __getOptActions__(getSubParser(parser, functionName))

    _seen = False
    for k, v in kwargs.items():
        # When an _ is seen, consider all subsequent options to be subcommand options
        # Add the subcommand also to command
        if k == '_':
            _seen = True
            continue

        # Give preference to optActions (main program options) until an _ is seen
        if not _seen and k in optActions:
            args.extend(__getArgs__(k, v, optActions[k]))

        # If the given option is not in main program options, look in subcommand options
        elif k in subParserOptActions:
            subParserArgs.extend(__getArgs__(k, v, subParserOptActions[k]))

        else:
            assert False, f'unknown kwarg {k}'

    if len(subParserOptActions):
        return args + [functionName] + subParserArgs

    return args


def api(parser):
    '''Make the function being decorated an API'''

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) == 0:
                args = (parser.parse_args(prepareArgs(parser, func.__name__, **kwargs)),)
            return func(*args, **kwargs)
        return wrapper
    return decorate


def dumpArgs(parser):
    'Dump the script to pass the args for the calling Shell script'

    apDumper = apd.ArgparseDumper(parser)
    apDumper.parseArgs()
    # Do not explicitly call `apDumper.__dumpArgs__()` as it is registered with atexit already


if __name__ == '__main__':
    assert False, 'Meant for importing only'
