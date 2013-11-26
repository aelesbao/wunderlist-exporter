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

import sys, os, sqlite3
import csv, codecs, cStringIO
import time
from datetime import datetime


DESCRIPTION = 'Export Wunderlist tasks to CSV or import them to other task managers'
USAGE = 'usage: %prog [options]'
VERSION = '%prog 0.1.0'


class WunderlistReader():
    __ENT_LIST = 8
    __ENT_TASK = 7

    def __init__(self, db_path):
        if not os.path.isfile(db_path):
            raise RuntimeError('Invalid Wunderlist database path: %s' % db_path)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = self.__dict_factory

    def __del__(self):
        self.conn.close()

    def tasklists(self):
        cursor = self.conn.execute('SELECT * FROM ZRESOURCE WHERE Z_ENT=? ORDER BY ZTITLE', (self.__ENT_LIST,))
        return cursor.fetchall()

    def tasks(self, tasklist):
        cursor = self.conn.execute('SELECT * FROM ZRESOURCE WHERE Z_ENT=? AND ZTASKLIST=? ORDER BY ZORDERINDEXDOUBLE', (self.__ENT_TASK, tasklist['Z_PK']))
        return cursor.fetchall()

    def subtasks(self, task):
        cursor = self.conn.execute('SELECT * FROM ZRESOURCE WHERE Z_ENT=? AND ZPARENTTASK=? ORDER BY ZORDERINDEXDOUBLE', (self.__ENT_TASK, task['Z_PK']))
        return cursor.fetchall()

    def __dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d


class Exporter(object):
    def __init__(self, reader):
        self.reader = reader
    
    def execute(self, args):
        raise NotImplementedError('Not implemented')

class CsvExporter(Exporter):
    class UTF8Recoder:
        """
        Iterator that reads an encoded stream and reencodes the input to UTF-8
        """
        def __init__(self, f, encoding):
            self.reader = codecs.getreader(encoding)(f)

        def __iter__(self):
            return self

        def next(self):
            return self.reader.next().encode("utf-8")

    class UnicodeWriter:
        """
        A CSV writer which will write rows to CSV file "f",
        which is encoded in the given encoding.
        """

        def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
            # Redirect output to a queue
            self.queue = cStringIO.StringIO()
            self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
            self.stream = f
            self.encoder = codecs.getincrementalencoder(encoding)()

        def writerow(self, row):
            self.writer.writerow([s.encode("utf-8") if isinstance(s, basestring) else s for s in row])
            # Fetch UTF-8 output from the queue ...
            data = self.queue.getvalue()
            data = data.decode("utf-8")
            # ... and reencode it into the target encoding
            data = self.encoder.encode(data)
            # write to the target stream
            self.stream.write(data)
            # empty queue
            self.queue.truncate(0)

        def writerows(self, rows):
            for row in rows:
                self.writerow(row)


    def __init__(self, reader):
        super(CsvExporter, self).__init__(reader)
    
    def execute(self, args):
        print 'Executing CSV exporter...'
        rows = self.__export_rows()
        self.__write_csv(args.filename, rows)
        print 'Tasks exported to %s' % args.filename

    def __export_rows(self):
        header = ['LIST_NAME', 'TASK_NAME', 'STARRED', 'DONE', 'CREATED_AT', 'COMPLETED_AT', 'DUE_DATE', 'NOTES', 'SUBTASK_TITLE']
        rows = [self.__export_task(tasklist, task) for tasklist in self.reader.tasklists() for task in self.reader.tasks(tasklist)]
        return [header] + reduce(lambda x, y: x + y, rows)

    def __export_task(self, tasklist, task):
        subtasks = self.reader.subtasks(task)
        return [self.__format_row(tasklist, task)] + [self.__format_row(tasklist, task, subtask) for subtask in subtasks]

    def __format_row(self, tasklist, task, subtask=None):
        row = [tasklist['ZTITLE'], task['ZTITLE']]
        if not subtask:
            row += [task['ZSTARRED']]
            row += [1 if task['ZCOMPLETER'] else 0]
            row += [self.__get_date(task['ZCREATEDAT']), self.__get_date(task['ZCOMPLETEDAT']), self.__get_date(task['ZDUEDATE'])]
            if task['ZNOTE']: row += [task['ZNOTE']]
        else:
            row += ['']
            row += [1 if task['ZCOMPLETER'] else 0]
            row += [self.__get_date(subtask['ZCREATEDAT']), self.__get_date(subtask['ZCOMPLETEDAT']), '', '', subtask['ZTITLE']]

        return row

    def __get_date(self, date_timestamp):
        base_date = datetime(2001, 1, 1)
        return datetime.fromtimestamp(time.mktime(base_date.timetuple()) + date_timestamp).isoformat() if date_timestamp else '';

    def __write_csv(self, filename, rows):
        with open(filename, 'wb') as csvfile:
            writer = CsvExporter.UnicodeWriter(csvfile, delimiter=';', escapechar='\\', doublequote=False, quoting=csv.QUOTE_ALL, strict=True)
            writer.writerows(rows)


class TwoDoExporter(Exporter):
    def __init__(self, reader):
        super(TwoDoExporter, self).__init__(reader)
    
    def execute(self, args):
        print 'Executing 2Do exporter...'


def die(msg):
    print >> sys.stderr, '%s: %s' % (sys.argv[0], msg)
    sys.exit(1)

def parse_args(exporters, default_exporter):
    from optparse import OptionParser,TitledHelpFormatter
    
    parser = OptionParser(description=DESCRIPTION, usage=USAGE, version=VERSION)

    parser.set_defaults(wunderlist_db_path=get_wunderlist_db_path())
    parser.add_option('-w', '--wunderlist-db', dest='wunderlist_db_path',
                      metavar='DB_PATH', help='path to Wunderlist database')

    parser.set_defaults(exporter=default_exporter)
    parser.add_option('-e', '--exporter', type='choice', choices=exporters,
                      help='exporter to use (%s)' % (', '.join(exporters)))

    parser.set_defaults(filename='wunderlist.csv')
    parser.add_option('-f', '--filename', help='CSV filename to export data')
    
    (options, args) = parser.parse_args()

    return options

def get_wunderlist_db_path():
    from itertools import ifilter

    db_path = '/Library/Application Support/Wunderlist/WKmodel.sqlite'
    possible_paths = [
        os.getenv('HOME') + db_path,
        '%s/Library/Containers/com.wunderkinder.wunderlistdesktop/Data%s' % (os.getenv('HOME'), db_path)
    ]

    return next(ifilter(lambda path: os.path.isfile(path), possible_paths), None)

if __name__ == '__main__':
    exporters = { 'csv': CsvExporter, '2do': TwoDoExporter }
    args = parse_args(exporters.keys(), 'csv')

    reader = WunderlistReader(args.wunderlist_db_path)
    exporter = exporters[args.exporter](reader)
    exporter.execute(args)
    del reader, exporter
