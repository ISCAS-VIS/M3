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
# import getopt
from util.tripFlow.constructTreeMap import ConstructTreeMap

	
def processTask(x, stdindir, stdoutdir, tree_num, search_angle, seed_strength, tree_width, jump_length, seed_unit, grid_dirnum, delta): 
	dataType = 'angle'
	custom_params = {
		'tree_num': tree_num,
		'search_angle': search_angle,
		'seed_strength': seed_strength,
		'max_curvation': 90,
		'tree_width': tree_width,
		'jump_length': jump_length,
		"seed_unit": seed_unit,
		"grid_dirnum": grid_dirnum,
		'LngSPLIT': 0.0064,
		'LatSPLIT': 0.005,
		'delta': delta
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
	# print "python treeMapCal.py -d /dir -p /dir -x 9 -n 0.03 -a 60 -s 0.3 -w 3 -l 3"

	# 'stdindir='
	# 'stdoutdir'
	# "index="
	# "tree_num"
	# "search_angle"
	# "seed_strength"
	# "tree_width"
	# "jump_length"
	# "seed_unit"
	# "grid_dirnum"
	# "delta"
	print "python treeMapCal.py /datahouse/tripflow/200 /datahouse/tripflow/200 9 0.03 60 0.1 1 3 basic -1 1"


def main(argv):
	# try:
	# 	argsArray = ["help", 'stdindir=', 'stdoutdir', "index=", "tree_num", "search_angle", "seed_strength", "tree_width", "jump_length"]
	# 	opts, args = getopt.getopt(argv, "hd:p:x:n:a:s:w:l:", argsArray)
	# except getopt.GetoptError as err:
	# 	print str(err)
	# 	usage()
	# 	sys.exit(2)

	[indir, outdir, x, tree_num, search_angle, seed_strength, tree_width, jump_length, seed_unit, grid_dirnum, delta] = argv
	x = int(x)
	tree_num = float(tree_num)
	search_angle = int(search_angle)
	seed_strength = float(seed_strength)
	tree_width = int(tree_width)
	jump_length = int(jump_length)
	grid_dirnum = int(grid_dirnum)
	delta = float(delta)

	# stdindir = '/home/tao.jiang/datasets/JingJinJi/records'
	# stdoutdir = '/home/tao.jiang/datasets/JingJinJi/records'
	# x = 9
	# tree_num, search_angle, seed_strength, tree_width = 30, 60, 0.3, 3
	# # topN = 100
	# jump_length = 3

	# for opt, arg in opts:
	# 	if opt == '-h':
	# 		usage()
	# 		sys.exit()
	# 	elif opt in ("-d", "--stdindir"):
	# 		stdindir = arg
	# 	elif opt in ('-p', '--stdoutdir'):
	# 		stdoutdir = arg
	# 	elif opt in ('-x', '--index'):
	# 		x = int(arg)
	# 	elif opt in ('-n', '--tree_num'):
	# 		tree_num = int(arg)
	# 	elif opt in ('-a', '--search_angle'):
	# 		search_angle = int(arg)
	# 	elif opt in ('-s', '--seed_strength'):
	# 		seed_strength = float(arg)
	# 	elif opt in ('-w', '--tree_width'):
	# 		tree_width = int(arg)
	# 	elif opt in ('-l', '--jump_length'):
	# 		jump_length = int(arg)

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	processTask(x, indir, outdir, tree_num, search_angle, seed_strength, tree_width, jump_length, seed_unit, grid_dirnum, delta)

	# @多进程运行程序 END
	ENDTIME = time.time()
	print "END TIME: %s" % ENDTIME
	print "Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0)


if __name__ == '__main__':
	logging.basicConfig(filename='logger-treemapflowcal.log', level=logging.DEBUG)
	main(sys.argv[1:])