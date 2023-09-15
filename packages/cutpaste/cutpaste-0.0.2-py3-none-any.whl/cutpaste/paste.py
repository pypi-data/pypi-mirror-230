#!/usr/bin/env python3

import os
import sys
import argparse

from cutpaste import utils
from cutpaste.version import version


def main():
    args = utils.parse_args('pypaste')
    print(args)


if __name__ == '__main__':
    main()
