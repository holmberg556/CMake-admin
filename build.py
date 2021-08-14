#!/usr/bin/env python3
#----------------------------------------------------------------------
# build.py
#----------------------------------------------------------------------

import argparse
import os
import sys

from pathlib import Path
from subprocess import run

WINDOWS = (sys.platform == 'win32')

def parse_arguments():
    parser = argparse.ArgumentParser('build.py')
    add = parser.add_argument

    add('-q', '--quiet', action='store_true', help='be more quiet')
    add('-n', '--dry-run', action='store_true', help='dry run')
    add('--ssh', action='store_true', help='use ssh')
    add('branch', help='branch to build')
    return parser.parse_args()

#----------------------------------------------------------------------

def main(opts):
    def sh(cmdline):
        if opts.dry_run:
            print(cmdline)
        else:
            print('###', cmdline)
            run(cmdline, shell=True, check=True)

    if opts.ssh:
        url = 'git@github.com:holmberg556/CMake.git'
    else:
        url = 'https://github.com/holmberg556/CMake.git'

    srcdir = Path.cwd().parent.joinpath('CMake')

    sh(f'git clone -b {opts.branch} {url} {srcdir}')
    if WINDOWS:
        sh(f'cmake -DCPACK_BINARY_NSIS:BOOL=FALSE -DCPACK_BINARY_ZIP:BOOL=TRUE -DCMAKE_INSTALL_PREFIX={srcdir}.install -B {srcdir}.build {srcdir}')
    else:
        sh(f'cmake -GNinja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX={srcdir}.install -B {srcdir}.build {srcdir}')

    if WINDOWS:
        sh(f'cmake --build {srcdir}.build --target install --config Release')
        sh(f'cmake --build {srcdir}.build --target package --config Release')
    else:
        sh(f'cmake --build {srcdir}.build --target install')
        sh(f'cmake --build {srcdir}.build --target package')

if __name__ == '__main__':
    exit(main(parse_arguments()))
