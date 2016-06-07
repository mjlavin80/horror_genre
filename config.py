import os
import psycopg2
# edit the URI below to add your RDS password and your AWS URL
# The other elements are the same as used in the tutorial
# format: (user):(password)@(db_identifier).amazonaws.com:3306/(db_name)
MYDB = "uw"
PWD = "wyoming45"

#SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/datastore.db' % (os.path.dirname(__file__))
#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:%s@localhost:3306/%s?charset=utf8' % (PWD, MYDB)
#SQLALCHEMY_DATABASE_URI = "postgresql://mjlavin80:wyoming45@walker.cyizldgqnjpd.us-west-2.rds.amazonaws.com:5432/postgres"
SQLALCHEMY_DATABASE_URI = "postgresql://matthewlavin@localhost/walker"
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = True
SECRET_KEY = 'jkdfkqweieqwjweqm,dwqHJADGTT'

#AKIAJTCPZIBDOQR5NWQQ
#print(SQLALCHEMY_DATABASE_URI)
