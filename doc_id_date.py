#derive test set
from application import db
from application.models import *
import sqlite3

#get ids, dates fiction
years = [(r.pub_year, r.doc_id, r.title) for r in db.session.query(Metadata).filter(Metadata.genre=='fic').all()]

conn = sqlite3.connect('all_measures_fiction.db')
c = conn.cursor()
create = """CREATE TABLE IF NOT EXISTS metadata (pub_year INTEGER, doc_id TEXT, title TEXT)"""
c.execute(create)
insert = """INSERT INTO metadata (pub_year, doc_id, title ) VALUES (?,?,?)"""

for i in years:
    c.execute(insert, i)
    conn.commit()
