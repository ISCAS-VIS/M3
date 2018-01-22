#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 


import sys
import time
import logging
import getopt
from util.meanshiftPOI import MeanshiftPOI


def processTask(mstype, directory, quantile, n_samples): 
	PROP = {
		'mstype': mstype, 
		'IDIRECTORY': directory,
		'ODIRECTORY': directory
	}

	task = MeanshiftPOI(PROP)
	task.run(quantile, n_samples)


def usage():
	"""
	使用说明函数
	"""
	print "python test.py -d /datasets -t c12_t1 -q 0.2 -n 500"


def main(argv):
    	"""
	主入口函数
		:param argv: 
		city 表示城市， directory 表示路径
		type 为 meanshift 聚类数据源类型
		quantile, n_samples 分为别 Meanshift 两个入参
	"""
	try:
		argsArray = ["help", "city=", 'directory=', "type=", "quantile=", "n_samples="]
		opts, args = getopt.getopt(argv, "hc:d:t:q:n:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records'
	mstype = 'c12_t1'
	quantile, n_samples = 0.2, 500

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
		elif opt in ("-q", "--quantile"):
			quantile = float(arg)
		elif opt in ('-n', '--n_samples'):
			n_samples = int(arg)

	STARTTIME = time.time()
	print "%s: Start approach at %s" % (city, STARTTIME)

	processTask(mstype, directory, quantile, n_samples)
	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-meanshiftcal.log', level=logging.DEBUG)
	main(sys.argv[1:])