#derive test set
from application import db
from application.models import *
from collections import Counter
from random import shuffle
import pickle
from ratio_functions import *
from sklearn.utils import resample
import sqlite3
from nltk.corpus import stopwords
import numpy

#dictionary_com
dictcom_dictionary = dict([(term.term, term.year) for term in db.session.query(Dictionary).all()])
oed_dictionary = dict([(term.term, term.oed_first) for term in db.session.query(Oed).all()])
conn_w = sqlite3.connect('walker_datastore.db')
cw = conn_w.cursor()

stops = stopwords.words('English')

#create results_db here
conn = sqlite3.connect('all_measures_walker.db')
c = conn.cursor()
create = """CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, is_resample INTEGER, test_train INTEGER, doc_id TEXT, tt_ratio REAL,
oed_ratio_no_set REAL, oed_matched_no_set REAL, oed_passed_no_set REAL, oed_neo REAL, oed_ratio_set REAL,
oed_matched_set REAL, oed_passed_set REAL, oed_neo_set REAL, gl_ratio_no_set REAL, matched_no_set REAL, passed_no_set,
neo, gl_ratio_set REAL, matched_set REAL, passed_set REAL, neo_set REAL, walker_ratio_no_set REAL, walker_matched_no_set REAL,
walker_passed_no_set REAL, walker_ratio_set REAL, walker_matched_set REAL, walker_passed_set REAL)"""
c.execute(create)
insert = """INSERT INTO results (id, is_resample, test_train, doc_id, tt_ratio, oed_ratio_no_set, oed_matched_no_set, oed_passed_no_set,
oed_neo, oed_ratio_set, oed_matched_set, oed_passed_set, oed_neo_set, gl_ratio_no_set, matched_no_set, passed_no_set,
neo, gl_ratio_set, matched_set, passed_set, neo_set, walker_ratio_no_set, walker_matched_no_set, walker_passed_no_set,
walker_ratio_set, walker_matched_set, walker_passed_set) VALUES (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

walker_query = """SELECT term, c_count FROM counts LEFT JOIN terms ON counts.term_id=terms.id WHERE c_count > 1 ORDER BY c_count DESC"""
data = cw.execute(walker_query).fetchall()
walker_dictionary = {}

is_resample= 0
test_train = 0
#remove stopwords
no_fw = [tup for tup in data if tup[0] not in stops]
expanded = counts_to_shuffled(no_fw)
#conditional, len >= 5000
if len(expanded) >= 5000:
    _id = "WalkerDict"
    #to analyze as set, run same function on as_set
    as_set = [f[0] for f in no_fw]

    tt_ratio = float(len(no_fw))/len(expanded)
    #calculate walker, oed, and dictcom ratios, plus to neologism scores for all, cluster_train, cluster_test
    results = run_all_ratios(expanded, as_set, oed_dictionary, dictcom_dictionary, walker_dictionary)
    row = [is_resample, test_train, _id, tt_ratio]
    row.extend(results)
    #store in db ... make each a row, all the same

    c.execute(insert, row)
    conn.commit()
    expanded = numpy.asarray(expanded)
    #runis_resample 5k, all calcs
    resampled = []
    for i in range(1000):
        a = resample(expanded, n_samples=5000)
        resampled.append(a)

    for res in resampled:
        is_resample= 1
        tt_ratio = float(len(set(res)))/5000
        results = run_all_ratios(res, set(res), oed_dictionary, dictcom_dictionary, walker_dictionary)
        #to db
        row = [is_resample, test_train, _id, tt_ratio]
        row.extend(results)
        #store in db ... make each a row, all the same
        c.execute(insert, row)
        conn.commit()
