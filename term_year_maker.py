from application import db
from application.models import *
from collections import Counter
from random import shuffle
from ratio_functions import dictcom_gl_ratio
from sklearn.utils import resample
import sqlite3, json

conn = sqlite3.connect('terms_years.db')
c = conn.cursor()
create = """CREATE TABLE IF NOT EXISTS terms_years (id INTEGER PRIMARY KEY,
             term TEXT, year integer)"""
c.execute(create)

#get years from metadata, loop through them
years = list(set([row.pub_year for row in db.session.query(Metadata).order_by(Metadata.pub_year).all()]))
#print(ids)

from nltk.corpus import stopwords
import pickle
test_set = pickle.load(open("test_set.p", "rb" ) )
test_set_flat = []
for f in test_set:
     test_set_flat.extend(f)
test_doc_ids = []
for _id in test_set_flat:
    work_id = db.session.query(Metadata).filter(Metadata.doc_id==_id).one().id
    test_doc_ids.append(work_id)

terms_years = {}
for year in years:
    #print(year)
    #get all ids matching year, fiction only
    fic_ids = [row.id for row in db.session.query(Metadata).filter(Metadata.pub_year==year).filter(Metadata.genre=='fic')]
    if fic_ids:
        data = [row.type for row in db.session.query(Counts).filter(Counts.work_id.in_(fic_ids)).filter(Counts.work_id.notin_(test_doc_ids)).filter(Counts.type_count > 1)]
        #print(data)
        for term in data:
            try:
                already_in = terms_years[term]
            except:
                terms_years[term] = year

for term, year in terms_years.items():
    #insert in db
    insert = """INSERT INTO terms_years (id, term, year) VALUES (null, ?, ?)"""
    c.execute(insert, (term, year))
    conn.commit()
