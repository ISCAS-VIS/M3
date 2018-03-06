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

	
def processTask(x, stdindir, stdoutdir, tree_num, search_angle, seed_strength, tree_width): 
	dataType = 'angle'
	custom_params = {
		'tree_num': tree_num,
		'search_angle': search_angle,
		'seed_strength': seed_strength,
		'max_curvation': 180,
		'tree_width': tree_width,
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
	print "python treeMapCal.py -d /dir -p /dir -x 9 -n 30 -a 60 -s 0.3 -w 3"


def main(argv):
	try:
		argsArray = ["help", 'stdindir=', 'stdoutdir', "index=", "tree_num", "search_angle", "seed_strength", "tree_width"]
		opts, args = getopt.getopt(argv, "hd:p:x:n:a:s:w:", argsArray)
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	stdindir = '/home/tao.jiang/datasets/JingJinJi/records'
	stdoutdir = '/home/tao.jiang/datasets/JingJinJi/records'
	x = 9
	tree_num, search_angle, seed_strength, tree_width = 30, 60, 0.3, 3

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
		elif opt in ('-n', '--tree_num'):
			tree_num = int(arg)
		elif opt in ('-a', '--search_angle'):
			search_angle = int(arg)
		elif opt in ('-s', '--seed_strength'):
			seed_strength = float(arg)
		elif opt in ('-w', '--tree_width'):
			tree_width = int(arg)

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	processTask(x, stdindir, stdoutdir, tree_num, search_angle, seed_strength, tree_width)

	# @多进程运行程序 END
	ENDTIME = time.time()
	print "END TIME: %s" % ENDTIME
	print "Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0)


if __name__ == '__main__':
	logging.basicConfig(filename='logger-treemapflowcal.log', level=logging.DEBUG)
	main(sys.argv[1:])