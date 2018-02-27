#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# 先 MeanShift 再 DBScan 记录，在最新版数据中未使用


import sys
import time
import logging
import getopt
from util.meanshiftPOI import MeanshiftPOI
from util.dbscanPOI import DBScanPOI


def processTask(mstype, directory, quantile, n_samples, eps, min_samples): 
	msPROP = {
		'mstype': mstype, 
		'IDIRECTORY': directory,
		'ODIRECTORY': directory
	}

	task = MeanshiftPOI(msPROP)
	clusterNum = task.run(quantile, n_samples)

	msOptSubFix = "_%s_quan_%f_sam_%d" % (mstype, quantile, n_samples)
	msfile = "meanshiftResult%s" % (msOptSubFix)
	dbPROP = {
		'clusterNum': clusterNum, 
		'IDIRECTORY': directory,
		'ODIRECTORY': directory,
		'msFile': msfile,
		'msOptSubFix': msOptSubFix
	}

	task = DBScanPOI(dbPROP)
	task.run(eps, min_samples)


def usage():
	"""
	使用说明函数
	"""
	print "python combinedClusterCal.py -d /d -t c12_t1 -q 0.05 -n 500 -e 0.01 -m 10"


def main(argv):
    	"""
	主入口函数
		:param argv: 
		city 表示城市， directory 表示路径
		type 为 meanshift 聚类数据源类型
		quantile, n_samples 分为别 Meanshift 两个入参
	"""
	try:
		argsArray = ["help", "city=", 'directory=', "type=", "quantile=", "n_samples=", "eps", "min_samples"]
		opts, args = getopt.getopt(argv, "hc:d:t:q:n:e:m:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records'
	mstype = 'c12_t1'
	quantile, n_samples = 0.2, 500
	eps, min_samples = 0.01, 10

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
		elif opt in ("-e", "--eps"):
			eps = float(arg)
		elif opt in ('-s', '--sample'):
			min_samples = int(arg)

	STARTTIME = time.time()
	print "%s: Start approach at %s" % (city, STARTTIME)

	print '''
	===	Cluster Opts	===
	quantile	= %f
	n_samples	= %d
	eps			= %f
	min_samples	= %d
	===	Cluster Opts	===
	''' % (quantile, n_samples, eps, min_samples)

	processTask(mstype, directory, quantile, n_samples, eps, min_samples)
	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-combinedclustercal.log', level=logging.DEBUG)
	main(sys.argv[1:])