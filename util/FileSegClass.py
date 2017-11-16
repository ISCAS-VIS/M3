#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import logging
import os
from util.preprocess import getCityLocs, formatGridID, formatTime


class FileSegByHour(object):
	"""
	多进程计算类：按照日期对文件进行分类重写存储，相关字段预先处理
		:param object: 
	"""
	def __init__(self, PROP):
		super(FileSegByHour, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.DIRECTORY = PROP['DIRECTORY']
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.MAXDAY = PROP['MAXDAY']
		self.MATRIX = [[] for x in xrange(0, PROP['MAXDAY'])]
		self.COUNT = [0 for x in xrange(0, PROP['MAXDAY'])]
		self.SAFECOUNT = PROP['SAFECOUNT']
	
	def run(self):
		logging.info('TASK-%d running...' % (self.INDEX))

		idir = os.path.join(self.DIRECTORY, 'result')
		odir = os.path.join(self.DIRECTORY, 'bj-byday')

		for x in xrange(0, 10000):
			number = self.INDEX + 20 * x
			if number > self.INUM:
				break

			ifilename = 'part-%05d' % number
			logging.info('Job-%d File-%s Operating...' % (self.INDEX, ifilename))
			self.iterateFile(os.path.join(idir, ifilename), odir)

		# 捡完所有漏掉的记录，遍历输入文件
		for x in xrange(0, self.MAXDAY):
			if self.COUNT[x] == 0:
				continue

			ofile = os.path.join(odir, "hres-%d-%d" % (self.INDEX, x))
			with open(ofile, 'ab') as stream:
				stream.write('\n'.join(self.MATRIX[x]) + '\n')
			stream.close()

		logging.info('End Job-%d' % (self.INDEX))

	def iterateFile(self, ifile, opath):
		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				linelist = line.split(',')

				state = linelist[4]
				# 无效 Travel 状态信息
				if state == 'T' and (line[6] == '0' or line[5] == '0' or line[8] == '0' or line[7] == '0'):
					continue

				# 分析日期
				tmp = formatTime(linelist[1])
				ydayCurrent = tmp['day'] - 187
				if ydayCurrent < 0 or ydayCurrent >= self.MAXDAY:
					continue

				# 处理字段
				grid = formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]])
				fromGid = formatGridID(getCityLocs(self.CITY), [linelist[6], linelist[5]])
				toGrid = formatGridID(getCityLocs(self.CITY), [linelist[8], linelist[7]])

				# 计数存储，看情况写入文件
				if self.COUNT[ydayCurrent] == self.SAFECOUNT:
					ofile = os.path.join(opath, "hres-%d-%d" % (self.INDEX, ydayCurrent))
					with open(ofile, 'ab') as stream:
						stream.write('\n'.join(self.MATRIX[ydayCurrent]) + '\n')
					stream.close()

					self.COUNT[ydayCurrent] = 0
					self.MATRIX[ydayCurrent] = []
				else:
					self.COUNT[ydayCurrent] += 1
					newline = "%s,%d,%d,S,0,0" % (line[0], ydayCurrent, grid)
					if state == 'T':
						newline = "%s,%d,%d,T,%d,%d" % (line[0], ydayCurrent, grid, fromGid, toGrid)

					self.MATRIX[ydayCurrent].append(newline)
