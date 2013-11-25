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


class WunderlistReader():
    def __init__(self, db_path):
        if not os.path.isfile(db_path):
            raise RuntimeError('Invalid Wunderlist database path: %s' % db_path)

    def groups():
        return []

    def tasks(group):
        return []

    def subtasks(task):
        return []


class Exporter(object):
    def __init__(self, wunderlist_reader):
        self.wunderlist_reader = wunderlist_reader
    
    def execute(self, args):
        raise NotImplementedError('Not implemented')

class CsvExporter(Exporter):
    def __init__(self, wunderlist_reader):
        super(CsvExporter, self).__init__(wunderlist_reader)
    
    def execute(self, args):
        print 'Execute CSV exporter'

class TwoDoExporter(Exporter):
    def __init__(self, wunderlist_reader):
        super(TwoDoExporter, self).__init__(wunderlist_reader)
    
    def execute(self, args):
        print 'Execute 2Do exporter'


def die(msg):
    print >> sys.stderr, '%s: %s' % (sys.argv[0], msg)
    sys.exit(1)

def parseArgs(exporters, default_exporter):
    from optparse import OptionParser,TitledHelpFormatter
    
    parser = OptionParser(description=DESCRIPTION, usage=USAGE, version=VERSION)

    parser.set_defaults(wunderlist_db_path=getWunderlistDbPath())
    parser.add_option('-w', '--wunderlist-db', dest='wunderlist_db_path',
                      metavar='DB_PATH', help='path to Wunderlist database')

    parser.set_defaults(exporter=default_exporter)
    parser.add_option('-e', '--exporter', type='choice', choices=exporters,
                      help='exporter to use (%s)' % (', '.join(exporters)))
    
    (options, args) = parser.parse_args()

    return options

def getWunderlistDbPath():
    from itertools import ifilter

    db_path = '/Library/Application Support/Wunderlist/WKmodel.sqlite'
    possible_paths = [
        os.getenv('HOME') + db_path,
        '%s/Library/Containers/com.wunderkinder.wunderlistdesktop/Data%s' % (os.getenv('HOME'), db_path)
    ]

    return next(ifilter(lambda path: os.path.isfile(path), possible_paths), None)

if __name__ == '__main__':
    exporters = { 'csv': CsvExporter, '2do': TwoDoExporter }
    args = parseArgs(exporters.keys(), 'csv')

    wunderlist_reader = WunderlistReader(args.wunderlist_db_path)
    exporter = exporters[args.exporter](wunderlist_reader)
    exporter.execute(args)
    del wunderlist_reader, exporter
