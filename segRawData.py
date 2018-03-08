#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# 引用 FileSegByHour 类切分原始文件，并合并最终结果至按天分的子文件中

import sys
import os
import time
import logging
import getopt
from multiprocessing import Process
from util.FileSegClass import FileSegByHour

			
def processTask(x, city, stdindir, stdoutdir, inum, onum, MAXDAY, SAFECOUNT): 
	PROP = {
		'INDEX': x, 
		'CITY': city, 
		'IDIRECTORY': stdindir, 
		'ODIRECTORY': stdoutdir,
		'INUM': inum, 
		'ONUM': onum,
		'MAXDAY': MAXDAY,
		'SAFECOUNT': SAFECOUNT
	}
	task = FileSegByHour(PROP)
	task.run()


def mergeLargeRecords(city, baseurl, count):
	"""
	通过整个文件读取的方式合并记录数
		:param city: 
		:param baseurl: 
		:param count: 
	"""
	
	for x in xrange(0, count):
		with open(os.path.join(baseurl, 'rawdata-%d' % (x)), 'ab') as output:
			for jobId in xrange(0, 20):
				with open(os.path.join(baseurl, 'rawdata-j%d-%d' % (jobId, x)), 'rb') as s:
					output.write(s.read())
				s.close()
		output.close()


def usage():
	# /datahouse/zhtan/datasets/VIS-rawdata-region/
	print "python -d /datasetsURL -p /datahouse/tao.jiang -i 3999"


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
		jobs.append(Process(target=processTask, args=(x, city, stdindir, stdoutdir, inum, onum, 87, 300000)))
		jobs[x].start()

	for job in jobs:
		job.join()

	# 处理剩余数据进文件
	# 合并操作
	path = os.path.join(stdoutdir, 'bj-byday-tf')
	mergeLargeRecords(city, path, 87)

	# @多进程运行程序 END
	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-segrawdata.log', level=logging.DEBUG)
	main(sys.argv[1:])