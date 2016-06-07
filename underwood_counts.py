#import MySQLdb
import csv
import sys
import io
from itertools import repeat
import urllib
from config import MYDB, PWD
from application import db
from underwood_classes import *

maxInt = sys.maxsize
decrement = True

if __name__ == "__main__":
    #call instance and method
   _tsv = TsvHandler()
   _tsv.build_counts()
