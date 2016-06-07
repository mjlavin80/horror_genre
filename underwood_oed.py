import re
import sqlite3
from application import db
from application.models import *

conn = sqlite3.connect('oed_data.db')
c = conn.cursor()
rows = c.execute('SELECT term, GROUP_CONCAT(year) FROM dictionary WHERE year !=" " GROUP BY term').fetchall()
conn.close()

Oed.query.delete()

def term_normalize(mytuple):
    word = [i for i in mytuple[0].lower() if i.isalpha() or i=="-"]
    word = [i for i in word if i.encode('unicode_escape') != b'\\u02c8' and i.encode('unicode_escape') != b'\\u02cc']
    word = ''.join(word)
    new_tuple = (word, mytuple[1])
    return new_tuple

#lowercase all and drop leading apostrophe and other punctuation (keep hyphens)
new_rows = []
for i in rows:
    a = term_normalize(i)
    new_rows.append(a)

terms_and_origins = []
exceptions = []
for h,i in new_rows:
    quals = []
    if 'oe' in i.lower():
        #the following code is designed to make sure any qualifiers (a, c, ?) are directly before or after oe, eoe, or loe
        pattern = "...oe.|...oe|..oe.|..oe|.oe.|oe.|.oe|oe"
        quals_test = re.search(pattern, i.lower())
        if quals_test:
            if "a" in quals_test.group(0):
                quals.append("a")
            if "c" in quals_test.group(0):
                quals.append("c")
            if "?" in quals_test.group(0):
                quals.append("?")
        row = [h, i, 750, quals]
    else:
        if i[0] == " ":

            if i[1].isdigit():
                #means first char after space is a number
                #test for 4, 3,2, 1 digits
                for z in range(5, 1, -1):
                    if i[1:z].isdigit():
                        try:
                            if i[z+1] == "?":
                                quals.append("?")
                        except:
                            pass
                        year = i[1:z]
                        break
                row = [h,i,year,quals]

            else:
                #match letter or ?letter
                if i[2].isdigit():
                    quals.append(i[1])
                    #test for 4, 3,2, 1 digits
                    for z in range(6, 3, -1):
                        if i[2:z].isdigit():
                            try:
                                if i[z+1] == "?" or i[1] == "?":
                                    quals.append("?")
                            except:
                                pass
                            year = i[2:z]
                            break
                    row = [h,i,year,quals]
                else:
                    #by def should be ?c or ?a
                    quals.append(i[1])
                    quals.append(i[2])
                    #test for 4, 3,2, 1 digits
                    for z in range(7, 4, -1):
                        if i[3:z].isdigit():
                            try:
                                if i[z+1] == "?":
                                    quals.append("?")
                            except:
                                pass
                            year = i[3:z]
                            break
                    row = [h,i,year,quals]
    if int(row[2]) < 1100:
        row.append("germ")
    elif int(row[2]) > 1100 and int(row[2]) < 1700:
        row.append("lat")
    else:
        row.append("neo")
    terms_and_origins.append(row)

#scrub repeated terms, keep one with lower date
terms = {}
for i in terms_and_origins:
    try:
        a = terms[i[0]]
        if i[2] < a[2]:
            terms[i[0]] = i
    except:
        terms[i[0]] = i
oed_normalized = terms.values()

k = ("term_id", "term", "oed_first")
count = 0
for u in oed_normalized:
    ins = Oed()
    setattr(ins, k[0], None)
    setattr(ins, k[1], u[0])
    setattr(ins, k[2], u[2])
    db.session.add(ins)
    if count % 1000 == 0:
        print count
    count +=1
    db.session.commit()
