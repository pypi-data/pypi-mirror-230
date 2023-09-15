#! /usr/bin/env python3

'''
ARGPARSE Dumper
'''

import argparse
import atexit
import os
import sys

import psutil


class ArgparseDumper:
    'Class to abstract out the dumping of argparse args in shell scripts'

    def __init__(self, parser):
        self.args = None
        self.apdArgs = None
        self.parser = parser
        self.__stdOutBkp__ = sys.stdout
        atexit.register(self.__dumpArgs__)


    def __getApdParser__(self):
        'Return Argparse Enh Parser that handles the additional arguments of Argparse Dumper'

        parser = argparse.ArgumentParser(
            allow_abbrev=True,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            # Add custom help option so that it does not conflict with main parser
            add_help=False,
            description='Parser to parse options for Argparse Dumper'
        )

        parser.add_argument(
            '--apdPrefix', type=str, default='opt_', help='Prefix for the argparse dumper options'
        )

        parser.add_argument(
            '--apdUseEnvVars', action='store_true',
            help='Set opts as environment variables instead of shell variables'
        )

        parser.add_argument(
            '--apdDebug', action='store_true',
            help='Enable debug mode for argparse dumper'
        )

        parser.add_argument(
            '--apdHelp', action='help', help='Dump the help of argparse dumper options'
        )

        return parser


    def parseArgs(self):
        'Parse the args and return the args object'

        # When parsing args, use stderr for all output from argparse
        sys.stdout = sys.stderr
        self.apdArgs, remainingArgs = self.__getApdParser__().parse_known_args()
        self.args = self.parser.parse_args(remainingArgs)
        sys.stdout = self.__stdOutBkp__


    def __dumpArgs__(self):
        'Dump the script to pass the args for the calling Shell script'

        # Restore the stdout
        sys.stdout = self.__stdOutBkp__
        dbgId = "[APD_DEBUG] "
        if self.args is None:
            if self.apdArgs.apdDebug:
                print(
                    f'{dbgId}argparse exited before parsing, possibly due to help/version',
                    file=sys.stderr
                )
            print('exit 0')
            return

        shell = psutil.Process(os.getpid()).parent().name()

        if self.apdArgs.apdDebug:
            print(f'{dbgId}Detected Shell: {shell}', file=sys.stderr)

        code = []
        for k, v in vars(self.args).items():
            if v is None:
                continue

            # If the value is a filetype, close the file handle and retain just name of the file
            if k in ('rdFile', 'wrFile'):
                v.close()
                v = v.name

            if isinstance(v, list):
                v = f'({" ".join(v)})'

            if self.apdArgs.apdUseEnvVars:
                if shell == 'tcsh':
                    code.append(f'setenv {self.apdArgs.apdPrefix}{k} {v}')
                elif shell in ('sh', 'bash', 'zsh'):
                    code.append(f'export {self.apdArgs.apdPrefix}{k}={v}')
            else:
                if shell == 'tcsh':
                    code.append(f'set {self.apdArgs.apdPrefix}{k} = {v}')
                elif shell in ('sh', 'bash', 'zsh'):
                    code.append(f'{self.apdArgs.apdPrefix}{k}={v}')

        if len(code) > 0:
            if self.apdArgs.apdDebug:
                print("\n".join([dbgId + i for i in code]), file=sys.stderr)
            print("\n".join(code))


if __name__ == '__main__':
    assert False, 'Meant for importing only'
