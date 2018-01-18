#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import os
import sys
import time
import logging
import getopt
from util.meanshiftPOI import MeanshiftPOI


def processTask(mstype, directory): 
	PROP = {
		'mstype': mstype, 
		'IDIRECTORY': directory,
		'ODIRECTORY': directory
	}

	task = MeanshiftPOI(PROP)
	task.run()


def usage():
	"""
	使用说明函数
	"""
	print "python test.py -d /datasets -t c12_t1"


def main(argv):
    	"""
	主入口函数
		:param argv: 
		city 表示城市， directory 表示路径
	"""
	try:
		argsArray = ["help", "city=", 'directory=', "type="]
		opts, args = getopt.getopt(argv, "hc:d:t:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records'
	mstype = 'c12_t1'

	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-c", "--city"):
			city = arg
		elif opt in ("-d", "--directory"):
			directory = arg
		elif opt in ('-t', '--type'):
			mstype = arg

	STARTTIME = time.time()
	print "%s: Start approach at %s" % (city, STARTTIME)

	processTask(mstype, directory)
	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-meanshiftcal.log', level=logging.DEBUG)
	main(sys.argv[1:])