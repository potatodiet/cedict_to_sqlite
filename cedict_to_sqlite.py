#!/usr/bin/env python3
import sqlite3, requests, pathlib, gzip
from pinyin import convert_pinyin

if not pathlib.Path("/tmp/cedict.txt.gz").is_file():
    with open("/tmp/cedict.txt.gz", "wb") as f:
        r = requests.get("https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz")
        f.write(r.content)

conn = sqlite3.connect("/tmp/cedict.db")
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS entries")
c.execute("CREATE TABLE entries (traditional TEXT, simplified TEXT, pinyin TEXT, english TEXT)")
c.execute("CREATE INDEX entries_index ON entries (traditional, simplified)")

with gzip.open("/tmp/cedict.txt.gz", "rt") as f:
    for line in f:
        if line[0] is "#":
            continue

        line = convert_pinyin(line)

        trad, simp = line.split(" ")[:2]
        pinyin = line[line.index("[") + 1 : line.index("]")]
        english = line[line.index("/") + 1 : -2].strip()
        c.execute("INSERT INTO entries VALUES (?,?,?,?)", (trad, simp, pinyin, english))

conn.commit()
