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

walker_query = """SELECT term FROM counts LEFT JOIN terms ON counts.term_id=terms.id"""
walker_terms = [i[0] for i in cw.execute(walker_query).fetchall()]
#walker dictionary
walker_dictionary = Counter(walker_terms)

stops = stopwords.words('English')

#get ids, titles, authors, len, years of fiction
years = [(r.pub_year, r.doc_id, r.author_last, r.total_wordcount, r.title) for r in db.session.query(Metadata).filter(Metadata.genre=='fic').all()]
years.sort()

#group by 25-year ranges
groups = []
year_range = 25
start = 1751
end = 1900
for i in range(start, end, year_range):
    e = i+year_range-1
    r = str(i)+"-"+str(e)
    docs = [z for z in years if z[0] >= i and z[0] <= e ]
    mytuple = (r, docs)
    groups.append(mytuple)


#load test set from pickle, 15 ids per item in list, each item is a grouping matching groups list of tuples
test_set = pickle.load(open("test_set.p", "rb" ) )
test_set_flat = []
for f in test_set:
     test_set_flat.extend(f)
#loop through groups, separate test from train, get ids for date range if word count big enough
count = 0

#create results_db here
conn = sqlite3.connect('all_measures_fiction.db')
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

for s, t in groups:
    train_doc_ids = [y[1] for y in t if y[3] >= 5000 and y[1] not in test_set_flat]
    #print(train_doc_ids)#s = year range as string
    test_doc_ids = [z for z in test_set[count]]
    count +=1
    #loop train_doc_ids
    for _id in train_doc_ids:
        #convert doc_id to w_id
        is_resample= 0
        test_train = 0
        w_id = db.session.query(Metadata).filter(Metadata.doc_id==_id).one().id
        data = [(row.type, row.type_count) for row in db.session.query(Counts).filter(Counts.work_id==w_id).filter(Counts.type_count > 1)]
        #remove stopwords
        no_fw = [tup for tup in data if tup[0] not in stops]
        expanded = counts_to_shuffled(no_fw)
        #conditional, len >= 5000
        if len(expanded) >= 5000:
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
            for i in range(100):
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
    for _id in test_doc_ids:
        is_resample = 0
        test_train = 1
        w_id = db.session.query(Metadata).filter(Metadata.doc_id==_id).one().id
        data = [(row.type, row.type_count) for row in db.session.query(Counts).filter(Counts.work_id==w_id).filter(Counts.type_count > 1)]
        #remove stopwords
        no_fw = [tup for tup in data if tup[0] not in stops]
        expanded = counts_to_shuffled(no_fw)
        if len(expanded) >= 5000:
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
            for i in range(100):
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
