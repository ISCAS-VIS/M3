#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 测试所有时段同时处理平均分布情况下最多容纳多少行数据同时在内存

import numpy as np
from multiprocessing import Process

def processTask():
	MATRIX = [['j, 3.33, 3.33, 3.33, 3.33, 3.33, 3.33' for j in xrange(1000)] for x in xrange(0, 2088)]

	eachNum = 1000
	for t in xrange(0, 100000):
		for i in xrange(0, 2088):
			MATRIX[x].append("[j, 3.33, 3.33, 3.33, 3.33, 3.33, 3.33]")
		eachNum += 1
		print "current length of each time seg %d" % (eachNum)


if __name__ == '__main__':
	MATRIX = np.array([np.array([x, 0, 0]) for x in xrange(0, 800000)])

	jobs = []

	for x in xrange(0, 20):
		jobs.append(Process(target=processTask))
		jobs[x].start()

	for job in jobs:
		job.join()