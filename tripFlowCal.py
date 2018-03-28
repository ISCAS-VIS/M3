#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# tripFlow 计算
# 
# python tripFlowCal.py -d /home/joe/Documents/git/fake -p /home/joe/Documents/git/fake -e 0.01 -m 40 [grid]
# [circle]
# 
# line
# python tripFlowCal.py -d /datahouse/tao.jiang -p /datahouse/tao.jiang -e 2 -m 10


import sys
import time
import logging
import getopt
from util.tripFlow.extractGridEdges import ExtractGridEdges
from util.tripFlow.dbscanTFIntersections import DBScanTFIntersections
from util.tripFlow.mergeClusterEdges import MergeClusterEdges
from util.tripFlow.lineTFIntersections import LineTFIntersections

			
def processTask(x, eps, K, delta, stdindir, stdoutdir): 
	subfix = ".2f" % (delta)
	PROP = {
		'index': x, 
		'delta': delta,
		'IDIRECTORY': stdindir, 
		'ODIRECTORY': stdoutdir,
		'subfix': subfix
	}
	task = ExtractGridEdges(PROP)
	res = task.run()
	
	count = res['count']
	min_samples = int(count / K) if count > K else 1

	resByDir = res['res']['resByDir']
	resByCate = res['res']['resByCate']
	dataType = 'angle'  # 确定是按照方向聚类还是角度聚类 direction, category
	EPS_INTERVAL = 0.001 if dataType == 'direction' else 0.4

	clusterofilename = ''
	iterationTimes = 0

	while (True):
		if (iterationTimes == 50):
			eps -= EPS_INTERVAL*50
			min_samples -= 5
			iterationTimes = 0
		
		clusterPROP = {
			'index': x, 
			'ODIRECTORY': stdoutdir,
			'resByDir': resByDir,
			'resByCate': resByCate,
			'resByAng': resByCate,
			'dataType': dataType,
			'eps': eps,
			'min_samples': min_samples,
			'subfix': subfix
		}
		print '''
===	Cluster Parameters	===
index	= %d
stdindir	= %s
stdoutdir	= %s
eps		= %f
min_samples	= %d
===	Cluster Parameters	===
''' % (x, stdindir, stdoutdir, eps, min_samples)

		# 角度聚类单独处理
		if dataType == 'angle':
			clusterTask = LineTFIntersections(clusterPROP)
			noiseRate, clusterofilename = clusterTask.run()
			break

		clusterTask = DBScanTFIntersections(clusterPROP)
		noiseRate, clusterofilename = clusterTask.run()

		if noiseRate <= 0.5:
			break
		else:
			eps += EPS_INTERVAL
			iterationTimes += 1

	mergePROP = {
		'index': x, 
		'IDIRECTORY': stdindir, 
		'ODIRECTORY': stdoutdir,
		'dataType': dataType,
		'subfix': subfix
	}
	mergeTask = MergeClusterEdges(mergePROP)
	mergeTask.run()


def usage():
	# /datahouse/zhtan/datasets/VIS-rawdata-region/
	print "python tripFlowCal.py -d /datasets -p /datasets -e 2 -x 18 -k 24000"


def main(argv):
	try:
		argsArray = ["help", 'stdindir=', 'stdoutdir', "eps", "min_samples", "index=", "delta", "kval"]
		opts, args = getopt.getopt(argv, "hd:p:e:m:x:t:k:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	stdindir = '/home/tao.jiang/datasets/JingJinJi/records'
	stdoutdir = '/home/tao.jiang/datasets/JingJinJi/records'
	eps = 0.01
	# min_samples = 10
	delta = -1.0
	x = 9
	K = 24000

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
		# elif opt in ('-m', '--min_samples'):
		# 	min_samples = int(arg)
		elif opt in ('-x', '--index'):
			x = int(arg)
		elif opt in ('-t' '--delta'):
			delta = float(arg)
		elif opt in ('-k' '--kval'):
			K = int(arg)				

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	# print '''
	# ===	Cluster Opts	===
	# stdindir	= %s
	# stdoutdir	= %s
	# eps		= %f
	# min_samples	= %d
	# ===	Cluster Opts	===
	# ''' % (stdindir, stdoutdir, eps, min_samples)

	processTask(x, eps, K, delta, stdindir, stdoutdir)

	# @多进程运行程序 END
	ENDTIME = time.time()
	print "END TIME: %s" % ENDTIME
	print "Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0)


if __name__ == '__main__':
	logging.basicConfig(filename='logger-tripflowcal.log', level=logging.DEBUG)
	main(sys.argv[1:])