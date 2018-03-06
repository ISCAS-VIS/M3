#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# tripFlow 计算
# 
# python treeMapCal.py -d /home/joe/Documents/git/fake -p /home/joe/Documents/git/fake -e 0.01 -m 40 [grid]
# [circle]
# 
# line
# python treeMapCal.py -d /datahouse/tao.jiang -p /datahouse/tao.jiang -e 2 -m 10


import sys
import time
import logging
import getopt
from util.tripFlow.constructTreeMap import ConstructTreeMap

	
def processTask(x, stdindir, stdoutdir): 
	dataType = 'angle'
	custom_params = {
		'tree_num': 3,
		'search_angle': 60,
		'seed_strength': 0.3,
		'max_curvation': 180,
		'tree_width': 3,
		'jump_length': 3,
		'LngSPLIT': 0.0064,
		'LatSPLIT': 0.005
	}

	PROP = {
		'index': x, 
		'IDIRECTORY': stdindir, 
		'ODIRECTORY': stdoutdir,
		'dataType': dataType,
		'custom_params': custom_params
	}
	task = ConstructTreeMap(PROP)
	task.run()


def usage():
	# /datahouse/zhtan/datasets/VIS-rawdata-region/
	print "python treeMapCal.py -d /datasets -p /datasets -x 9"


def main(argv):
	try:
		argsArray = ["help", 'stdindir=', 'stdoutdir', "index="]
		opts, args = getopt.getopt(argv, "hd:p:x:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	stdindir = '/home/tao.jiang/datasets/JingJinJi/records'
	stdoutdir = '/home/tao.jiang/datasets/JingJinJi/records'
	x = 9

	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-d", "--stdindir"):
			stdindir = arg
		elif opt in ('-p', '--stdoutdir'):
			stdoutdir = arg
		elif opt in ('-x', '--index'):
			x = int(arg)

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME
	
	processTask(x, stdindir, stdoutdir)

	# @多进程运行程序 END
	ENDTIME = time.time()
	print "END TIME: %s" % ENDTIME
	print "Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0)


if __name__ == '__main__':
	logging.basicConfig(filename='logger-tripflowcal.log', level=logging.DEBUG)
	main(sys.argv[1:])