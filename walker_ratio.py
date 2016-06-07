from application import db
from application.models import *
from collections import Counter
from random import shuffle
from sklearn.utils import resample
import sqlite3, json
from nltk.corpus import stopwords
from ratio_functions import walker_ratio

conn_w = sqlite3.connect('walker_datastore.db')
cw = conn_w.cursor()

walker_query = """SELECT term FROM counts LEFT JOIN terms ON counts.term_id=terms.id"""
walker_terms = [i[0] for i in cw.execute(walker_query).fetchall()]
#walker dictionary
walker_dictionary = Counter(walker_terms)

#get years from metadata, loop through them
years = list(set([row.pub_year for row in db.session.query(Metadata).order_by(Metadata.pub_year).all()]))
#print(ids)


for year in years:
    #get all ids matching year, divide into genres here

    id_tuples = [(row.id, row.genre) for row in db.session.query(Metadata).filter(Metadata.pub_year==year)]
    ids = [i[0] for i in id_tuples]
    non_ids = [i[0] for i in id_tuples if i[1] == 'non']
    bio_ids = [i[0] for i in id_tuples if i[1] == 'bio']
    fic_ids = [i[0] for i in id_tuples if i[1] == 'fic']
    dra_ids = [i[0] for i in id_tuples if i[1] == 'dra']
    poe_ids = [i[0] for i in id_tuples if i[1] == 'poe']
    ora_ids = [i[0] for i in id_tuples if i[1] == 'ora']
    all_ids = [ids, non_ids, bio_ids, fic_ids, dra_ids, poe_ids, ora_ids]

    #get all tokens and counts matching year ... reduce to tuples
    all_data = []
    for id_list in all_ids:
        if len(id_list) != 0:
            data = [(row.type, row.type_count) for row in db.session.query(Counts).filter(Counts.work_id.in_(id_list)).filter(Counts.type_count > 1)]
        else:
            data = []
        all_data.append(data)

    #loop all_data
    datakey = ("all_genres", "nonfiction", "biography", "fiction", "drama", "poetry", "oratory")
    for count, dataset in enumerate(all_data):
        if len(dataset) == 0:
            no_data = [None for i in range(8)]
            data_list = [1, 0, year, datakey[count]]
            data_list.extend(no_data)
            data_tuple = tuple(data_list)
        else:
            #remove function words
            s = stopwords.words('English')
            no_fw = [i for i in dataset if i[0] not in s]
            #convert to shuffled list
            expanded = []
            for t, c in no_fw:
                e = [t for i in range(c)]
                expanded.extend(e)
            shuffle(expanded)

            #original_length
            original_length = len(expanded)
            if original_length >= 5000:
                #type-token ratio, after removing function words and hapaxes
                tt_ratio = 1.0*len(no_fw)/len(expanded)

                #run function on shuffled for plain ratio
                walker_ratio_no_set, matched_no_set, passed_no_set = walker_ratio(expanded, walker_dictionary)

                #to analyze as set, run same function on as_set
                as_set = [f[0] for f in no_fw]
                walker_ratio_set, matched_set, passed_set = walker_ratio(as_set, walker_dictionary)

                #matches
                walker_matches = {"matched_set":matched_set, "matched_no_set": matched_no_set, "passed_set": passed_set, "passed_no_set": passed_no_set}

                #resample
                resamples = []
                for i in range(100):
                    a = resample(expanded, n_samples=5000)
                    resamples.append(a)

                #run resampled regularly, and as set
                walker_resample_no_set = []
                walker_resample_set =[]
                for i in resamples:
                    results = walker_ratio(i, walker_dictionary)
                    walker_resample_no_set.append(results[0])
                    set_results = walker_ratio(set(i), walker_dictionary)
                    walker_resample_set.append(results[0])

                #resample TT ratios
                resample_tt_ratios = []
                for i in resamples:
                    token_count = len(i)
                    type_count = len(set(i))
                    resample_tt_ratios.append(1.0*type_count/token_count)
                #final data tuple for db
                data_tuple = (0, 0, year, datakey[count], original_length, tt_ratio, json.dumps(walker_matches), walker_ratio_set, walker_ratio_no_set, json.dumps(walker_resample_set), json.dumps(walker_resample_no_set), json.dumps(resample_tt_ratios))
            else:
                no_data = [None for i in range(7)]
                data_list = [0, 1, year, datakey[count], original_length]
                data_list.extend(no_data)
                data_tuple = tuple(data_list)
        #store results in sqlite database
        conn = sqlite3.connect('walker_ratios_data.db')
        c = conn.cursor()
        create = """CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY,
                     no_data integer, too_short integer, year integer, genre text, original_length integer,
                     tt_ratio real, walker_matches blob, walker_ratio_set real, walker_ratio_no_set real,
                     walker_resample_set blob, walker_resample_no_set blob, resample_tt_ratios blob)"""
        c.execute(create)
        insert = """INSERT INTO results (id, no_data, too_short, year, genre, original_length,
        tt_ratio, walker_matches, walker_ratio_set, walker_ratio_no_set, walker_resample_set, walker_resample_no_set,
        resample_tt_ratios) VALUES (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        c.execute(insert, data_tuple)
        conn.commit()
        data_tuple = (0, 0, year, datakey[count], original_length, tt_ratio, walker_matches, walker_ratio_set, walker_ratio_no_set, walker_resample_set, walker_resample_no_set, resample_tt_ratios )
