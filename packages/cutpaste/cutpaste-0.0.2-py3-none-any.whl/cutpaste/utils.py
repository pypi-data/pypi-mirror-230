import os
import sys
import argparse

from cutpaste.version import version


def parse_args(prog):
    p = get_parser(prog)
    args = p.parse_args()
    return args


def get_parser(prog):
    p = get_common_parser(prog)
    if prog == 'pycut':
        p.add_argument('-f', '--field', required=True, help='fields to select')
    return p

def get_common_parser(prog):
    p = argparse.ArgumentParser(prog)
    p.add_argument('-v', '-V', '--version', action='version', version='%(prog)s ' + version)
    p.add_argument('-d', '--delimiter', default='\t', help='string delimiter to use. default: TAB')
    p.add_argument('files', default=['-'], nargs='*', help='input files; defaults to - (stdin)')
    return p
