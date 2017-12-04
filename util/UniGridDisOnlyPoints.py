#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [hares-j[x]]
# nid, lat, lng, dev_num, rec_num, seg
# 
# 改进后计算脚本，适用于 0.003 精度 Grid 映射 POI 的聚集数据计算方案

import os
import gc
import logging
from util.preprocess import writeDayMatrixtoFile


class UniGridDisOnlyPoints(object):
	"""
	多进程计算类：输入分天的处理后数据，将网格内的定位记录数/人数计算并存入文件，一个进程执行一次负责一天24小时时间段的数据处理，结果增量输入至文件，最后多进程执行情况下需要做合并操作
		:param object: 
	"""
	def __init__(self, PROP):
		super(UniGridDisOnlyPoints, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.DIRECTORY = PROP['DIRECTORY'] 
		self.SUBOPATH = PROP['SUBOPATH']
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.DAY = -1
		self.GRIDSNUM = PROP['GRIDSNUM']

	def run(self):
		logging.info('TASK-%d running...' % (self.INDEX))

		idir = os.path.join(self.DIRECTORY, 'bj-byday')
		odir = os.path.join(self.DIRECTORY, self.SUBOPATH)

		for x in xrange(0, 10000):
			number = self.INDEX + 20 * x
			if number > self.INUM:
				break

			# 结果处理完成重新初始化
			self.DAY = number
			self.MATRIX = [[[x, 0, 0] for x in xrange(0, self.GRIDSNUM)] for e in xrange(0, 24)]  # index, people, number
			self.LASTREC = [{
				'id': -1,
				'grid': []
			} for x in xrange(0, 24)]

			ifilename = 'hares-%d' % number
			logging.info('Job-%d File-%d Operating...' % (self.INDEX, number))
			self.updateDis(os.path.join(idir, ifilename))
		
			# 结果写进文件
			# # MATRIX
			writeDayMatrixtoFile(self.INDEX, self.CITY, self.MATRIX, odir, self.DAY)
			self.MATRIX = []
			self.LASTREC = []
			gc.collect()

	def updateDis(self, ifile):
		resnum = 0

		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				resnum += 1
				linelist = line.split(',')

				state = linelist[3]
				if state == 'T':
					continue

				self.dealPointState({
					'id': linelist[0],
					'hour': int(linelist[1]) % 23,
					'grid': int(linelist[2]),
				})
		stream.close()

	def dealPointState(self, data):
		grid = data['grid']
		id = data['id']
		hour = data['hour']

		# stay 状态更新
		if id == self.LASTREC[hour]['id']:
			if grid not in self.LASTREC[hour]['grid']:
				self.LASTREC[hour]['grid'].append(grid)
				self.MATRIX[hour][grid][1] += 1
		else:
			self.LASTREC[hour]['id'] = id
			self.LASTREC[hour]['grid'] = [grid]
			self.MATRIX[hour][grid][1] += 1

		self.MATRIX[hour][grid][2] += 1
