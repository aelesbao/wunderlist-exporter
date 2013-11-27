# Wunderlist Exporter

An utility to export Wunderlist tasks to CSV or import them into [2Do][2do].
Can be easily extended to support other task managers.

## Usage

From the command line type `./wunderlist_export.py`

To import tasks into *2Do*, specify these arguments:

`-e 2do -2 TWODO_DB_PATH`

Since I couldn't find where the 2Do DB file is located, I used a backup
DB and later just restored this DB in the app preferences.

### Options

    --version             show program's version number and exit
    -h, --help            show this help message and exit

    -w DB_PATH, --wunderlist-db=DB_PATH
                          path to Wunderlist database

    -e EXPORTER, --exporter=EXPORTER
                          exporter to use (2do, csv)

    -f FILENAME, --filename=FILENAME
                          CSV filename to export data

    -2 TWODO_DB_PATH, --2do-db=TWODO_DB_PATH
                          path to 2Do backup database

[2do]: http://www.2doapp.com/ "2Do"
