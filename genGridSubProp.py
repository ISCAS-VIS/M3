#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [grid-at]
# JSON

import os
import logging
import getopt
import sys
import time
import json
from multiprocessing import Process
from util.dbopts import connectMongo
from util.GridPropSup import GridPropSup
from util.preprocess import chunks, getCityLocs
from util.preprocess import parseFormatGID


def mergeGrids(basepath, jobsNum):
	# 加载所有网格
	locs = getCityLocs('beijing')
	SPLIT = 0.0005
	LATNUM = int((locs['north'] - locs['south']) / SPLIT + 1)
	LNGNUM = int((locs['east'] - locs['west']) / SPLIT + 1)

	totalLen = LATNUM * LNGNUM
	result = [parseFormatGID(locs, i) for i in xrange(0, totalLen)]

	# 根据每个文件对网格进行更新
	for i in xrange(0, jobsNum):
		with open(os.path.join(basepath, "BJ-MID-SQL", "grid-j%d" % j)) as f:
			for each in f:
				each = each.strip().split(',')
				nid = int(each[0])
				pid = int(each[1])

				if result[nid]['pid'] != -1:
					result[nid]['pid'] = pid
		f.close()

	# 结果写入文件
	result = [i for i in result if i['pid'] != -1]
	with open(os.path.join(basepath, 'BJ-MID-SQL', 'grid-at'), 'ab') as res:
		res.write(json.dumps(result).encode('utf-8'))
	res.close()


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
		'pid': 1,
		'coordinates': 1
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
	mergeGrids(directory, 20)

	# @多进程运行程序 END

	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-gengridsubprop.log', level=logging.DEBUG)
	main(sys.argv[1:])
