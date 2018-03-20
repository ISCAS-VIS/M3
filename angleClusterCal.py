#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# angleCluster 计算

import sys
import time
import logging
from util.tripFlow.AngleClusterInOneGrid import AngleClusterInOneGrid


def processTask(x, stdindir, stdoutdir, eps, min_samples): 
	PROP = {
		'index': x, 
		'IDIRECTORY': stdindir, 
		'ODIRECTORY': stdoutdir,
		'eps': eps,
		'min_samples': min_samples
	}
	task = AngleClusterInOneGrid(PROP)
	task.run()


def usage():
	print "python angleClusterCal.py /datahouse/tripflow/200 /datahouse/tripflow/200 9 0.01 100"


def main(argv):
	[indir, outdir, x, eps, min_samples] = argv
	x = int(x)
	eps = float(eps)
	min_samples = int(min_samples)
	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	processTask(x, indir, outdir, eps, min_samples)

	ENDTIME = time.time()
	print "END TIME: %s" % ENDTIME
	print "Total minutes: %f" % ((ENDTIME-STARTTIME)/60.0)


if __name__ == '__main__':
	logging.basicConfig(filename='logger-angleclustercal.log', level=logging.DEBUG)
	main(sys.argv[1:])