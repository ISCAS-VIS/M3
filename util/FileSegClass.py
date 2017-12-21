#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Format:
# id, time, lat, lng, state, sid, admin
# 
# Output Format:
# [hares-x]
# id, seg, hour, wday, gid, state, admin, from_gid, to_gid, from_aid, to_aid

import logging
import os
from util.preprocess import getCityLocs, formatGridID, formatTime
from util.preprocess import getAdminNumber


class FileSegByHour(object):
	"""
	多进程计算类：按照日期对文件进行分类重写存储，相关字段预先处理，需同时指定基础输入目录和输出目录
		:param object: 
	"""
	def __init__(self, PROP):
		super(FileSegByHour, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.INPUT_PATH = PROP['IDIRECTORY']
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'bj-byday-sg')
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.MAXDAY = PROP['MAXDAY']
		self.MATRIX = [[] for x in xrange(0, PROP['MAXDAY'])]
		self.COUNT = [0 for x in xrange(0, PROP['MAXDAY'])]
		self.SAFECOUNT = PROP['SAFECOUNT']

		self.currentDatasets = {
			'fromLatLng': [0, 0],
			'fromAdmin': '',
			'toLatLng': [0, 0],
			'toAdmin': '',
			'data': [],
			'stateId': 0
		}
	
	def run(self):
		logging.info('TASK-%d running...' % (self.INDEX))

		for x in xrange(0, 10000):
			number = self.INDEX + 20 * x
			if number > self.INUM:
				break

			ifilename = 'part-%05d' % number
			logging.info('Job-%d File-%s Operating...' % (self.INDEX, ifilename))
			self.iterateFile(os.path.join(self.INPUT_PATH, ifilename))

		# 捡完所有漏掉的记录，遍历输入文件
		for x in xrange(0, self.MAXDAY):
			if self.COUNT[x] == 0:
				continue

			ofile = os.path.join(self.OUTPUT_PATH, "rawdata-j%d-%d" % (self.INDEX, x))
			with open(ofile, 'ab') as stream:
				stream.write('\n'.join(self.MATRIX[x]) + '\n')
			stream.close()

		logging.info('End Job-%d' % (self.INDEX))

	def iterateFile(self, ifile):
		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				linelist = line.split(',')

				state = linelist[4]
				
				if state == 'U' or line == '':
					continue

				# 分析日期
				tmp = formatTime(linelist[1])
				ydayCurrent = tmp['yday'] - 187
				
				wday = tmp['wday']
				hour = tmp['hour']
				seg = ydayCurrent * 24 + hour
				
				if ydayCurrent < 0 or ydayCurrent >= self.MAXDAY:
					continue
				
				id = linelist[0]
				admin = getAdminNumber(linelist[6])
				gid = formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]])
				newLinePreStr = "%s,%d,%d,%d,%d" % (id, seg, hour, wday, gid)

				# 分状态处理原始数据
				# S 时 currentDatasets 数据重置（重置前查看是否需要转存上一段 T 的数据）， T 时对比当前 from 是否为初始状态，若为初始状态当前数据存在 from，否则存在 to
				if state == 'T':
					if self.currentDatasets['fromLatLng'][0] == 0:
						self.currentDatasets['fromLatLng'] = [linelist[3], linelist[2]]
						self.currentDatasets['fromAdmin'] = linelist[6]
						self.currentDatasets['stateId'] = linelist[5]
					else:
						# 判断 stateId 是否一致
						if linelist[5] != self.currentDatasets['stateId']:
							self.updLastTravelRecs()
						else:
							self.currentDatasets['toLatLng'] = [linelist[3], linelist[2]]
							self.currentDatasets['toAdmin'] = linelist[6]
					tmp = "%s,T,%d" % (newLinePreStr, admin)
					self.currentDatasets['data'].append([tmp, ydayCurrent])
				else:
					self.updLastTravelRecs()

					newline = "%s,S,%d,0,0,0,0" % (newLinePreStr, admin)
					self.COUNT[ydayCurrent] += 1
					self.MATRIX[ydayCurrent].append(newline)

					self.checkWriteOpt(ydayCurrent)
				
		stream.close()

	def checkWriteOpt(self, ydayCurrent):
		# 计数存储，看情况写入文件
		if self.COUNT[ydayCurrent] >= self.SAFECOUNT:
			ofile = os.path.join(self.OUTPUT_PATH, "rawdata-j%d-%d" % (self.INDEX, ydayCurrent))
			with open(ofile, 'ab') as stream:
				stream.write('\n'.join(self.MATRIX[ydayCurrent]) + '\n')
			stream.close()

			self.COUNT[ydayCurrent] = 0
			self.MATRIX[ydayCurrent] = []

	def updLastTravelRecs(self):
		if self.currentDatasets['fromAdmin'] == '':
			return 0
		# 		
		fromGid = formatGridID(getCityLocs(self.CITY), self.currentDatasets['fromLatLng'])
		toGid = formatGridID(getCityLocs(self.CITY), self.currentDatasets['toLatLng'])
		fromAdmin = getAdminNumber(self.currentDatasets['fromAdmin'])
		toAdmin = getAdminNumber(self.currentDatasets['toAdmin'])
		supStr = "%d,%d,%d,%d" % (fromGid, toGid, fromAdmin, toAdmin)

		# 遍历记录
		for each in self.currentDatasets['data']:
			ydayCurrent = each[1]
			newline = "%s,%s" % (each[0], supStr)

			self.COUNT[ydayCurrent] += 1
			self.MATRIX[ydayCurrent].append(newline)
			self.checkWriteOpt(ydayCurrent)

		# 重置
		self.currentDatasets['fromLatLng'] = [0, 0]
		self.currentDatasets['fromAdmin'] = ''
		self.currentDatasets['data'] = []