#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [rares-at]
# from_nid, to_nid, dev_num, rec_num, seg
# [mares-at]
# nid, lat, lng, dev_num, rec_num, seg
# 
# 初始计算脚本，适用于空间精度 0.05 的划分结构

import os
import logging
import numpy as np
from util.preprocess import getCityLocs, formatGridID, formatTime
from util.preprocess import writeMatrixtoFile, writeObjecttoFile


class UniGridDisBasic(object):
	"""
	多进程计算类：通过给定小时过滤数据，将分属网格、以及两节点间连线的定位记录数/人数计算并存入文件，多个小时数据需要分别遍历所有数据多遍进行处理
		:param object: 
	"""
	def __init__(self, PROP):
		super(UniGridDisBasic, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.DIRECTORY = PROP['DIRECTORY'] 
		self.SUBPATH = PROP['SUBPATH']
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.DAY = PROP['DAY']
		self.HOUR = PROP['HOUR']
		self.TimeIndex = (self.DAY - 187) * 24 + self.HOUR
		self.GRIDSNUM = PROP['GRIDSNUM']
		self.MATRIX = np.array([np.array([x, 0, 0]) for x in xrange(0, PROP['GRIDSNUM'])])  # index, people, number
		self.RECS = {}  # fromgid, togid, people, number
		self.LASTREC = {
			'id': -1,
			'grid': [],
			'travel': ''
		}

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
		
		# 结果写进文件
		# MATRIX
		writeMatrixtoFile(self.CITY, self.MATRIX, ofile, True)
		# RECORDS
		writeObjecttoFile(self.RECS, os.path.join(self.DIRECTORY, self.SUBPATH, orecsaname))

	def updateDis(self, ifile):
		# 
		resnum = 0
		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				resnum += 1
				linelist = line.split(',')

				grid = formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]])
				fromGid = formatGridID(getCityLocs(self.CITY), [linelist[6], linelist[5]])
				toGrid = formatGridID(getCityLocs(self.CITY), [linelist[8], linelist[7]])
				state = linelist[4]

				# 无效 Travel 状态信息
				if state == 'T' and (line[6] == '0' or line[5] == '0' or line[8] == '0' or line[7] == '0'):
					continue
	
				tmp = formatTime(linelist[1])
				ydayCurrent = tmp['day']
				hourCurrent = tmp['hour']

				if ydayCurrent == self.DAY and hourCurrent == self.HOUR:
					self.dealPointState({
						'id': linelist[0],
						'state': state, 
						'day': ydayCurrent,
						'grid': grid, 
						'fromGrid': fromGid, 
						'toGrid': toGrid
					})
		stream.close()
	
	def dealPointState(self, data):
		"""
		将当前记录更新到 distribution 以及存在的旅行记录更新到出行轨迹上
			:param self: 
			:param data: 
		"""
		grid = data['grid']
		id = data['id']
		if data['state'] == 'S':
			# stay 状态更新
			if id == self.LASTREC['id']:
				if grid not in self.LASTREC['grid']:
					self.LASTREC['grid'].append(grid)
					self.MATRIX[grid][1] += 1
			else:
				self.LASTREC['id'] = id
				self.LASTREC['grid'] = [grid]
				self.MATRIX[grid][1] += 1

			self.MATRIX[grid][2] += 1
		elif data['state'] == 'T':
			day = data['day']
			fromGrid = data['fromGrid']
			toGrid = data['toGrid']
			lastidentifier = '%s-%d-%d-%d' % (id, day, fromGrid, toGrid)
			existidentifier = '%d,%d' % (fromGrid, toGrid)

			if existidentifier in self.RECS:
				if lastidentifier != self.LASTREC['travel']:
					self.LASTREC['travel'] = lastidentifier
					self.RECS[existidentifier][2] += 1
				self.RECS[existidentifier][3] += 1
			else:
				self.LASTREC['travel'] = lastidentifier
				self.RECS[existidentifier] = [fromGrid, toGrid, 1, 1, self.TimeIndex]

