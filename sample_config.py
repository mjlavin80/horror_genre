import os

MYDB = "dbname"
PWD = "your_db_password"

#change db uri here to switch databases
SQLALCHEMY_DATABASE_URI = "postgresql://..."
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = True
SECRET_KEY = 'random alpha-numerical string'
