#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import sys
import time
import logging
import getopt
from multiprocessing import Process
from util.preprocess import mergeLargeRecords
from util.FileSegClass import FileSegByHour

			
def processTask(x, city, directory, inum, onum, MAXDAY, SAFECOUNT): 
	PROP = {
		'INDEX': x, 
		'CITY': city, 
		'DIRECTORY': directory, 
		'INUM': inum, 
		'ONUM': onum,
		'MAXDAY': MAXDAY,
		'SAFECOUNT': SAFECOUNT
	}
	task = FileSegByHour(PROP)
	task.run()


def usage():
	pass


def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hc:d:i:o:j:", ["help", "city=", 'directory=', 'inum=', 'onum=', 'jnum='])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory, inum, onum, jnum = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records', 3999, 20, 20
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

	# @多进程运行程序 START
	jobs = []

	for x in xrange(0, jnum):
		jobs.append(Process(target=processTask, args=(x, city, directory, inum, onum, 87, 300000)))
		jobs[x].start()

	for job in jobs:
		job.join()

	# 处理剩余数据进文件
	# 合并操作
	mergeLargeRecords(city, directory, 'bj-byday', 87)

	# @多进程运行程序 END

	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-segrawdata.log', level=logging.DEBUG)
	main(sys.argv[1:])