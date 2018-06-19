#!/usr/bin/env python3
import sqlite3
import gzip
from pathlib import Path
import requests
from pinyin import convert_pinyin


class CLI:
    """ Very basic command line interface to convert a cedict file to a sqlite
        database. """

    WEB_CEDICT_FILE = ("https://www.mdbg.net/chinese/export/cedict/"
                       "cedict_1_0_ts_utf-8_mdbg.txt.gz")

    def __init__(self):
        Path("build/").mkdir(exist_ok=True)

        self.download_cedict()
        self.init_db()
        self.populate_db()

    def download_cedict(self):
        """ Downloads the cedict file and stores it on the filesystem. """

        if not Path("build/cedict.txt.gz").is_file():
            with open("build/cedict.txt.gz", "wb") as file:
                file.write(requests.get(self.WEB_CEDICT_FILE).content)

    def init_db(self):
        """ Drops the cedict database if it already exists, and then creates
            the database. """

        self.conn = sqlite3.connect("build/cedict.db")
        cursor = self.conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS entries")
        cursor.execute("CREATE TABLE entries (traditional TEXT,"
                       "simplified TEXT, pinyin TEXT, english TEXT)")
        cursor.execute("CREATE INDEX entries_index "
                       "ON entries (traditional, simplified)")
        cursor.close()

    def populate_db(self):
        """ Parses the cedict text file, and populates the cedict database
            with the relevant fields. """

        cursor = self.conn.cursor()

        with gzip.open("build/cedict.txt.gz", "rt", encoding="utf-8") as file:
            for line in file:
                if line[0] == "#":
                    continue

                line = convert_pinyin(line)

                trad, simp = line.split(" ")[:2]
                pinyin = line[line.index("[") + 1:line.index("]")]
                english = line[line.index("/") + 1:-2].strip()
                cursor.execute("INSERT INTO entries VALUES (?,?,?,?)",
                               (trad, simp, pinyin, english))

        cursor.close()
        self.conn.commit()


CLI()
