#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import os, pymongo, math, sys, logging, MySQLdb
import numpy as np
from scipy import stats
from geopy.distance import great_circle  # https://pypi.python.org/pypi/geopy/1.11.0

def connectMongo(dbname):
	"""Connect MongoDB
	
	Returns:
		TYPE: Client, database
	"""
	try:
		conn = pymongo.MongoClient('192.168.1.42', 27017) # 192.168.1.42
		mdb = conn[dbname]
		print "Connected successfully!!!"
	except pymongo.errors.ConnectionFailure, e:
		print "Could not connect to MongoDB: %s" % e

	return conn, mdb

def connectMYSQL(dbname, passwd):
	"""Connect MySQL
	
	Returns:
		TYPE: db, cursor
	"""
	db = MySQLdb.connect(host="192.168.1.42",    	# your host, usually localhost
						user="root",         	# your username
						passwd=passwd,  	# your password
						db=dbname)		# name of the data base
	cur = db.cursor()

	return db, cur
