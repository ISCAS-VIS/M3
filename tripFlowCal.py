#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# tripFlow 计算

import sys
import os
import time
import logging
import getopt
from multiprocessing import Process
from util.tripFlow.extractGridEdges import ExtractGridEdges

			
def processTask(x, stdindir, stdoutdir): 
	PROP = {
		'index': x, 
		'IDIRECTORY': stdindir, 
		'ODIRECTORY': stdoutdir
	}
	task = ExtractGridEdges(PROP)
	task.run()


def usage():
	# /datahouse/zhtan/datasets/VIS-rawdata-region/
	print "python -d /datasets -p /datasets -i 3999"


def main(argv):
	try:
		argsArray = ["help", "city=", 'stdindir=', 'inum=', 'onum=', 'jnum=', 'stdoutdir']
		opts, args = getopt.getopt(argv, "hc:d:i:o:j:p:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, stdindir, inum, onum, jnum = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records', 3999, 20, 20
	stdoutdir = '/home/tao.jiang/datasets/JingJinJi/records'
	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-c", "--city"):
			city = arg
		elif opt in ("-d", "--stdindir"):
			stdindir = arg
		elif opt in ('-i', '--inum'):
			inum = int(arg)
		elif opt in ('-o', '--onum'):
			onum = int(arg)
		elif opt in ('-j', '--jnum'):
			jnum = int(arg)
		elif opt in ('-p', '--stdoutdir'):
			stdoutdir = arg

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	# @多进程运行程序 START
	jobs = []

	for x in xrange(0, jnum):
		jobs.append(Process(target=processTask, args=(x, stdindir, stdoutdir)))
		jobs[x].start()

	for job in jobs:
		job.join()

	# 处理剩余数据进文件

	# @多进程运行程序 END
	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-segrawdata.log', level=logging.DEBUG)
	main(sys.argv[1:])