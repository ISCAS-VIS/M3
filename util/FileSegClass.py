#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import numpy as np
import logging
import os
from util.preprocess import getCityLocs, formatGridID, formatTime


class FileSegByHour(object):
    	"""
	多进程计算类：通过给定小时过滤数据，将分属网格、以及两节点间连线的定位记录数/人数计算并存入文件，多个小时数据需要分别遍历所有数据多遍进行处理
		:param object: 
	"""
	def __init__(self, PROP):
		super(FileSegByHour, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.DIRECTORY = PROP['DIRECTORY'] 
		self.SUBPATH = PROP['SUBPATH']
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.DAY = PROP['DAY']
		self.HOUR = PROP['HOUR']
		self.TimeIndex = (self.DAY - 187) * 24 + self.HOUR
	
	def run(self):
		logging.info('TASK-%d running...' % (self.INDEX))

		oname = 'mres-t%02d-ti%d' % (self.INDEX, self.TimeIndex)
		orecsaname = 'rres-t%02d-ti%d' % (self.INDEX, self.TimeIndex)
		idir = os.path.join(self.DIRECTORY, 'result')
		ofile = os.path.join(self.DIRECTORY, self.SUBPATH, oname)

		for x in xrange(0, 10000):
			number = self.INDEX + 20 * x
			if number > self.INUM:
				break

			ifilename = 'part-%05d' % number
			logging.info('Job-%d Task-%d File-%s Operating...' % (self.INDEX, self.TimeIndex, ifilename))
			self.updateDis(os.path.join(idir, ifilename))