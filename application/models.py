from application import db

class Metadata(db.Model):
    __tablename__ = 'metadata'
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.String(64), index=True, unique=False)
    filename = db.Column(db.String(64), index=True, unique=False)
    author_last = db.Column(db.String(512), index=False, unique=False)
    author_first = db.Column(db.String(512), index=False, unique=False)
    author_dates = db.Column(db.String(512), index=False, unique=False)
    pub_year = db.Column(db.Integer)
    genre = db.Column(db.String(32), index=True, unique=False)
    subgenre = db.Column(db.String(32), index=True, unique=False)
    collection = db.Column(db.String(32), index=True, unique=False)
    total_wordcount = db.Column(db.Integer)
    dictionary_wordcount = db.Column(db.Integer)
    title = db.Column(db.String(2048), index=False, unique=False)


class Tokens(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    work_id = db.Column(db.Integer, db.ForeignKey("metadata.id"))
    token = db.Column(db.String(128), index=True, unique=False)
    term_id = db.Column(db.Integer, db.ForeignKey("terms.id"))
    pos = db.Column(db.String(128), index=True, unique=False)
    stem = db.Column(db.String(128), index=True, unique=False)
    lemma = db.Column(db.String(128), index=True, unique=False)


class Terms(db.Model):
    __tablename__ = 'terms'
    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(128), index=True, unique=True)
    oed_first = db.Column(db.String(128), index=True, unique=False)
    oed_last = db.Column(db.String(128), index=True, unique=False)
    oed_list = db.Column(db.String(128), index=True, unique=False)
    dictcom = db.Column(db.String(128), index=True, unique=False)

class Counts(db.Model):
    __tablename__ = 'counts'
    counts_id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.String(64), index=True, unique=False)
    work_id = db.Column(db.Integer, db.ForeignKey("metadata.id"))
    type = db.Column(db.String(64), index=True, unique=False)
    type_count = db.Column(db.Integer)
    segment = db.Column(db.Integer)

class Dictionary(db.Model):
    __tablename__ = 'dictionary'
    term_id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(64), index=True, unique=True)
    year = db.Column(db.Integer)

class Oed(db.Model):
    __tablename__ = 'oed'
    term_id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(64), index=True, unique=True)
    oed_first = db.Column(db.String(128), index=True, unique=False)
    oed_last = db.Column(db.String(128), index=True, unique=False)
    oed_list = db.Column(db.String(128), index=True, unique=False)
