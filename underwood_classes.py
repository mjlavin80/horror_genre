#import MySQLdb
import csv
import sys
import io
from itertools import repeat
import urllib
from config import MYDB, PWD
from application import db
from application.models import *

def line_to_escape_tuple(a_line):
    data = []
    for i in a_line:
        try:
            d = urllib.quote_plus(i.decode('utf8', 'ignore'))
            data.append(d)
        except:
            b = urllib.quote_plus(i.decode('ascii', 'ignore'))
            data.append(b)
    return tuple(data)

class TsvHandler(object):
         def __init__(self):
                  self.metadata = "DocMetadata.txt"
                  self.word_list = "JointCorpus.txt"
                  self.dic = "Etymologies.txt"
         def dictionary_com_list(self):
                  with open (self.dic, "r") as myfile:
                           count = 1
                           #insert statement
                           for line in csv.reader(myfile, dialect="excel-tab"):
                               d_data = line_to_escape_tuple(line)
                               k = ("term_id", "term", "year")
                               ins = Dictionary()
                               setattr(ins, k[0], None)
                               setattr(ins, k[1], d_data[0])
                               setattr(ins, k[2], d_data[1])
                                   #try:
                               #slower than raw psycopg2 but will work with sqlite, mysql, or posgresql
                               db.session.add(ins)
                               if count % 1000 == 0:
                                   print count
                               count +=1
                               db.session.commit()

         def build_metadata(self):
                  with open (self.metadata, "r") as myfile:
                           count = 1
                           #insert statement
                           #db = MySQLdb.connect(host="localhost", user="root", passwd=PWD, db=MYDB)
                           for m_line in csv.reader(myfile, dialect="excel-tab"):
                               m_data = line_to_escape_tuple(m_line)
                               #print([type(i) for i in m_data])
                               author_pair = urllib.unquote_plus(m_data[2]).split(', ')
                               if len(author_pair) > 3:
                                   author_tuple = []
                                   author_tuple.append(author_pair[0])
                                   a = " ".join(author_pair[1:-1])
                                   author_tuple.append(a)
                                   author_tuple.append(author_pair[-1])

                               else:
                                   author_tuple = author_pair

                               author_tuple = [urllib.quote_plus(u) for u in author_tuple]
                               m_data_first = list(m_data[0:2])
                               m_data_first.extend(author_tuple)
                               m_data_first.extend(list(m_data[3:]))
                               if len(author_tuple) == 1:
                                   k = ["doc_id", "filename", "author_last", "pub_year", "genre", "collection", "total_wordcount", "dictionary_wordcount", "title"]

                               if len(author_tuple) == 2:
                                   k = ["doc_id", "filename", "author_last", "author_first", "pub_year", "genre", "collection", "total_wordcount", "dictionary_wordcount", "title"]

                               if len(author_tuple) == 3:
                                   k = ["doc_id", "filename", "author_last", "author_first", "author_dates", "pub_year", "genre", "collection", "total_wordcount", "dictionary_wordcount", "title"]
                               a = dict(zip(k, m_data_first))

                               ins = Metadata()
                               ins.id = None
                               for i, j in enumerate(m_data_first):
                                  setattr(ins, k[i], j)

                               db.session.add(ins)
                               if count % 1000 == 0:
                                  print count
                               count +=1
                               db.session.commit()

                                    #stmnt = """INSERT INTO metadata (doc_id, filename, author_dates, pub_year, genre, collection, total_wordcount, dictionary_wordcount, title) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s');""" % m_data

         def csv_processor(self):
                  with open (self.word_list, "r") as myfile:
                           data_reader = csv.reader(myfile, dialect="excel-tab")
                           my_buffer = []
                           count = 0
                           for line in data_reader:
                                    data = line_to_escape_tuple(line)
                                    my_buffer.append(data)
                                    count += 1
                                    if count == 50000:
                                        count = 0
                                        yield my_buffer
                                        my_buffer = []

         def build_counts(self):
                  #db = MySQLdb.connect(host="localhost", user="root", passwd=PWD, db=MYDB)
                  #c=db.cursor()
                  id_dict = dict([(row.doc_id, row.id) for row in db.session.query(Metadata).all()])
                  k = ["segment", "doc_id", "type", "type_count", "year", "genre", "collection"]
                  count = 50000
                  for my_buffer in self.csv_processor():
                           #my_buffer is 20000 rows as tuples
                           #every tuple becomes a dictionary with k for keys
                           pairs = []
                           for a in my_buffer:
                               mydict = dict(zip(k, list(a)))
                               doc_id = mydict["doc_id"]
                               try:
                                   mydict["work_id"] = id_dict[doc_id]
                               except:
                                   print id_dict[doc_id]
                               pairs.append(mydict)
                           #c.executemany("""INSERT INTO counts (segment, doc_id, type, type_count, year, genre, collection) VALUES (%s, %s, %s, %s, %s, %s, %s)""", my_buffer)
                           #db.session.bulk_insert_mappings(Counts, pairs)
                           db.engine.execute(Counts.__table__.insert(), pairs)
                           db.session.commit()
                           print "Finished processing ", count
                           count +=50000
