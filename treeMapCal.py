#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# treeMap 计算
# 
# python treeMapCal.py -d /home/joe/Documents/git/fake -p /home/joe/Documents/git/fake -e 0.01 -m 40 [grid]
# [circle]
# 
# line
# python treeMapCal.py -d /datahouse/tao.jiang -p /datahouse/tao.jiang -e 2 -m 10


import sys
import time
import logging
from util.tripFlow.constructTreeMap import ConstructTreeMap

	
def processTask(x, stdindir, stdoutdir, tree_num, search_angle, seed_strength, tree_width, jump_length, seed_unit, grid_dirnum, delta, max_distance): 
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
		'max_distance': max_distance,
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
	print "python treeMapCal.py /datahouse/tripflow/200 /datahouse/tripflow/200 9 0.03 60 0.1 1 3 basic -1 1 9999"


def main(argv):

	[indir, outdir, x, tree_num, search_angle, seed_strength, tree_width, jump_length, seed_unit, grid_dirnum, delta, max_distance] = argv
	x = int(x)
	tree_num = float(tree_num)
	search_angle = int(search_angle)
	seed_strength = float(seed_strength)
	tree_width = int(tree_width)
	jump_length = int(jump_length)
	grid_dirnum = int(grid_dirnum)
	delta = float(delta)
	max_distance = float(max_distance)

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	processTask(x, indir, outdir, tree_num, search_angle, seed_strength, tree_width, jump_length, seed_unit, grid_dirnum, delta, max_distance)

	# @多进程运行程序 END
	ENDTIME = time.time()
	print "END TIME: %s" % ENDTIME
	print "Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0)


if __name__ == '__main__':
	logging.basicConfig(filename='logger-treemapflowcal.log', level=logging.DEBUG)
	main(sys.argv[1:])