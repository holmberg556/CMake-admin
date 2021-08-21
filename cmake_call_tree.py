#!/usr/bin/env python3
#----------------------------------------------------------------------
# cmake_call_tree.py
#----------------------------------------------------------------------
#
# Process "cmake.trace.json", to produce a "tree view".
# Either an image via dot(1) or as an indented text output.
#
#----------------------------------------------------------------------

import argparse
import json
import os
import re
import sys

from subprocess import run

import networkx as nx
from networkx.drawing.nx_pydot import write_dot, to_pydot

def parse_arguments():
    parser = argparse.ArgumentParser('cmake_trace.py')
    add = parser.add_argument

    add('-v', '--verbose', action='store_true',
        help='more verbose output')

    add('--rankdir', action='store', default='LR', choices=('LR', 'TD'),
        help='dot parameter')
    add('--portrait', action='store_true',
        help='dot orientation')

    add('--avoid-subdir', action='append', default=[],
        help='avoid subdir(s)')

    add('-s', '--select', action='append', default=[],
        help='selected functions/macros')
    add('builddir', nargs='?', default='.',
        help='builddir with cmake.* files')

    return parser.parse_args()

#----------------------------------------------------------------------

def calls(trace):
    def is_fun(f):
        return f[0] == 'function' or f[0] == 'macro'
    def is_subdir(f):
        return f[0] == 'add_subdirectory'

    stack = [ ('add_subdirectory', 'TOP') ]
    for direction, typ, name in trace:
        frame = (typ,name)
        if direction == 'enter':
            stack.append(frame)
            if len(stack) >= 2:
                f1, f2 = stack[-2:]
                if (is_fun(f1) or is_subdir(f1)) and is_fun(f2):
                    yield f1, f2
        elif direction == 'leave':
            frame1 = stack.pop()
            assert frame1 == frame
        else:
            assert false

#----------------------------------------------------------------------

def quotient_graph(g):
    def kind(s):
        if ';add_subdirectory' in s:
            return 'subdir'
        elif ';function' in s:
            return 'function'
        else:
            return 'macro'
    def equiv(s1, s2):
        return ( kind(s1) == kind(s2) and
                 sorted(g.predecessors(s1)) == sorted(g.predecessors(s2)) and
                 sorted(g.successors(s1)) == sorted(g.successors(s2)) )

    def quotient_shape(x):
        x = list(x)
        return g.nodes[x[0]]['shape']

    group_g = nx.quotient_graph(g, equiv, edge_data=lambda x,y: {}, node_data=lambda x: { 'shape' : quotient_shape(x) })

    g2 = nx.relabel_nodes(group_g, lambda x: '\n'.join(re.sub(r';.*', '', y) for y in sorted(x)))
    return g2

#----------------------------------------------------------------------

def get_trace(opts):
    builddir = opts.builddir
    trace_file = f'{builddir}/cmake.trace.json'
    with open(trace_file) as f:
        trace = json.load(f)
    return [tuple(x) for x in trace]
    
#----------------------------------------------------------------------
# Functions & macros part of CMake itself ==> uninteresting.
#

def avoid_fun_byname(name):
    if name.upper() == name:
        return True

    prefixes = ['*', '_GNU', '_qt5', 'cmake_', '_has_compiler', '_check_function', '__', '_cmake', 'compiler_id_detection']

    if any(name.startswith(x) for x in prefixes):
        return True

    return False

#----------------------------------------------------------------------

def main(opts):
    trace = get_trace(opts)
    
    def avoid(f):
        if f[0] == 'add_subdirectory':
            return any((x in f[1]) for x in opts.avoid_subdir)
        else:
            return avoid_fun_byname(f[1])
    def show(f):
        if f[0] == 'add_subdirectory':
            return  ';'.join((label(f), f[0]))
        else:
            return f'{f[1]};{f[0]}'
    def shape(f):
        d = { 'function': 'ellipse', 'macro': 'octagon', 'add_subdirectory': 'folder' }
        return d[f[0]]
    def label(f):
        if f[0] == 'add_subdirectory':
            return os.path.relpath(f[1])
        else:
            return f[1]

    g = nx.DiGraph()

    seen = set()
    selected = set(y for x in opts.select for y in x.split(','))

    for call in calls(trace):
        f1, f2 = call
        if call in seen:
            continue
        seen.add(call)
        if avoid(f1) or avoid(f2):
            continue
        if f1[1] in selected or f2[1] in selected or len(selected) == 0:
            s1, s2 = show(f1), show(f2)
            if opts.verbose:
                print(f'{s1}\t{s2}')
            g.add_node(s1, shape=shape(f1), label=label(f1))
            g.add_node(s2, shape=shape(f2), label=label(f2))
            g.add_edge(s1, s2)

    g = quotient_graph(g)

    g.graph['graph'] = {
        'rankdir' : opts.rankdir,
        'size' : "11,15.8" if opts.portrait else "15.8,11",
        'ratio' : 'fill',
    }
    write_dot(g, 'tmp.dot')
    run('dot -Tpdf tmp.dot -o tmp.pdf', shell=True, check=True)
    
#----------------------------------------------------------------------

if __name__ == '__main__':
    exit(main(parse_arguments()))
