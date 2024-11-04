#!/usr/bin/env python3
#----------------------------------------------------------------------
# cmake_json_trace.py
#----------------------------------------------------------------------
# Use the "cmake --trace --trace-format=json-v1" output
# to present the "call tree" of a CMake run.
#
# It should be able to replace the patched CMake binary
# available from https://github.com/holmberg556/CMake-admin .
#
#----------------------------------------------------------------------

import argparse
import os
import sys

import json
import subprocess

#----------------------------------------------------------------------

DESCRIPTION = '''
Uses the JSON trace output from CMake, to display a call tree of
add_subdirectory / include / function calls in a CMake invocation.
Example use:

    # specify existing build tree
    cmake_json_trace.py build_dir

    # give a JSON trace file from earlier run of CMake
    cmake --trace --trace-format=json-v1 build_dir 2> cmake.json.trace
    cmake_json_trace.py cmake.json.trace

'''

def parse_arguments():
    parser = argparse.ArgumentParser('cmake_json_trace.py',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=DESCRIPTION)
    add = parser.add_argument

    add('-q', '--quiet', action='store_true',
        help='be more quiet')
    add('--builtin-function', action='append',
        help='builtin functions & macros to trace')
    add('--functions', action='store_true',
        help='log functions & macros')
    add('--files', action='store_true',
        help='log add_subdirectory & include')
    add('--args', action='store_true',
        help='log arguments too')
    add('-n', '--dry-run', action='store_true',
        help='do not perform actual task')
    add('dir_or_trace', action='store',
        help='build directory or trace JSON file')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()

#----------------------------------------------------------------------

def parse_builtin_function(arg):
    if arg is None:
        return []
    else:
        return [ f
                 for x in arg
                 for f in x.split(',') ]

#----------------------------------------------------------------------

def main(opts):
    if os.path.isfile(opts.dir_or_trace):
        with open(opts.dir_or_trace) as f:
            trace_lines = list(f)
    elif os.path.isdir(opts.dir_or_trace):
        build_dir = opts.dir_or_trace
        cmd = ('cmake', '--trace-expand', '--trace-format=json-v1', build_dir)
        r = subprocess.run(cmd, check=True, capture_output=True)
        trace_lines = r.stderr.decode().splitlines()
    else:
        print('ERROR: unknown argument', opts.dir_or_trace)
        exit(1)

    if not opts.functions and not opts.files:
        opts.functions = True
        opts.files = True

    macros = set()
    functions = set()

    opts.builtin_function = parse_builtin_function(opts.builtin_function)

    latest = None
    for line in trace_lines[1:]:
        line = line.rstrip('\n')
        data = json.loads(line)

        frame = data['frame']
        gframe = data['global_frame']
        path = data['file']
        cmd = data['cmd']

        if cmd == 'macro':
            macros.add(data['args'][0])
            continue

        if cmd == 'function':
            macros.add(data['args'][0])
            continue

        if cmd == 'include' or cmd == 'add_subdirectory':
            if opts.files:
                print('    ' * (gframe-1) + cmd + " " + repr(data['args']))

        if cmd in macros or cmd in functions or cmd in opts.builtin_function:
            if opts.functions:
                if opts.args:
                    print('    ' * (gframe-1) + cmd + " " + repr(data['args']))
                else:
                    print('    ' * (gframe-1) + cmd)

if __name__ == '__main__':
    exit(main(parse_arguments()))
