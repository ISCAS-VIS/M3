#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import sys
import time
import logging
import getopt
from multiprocessing import Process
from util.preprocess import mergeMatrixs
from util.preprocess import mergeSmallRecords
from util.UniGridDisBasic import UniGridDisBasic

			
def processTask(x, city, directory, inum, onum, judDay, judHour, GRIDSNUM, subpath): 
	PROP = {
		'INDEX': x, 
		'CITY': city, 
		'DIRECTORY': directory, 
		'INUM': inum, 
		'ONUM': onum,
		'DAY': judDay,
		'HOUR': judHour,
		'GRIDSNUM': GRIDSNUM,
		'SUBPATH': subpath
	}
	task = UniGridDisBasic(PROP)
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
onum	-o	number of output files

e.g. 
python ./uniGridDistribution.py -i 3999 -o 20 -d /enigma/tao.jiang/datasets/JingJinJi/records
'''


def main(argv):
	"""
	主入口函数
		:param argv: city 表示城市， directory 表示路径， inum 表示输入文件总数， onum 表示输出文件总数， jnum 表示处理进程数，通常和 onum 一致， subpath 为结果存储的子目录名字
	"""
	try:
		opts, args = getopt.getopt(argv, "hc:d:i:o:j:", ["help", "city=", 'directory=', 'inum=', 'onum=', 'jnum='])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory, inum, onum, jnum, subpath = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records', 3999, 20, 20, 'bj-newvis'
	dayBase, judDay, judHour = 187, 0, 0
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
		elif opt in ('-o', '--onum'):
			onum = int(arg)
		elif opt in ('-j', '--jnum'):
			jnum = int(arg)

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	# 连接数据获取网格信息，包括总数，具有有效POI的网格
	# 固定到北京大小
	GRIDSNUM = 2000

	for dayCount in xrange(0, 87):
		for hourCount in xrange(0, 24):
			judDay = dayCount + dayBase
			judHour = hourCount

			# 从时段 118 开始计算
			if ((judDay - 187) * 24 + judHour) < 118:
				continue

			# @多进程运行程序 START
			jobs = []

			for x in xrange(0, jnum):
				jobs.append(Process(target=processTask, args=(x, city, directory, inum, onum, judDay, judHour, GRIDSNUM, subpath)))
				jobs[x].start()

			for job in jobs:
				job.join()

			# 处理剩余数据进文件
			# 合并操作
			oTime = (judDay - 187) * 24 + judHour
			mergeMatrixs(city, GRIDSNUM, directory, subpath, oTime)
			mergeSmallRecords(city, directory, subpath, oTime)

			# @多进程运行程序 END

	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-unitGridDistribution.log', level=logging.DEBUG)
	main(sys.argv[1:])