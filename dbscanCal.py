#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import os
import sys
import time
import logging
import getopt
from util.dbscanPOI import DBScanPOI


def processTask(directory, clusterNum): 
	PROP = {
		'clusterNum': clusterNum, 
		'IDIRECTORY': directory,
		'ODIRECTORY': directory
	}

	task = DBScanPOI(PROP)
	task.run()


def usage():
	"""
	使用说明函数
	"""
	print "python test.py -d /datasets -m 6"


def main(argv):
    	"""
	主入口函数
		:param argv: 
		city 表示城市， directory 表示路径
	"""
	try:
		argsArray = ["help", "city=", 'directory=', "msnum="]
		opts, args = getopt.getopt(argv, "hc:d:m:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records'
	msnum = 6

	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-c", "--city"):
			city = arg
		elif opt in ("-d", "--directory"):
			directory = arg
		elif opt in ('-m', '--msnum'):
			msnum = int(arg)

	STARTTIME = time.time()
	print "%s: Start approach at %s" % (city, STARTTIME)

	processTask(directory, msnum)
	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-dbscancal.log', level=logging.DEBUG)
	main(sys.argv[1:])