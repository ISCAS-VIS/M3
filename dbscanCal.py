#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import sys
import time
import logging
import getopt
from util.dbscanPOI import DBScanPOI


def processTask(directory, clusterNum, eps, min_samples, msfile, msOptSubFix): 
	PROP = {
		'clusterNum': clusterNum, 
		'IDIRECTORY': directory,
		'ODIRECTORY': directory,
		'msFile': msfile,
		'msOptSubFix': msOptSubFix
	}

	task = DBScanPOI(PROP)
	task.run(eps, min_samples)


def usage():
	"""
	使用说明函数
	"""
	print "python test.py -d /datasets -m 6 -e 0.01 -s 10 -f meanshiftResult_c12_t1_quan_0.020000_sam_500"


def main(argv):
    	"""
	主入口函数
		:param argv: 
		city 表示城市， directory 表示路径
		eps, sample 分别为 DBScan 的两个入参
		msfile 表示 meanshift 文件名
		mstype 为 meanshift 聚类数据源类型，例如c12_t1
		msopts 为 meanshift 参数设置拼接字符串，例如quan_0.020000_sam_500
	"""
	try:
		argsArray = ["help", "city=", 'directory=', "msnum=", "eps=", "sample=", "msfile"]
		opts, args = getopt.getopt(argv, "hc:d:m:e:s:f:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records'
	msnum = 6
	eps, min_samples = 0.01, 10
	msfile = "meanshiftResult_c12_t1_quan_0.020000_sam_500"
	msOptSubFix = "_c12_t1_quan_0.020000_sam_500"

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
		elif opt in ("-e", "--eps"):
			eps = float(arg)
		elif opt in ('-s', '--sample'):
			min_samples = int(arg)
		elif opt in ("-f", "--msfile"):
			msfile = arg

	STARTTIME = time.time()
	print "%s: Start approach at %s" % (city, STARTTIME)

	processTask(directory, msnum, eps, min_samples, msfile, msOptSubFix)
	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-dbscancal.log', level=logging.DEBUG)
	main(sys.argv[1:])