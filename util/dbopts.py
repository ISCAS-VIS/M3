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

def connectMYSQL(dbname):
	"""Connect MySQL
	
	Returns:
		TYPE: db, cursor
	"""
	db = MySQLdb.connect(host="192.168.1.42",    	# your host, usually localhost
						user="root",         	# your username
						passwd="vis_2014",  	# your password
						db=dbname)		# name of the data base
	cur = db.cursor()

	return db, cur

def getGridsFromMongo(city, db):
	"""从 MongoDB 获取 grid 数据，传回第一个参数为 dictionary, 存有不同 id 的 POI vector; 第二个参数存有有效网格 ID 列表
	
	Args:
	    city (TYPE): Description
	    db (TYPE): Description
	
	Returns:
	    TYPE: Description
	"""
	res = list( db['newgrids_%s' % city].find({"properties.vecvalid": True }, {"properties.uid": 1, "properties.vec": 1}) )
	gridsData, validIDs = {}, []
	reslen = len(res)
	for x in xrange(0, reslen):
		id = str(res[x]['properties']['uid'])
		vec = np.array(res[x]['properties']['vec'], dtype='f')
		gridsData[ id ] = vec
		validIDs.append(id)

	return gridsData, validIDs