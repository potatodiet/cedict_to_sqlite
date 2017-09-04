#!/usr/bin/env python3
import sqlite3
from pinyin import convert_pinyin

conn = sqlite3.connect("cedict.db")
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS entries")
c.execute("CREATE TABLE entries (traditional TEXT, simplified TEXT, pinyin TEXT, english TEXT)")
c.execute("CREATE INDEX entries_index ON entries (traditional, simplified)")

with open("cedict.txt", "rt") as f:
    for line in f:
        if line[0] is "#":
            continue

        line = convert_pinyin(line)

        trad, simp = line.split(" ")[:2]
        pinyin = line[line.index("[") + 1 : line.index("]")]
        english = line[line.index("/") + 1 : -2].strip()
        c.execute("INSERT INTO entries VALUES (?,?,?,?)", (trad, simp, pinyin, english))

conn.commit()
