#derive test set
from application import db
from application.models import *
from collections import Counter
from random import shuffle
import pickle
from ratio_functions import *
from nltk.corpus import stopwords
stops = stopwords.words('English')

#connect to db

#get ids, titles, authors, len, years of fiction
#get years from metadata, loop through them
years = [(r.pub_year, r.doc_id, r.author_last, r.total_wordcount, r.title) for r in db.session.query(Metadata).filter(Metadata.genre=='fic').all()]
years.sort()

#group by 5-year or 10-year ranges
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

#groups = four levels deep
#groups[0][1][0][0] is a date
#groups[0][1][0][1] is a doc_id

#print([(g[0], len(g[1])) for g in groups])
#grab 15 random doc_ids per cluster and store as a pickle
test_set = []
for p, q in groups:
    doc_ids = []
    #doc_ids= [y[1] for y in q if y[3] >= 5000]
    for y in q:
        _id = y[1]
        w_id = db.session.query(Metadata).filter(Metadata.doc_id==_id).one().id
        data = [(row.type, row.type_count) for row in db.session.query(Counts).filter(Counts.work_id==w_id).filter(Counts.type_count > 1)]
        #remove stopwords
        no_fw = [tup for tup in data if tup[0] not in stops]
        expanded = counts_to_shuffled(no_fw)
        if len(expanded) >= 5000:
            doc_ids.append(_id)
    shuffle(doc_ids)
    testers = doc_ids[:15]
    test_set.append(testers)

pickle.dump( test_set, open( "test_set.p", "wb" ) )
#print [len(u) for u in test_set]
