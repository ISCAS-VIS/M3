#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 


import os
import logging
import getopt
import sys
import time
from multiprocessing import Process
from util.dbopts import connectMongo
from util.GridPropSup import GridPropSup
from util.preprocess import chunks


def processTask(INDEX, city, basepath, pidList):
	task = GridPropSup({
		'INDEX': INDEX,
		'city': city,
		'basepath': basepath,
		'pidList': pidList
	})
	task.run()


def usage():
    	pass


def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hc:d:", ["help", "city=", 'directory='])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records'
	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-c", "--city"):
			city = arg
		elif opt in ("-d", "--directory"):
			directory = arg

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	conn, db = connectMongo('stvis')
	plist = list(db['pois'].find({}, {
		'properties.pid': 1,
		'properties.coordinates': 1
	}))
	pois = list(chunks(plist, 20))
	conn.close()

	# @多进程运行程序 START
	jobs = []

	for x in xrange(0, 20):
		tProcess = Process(target=processTask, args=(x, city, directory, pois[x]))
		jobs.append(tProcess)
		jobs[x].start()

	for job in jobs:
		job.join()

	# 处理剩余数据进文件
	# 合并操作
	mergeLargeRecords(city, directory, 'bj-byday', 87)

	# @多进程运行程序 END

	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-gengridsubprop.log', level=logging.DEBUG)
	main(sys.argv[1:])
