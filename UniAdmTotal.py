#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import sys
import time
# import os
import json
import logging
import getopt
from multiprocessing import Process
from util.UniAdmDiswithEdgeBasic import UniAdmDiswithEdgeBasic
from util.preprocess import getAdminNumber
from shapely.geometry import shape

def processTask(x, city, directory, inum, subopath, bounds): 
	PROP = {
		'INDEX': x, 
		'CITY': city, 
		'DIRECTORY': directory, 
		'INUM': inum,
		'SUBOPATH': subopath,
		'bounds': bounds
	}

	task = UniAdmDiswithEdgeBasic(PROP)
	task.run()


def usage():
	"""
	使用说明函数
	"""
	print '''Usage Guidance
help	-h	get usage guidance
city	-c	city or region name, such as beijing
directory	-d	the root directory of records and results, such as /China/beijing
inum	-i	number of input files
'''


def main(argv):
	"""
	主入口函数
		:param argv: 
		city 表示城市， directory 表示路径， inum 表示输入文件总数， jnum 表示处理进程数， subopath 为结果存储的子目录名字
	"""
	try:
		opts, args = getopt.getopt(argv, "hc:d:i:j:", ["help", "city=", 'directory=', 'inum=', 'jnum='])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records'
	inum, jnum, subopath = 86, 20, 'bj-newvis-sg'
	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-c", "--city"):
			city = arg
		elif opt in ("-d", "--directory"):
			directory = arg
		elif opt in ('-i', '--inum'):
			inum = int(arg)
		elif opt in ('-j', '--jnum'):
			jnum = int(arg)

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	bounds = []
	with open('/home/joe/Documents/git/statePrediction/datasets/beijingBoundary.json', 'rb') as s:
		tmp = json.load(s, encoding='utf-8')
		tmp = tmp['features']
		for each in tmp:
			id = getAdminNumber(each['properties']['name'].encode("utf-8"))
			bounds.append({
				'id': id,
				'b': shape(each['geometry'])
			})
	s.close()

	# @多进程运行程序 START
	jobs = []

	for x in xrange(0, jnum):
		task = Process(target=processTask, args=(x, city, directory, inum, subopath, bounds))
		jobs.append(task)
		jobs[x].start()

	for job in jobs:
		job.join()

	# @多进程运行程序 END

	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-uniadmtotal.log', level=logging.DEBUG)
	main(sys.argv[1:])