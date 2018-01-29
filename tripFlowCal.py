#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# tripFlow 计算

import sys
import time
import logging
import getopt
from util.tripFlow.extractGridEdges import ExtractGridEdges
from util.tripFlow.dbscanTFIntersections import DBScanTFIntersections

			
def processTask(x, eps, min_samples, stdindir, stdoutdir): 
	PROP = {
		'index': x, 
		'IDIRECTORY': stdindir, 
		'ODIRECTORY': stdoutdir
	}
	task = ExtractGridEdges(PROP)
	res = task.run()

	clusterPROP = {
		'index': x, 
		'ODIRECTORY': stdoutdir,
		'res': res,
		'eps': eps,
		'min_samples': min_samples
	}
	clusterTask = DBScanTFIntersections(clusterPROP)
	clusterTask.run()


def usage():
	# /datahouse/zhtan/datasets/VIS-rawdata-region/
	print "python tripFlowCal.py -d /datasets -p /datasets -e 0.01 -m 10"


def main(argv):
	try:
		argsArray = ["help", 'stdindir=', 'stdoutdir', "eps", "min_samples"]
		opts, args = getopt.getopt(argv, "hd:p:e:m:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	stdindir = '/home/tao.jiang/datasets/JingJinJi/records'
	stdoutdir = '/home/tao.jiang/datasets/JingJinJi/records'
	eps, min_samples = 0.01, 10

	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-d", "--stdindir"):
			stdindir = arg
		elif opt in ('-p', '--stdoutdir'):
			stdoutdir = arg
		elif opt in ("-e", "--eps"):
			eps = float(arg)
		elif opt in ('-s', '--sample'):
			min_samples = int(arg)

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	print '''
	===	Cluster Opts	===
	stdindir	= %s
	stdoutdir	= %s
	eps			= %f
	min_samples	= %d
	===	Cluster Opts	===
	''' % (stdindir, stdoutdir, eps, min_samples)
	x = 9
	processTask(x, eps, min_samples, stdindir, stdoutdir)

	# @多进程运行程序 END
	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-tripflowcal.log', level=logging.DEBUG)
	main(sys.argv[1:])