#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011 Augusto Rocha Elesbão <aelesbao@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Export Wunderlist tasks to CSV or import them to other task managers.

import sys, os

DESCRIPTION = 'Export Wunderlist tasks to CSV or import them to other task managers'
USAGE = 'usage: %prog [options]'
VERSION = '%prog 0.1.0'

def die(msg):
    print >>sys.stderr, '%s: %s' % (sys.argv[0], msg)
    sys.exit(1)

def parseArgs():
    from optparse import OptionParser
    
    parser = OptionParser(description=DESCRIPTION, usage=USAGE, version=VERSION)
    parser.add_option('-w', '--wunderlistdb',
                      help='path to Wunderlist database')
    parser.add_option('-e', '--exporter', type='choice', choices=['csv', '2do'],
                      help='exporter to use')
    
    (options, args) = parser.parse_args()

    return options

def main():
    # import sqlite3
    # conn = sqlite3.connect('example.db')

    cmd = getCommand()
    
    dispatchers = filter(lambda item: item.match(cmd), DISPATCHERS)
    if len(dispatchers) != 1:
        die("Command to run was not recognized.")
        
    dispatcher = dispatchers.pop()
    dispatcher.execute(cmd, args)
    
    die("Cannot execute dispatcher command.")

if __name__ == '__main__':
    args = parseArgs()
