#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [hares-j[x]]
# nid, lat, lng, dev_num, rec_num, seg
# 
# 改进后计算脚本，适用于 0.0005 精度空间映射 POI 的数据计算

import os
import gc
import logging
from util.preprocess import writeDayObjecttoFile


class UniPOIDisBasic(object):
	"""
	多进程计算类：输入分天的处理后数据，将 POI 内的定位记录数/人数计算并存入文件，一个进程执行一次负责一天24小时时间段的数据处理，结果增量输入至文件，最后多进程执行情况下需要做合并操作
		:param object: 
	"""
	def __init__(self, PROP):
		super(UniPOIDisBasic, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.DIRECTORY = PROP['DIRECTORY'] 
		self.SUBOPATH = PROP['SUBOPATH']
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.DAY = -1
		self.poiMap = PROP['poiMap']

	def run(self):
		logging.info('TASK-%d running...' % (self.INDEX))

		idir = os.path.join(self.DIRECTORY, 'bj-byday-sg')
		odir = os.path.join(self.DIRECTORY, self.SUBOPATH)

		for x in xrange(0, 10000):
			number = self.INDEX + 20 * x
			if number > self.INUM:
				break

			# 结果处理完成重新初始化
			self.DAY = number
			self.MAP = [self.genPOIMapObj() for e in xrange(0, 24)]
			self.LASTREC = [{
				'id': -1,
				'poi': []
			} for x in xrange(0, 24)]

			ifilename = 'hares-%d' % number
			logging.info('Job-%d File-%d Operating...' % (self.INDEX, number))
			self.updateDis(os.path.join(idir, ifilename))
		
			# 结果写进文件
			# # MATRIX
			writeDayObjecttoFile(self.INDEX, self.CITY, self.MAP, odir, self.DAY)
			self.MAP = []
			self.LASTREC = []
			gc.collect()

	def genPOIMapObj(self):
		res = {}
		for key in self.poiMap:
			res[key] = [key, 0, 0]
		return res
    		
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
                
                if linelist[2] in self.poiMap:
                    self.dealPointState({
                        'id': linelist[0],
                        'hour': int(linelist[1]) % 23,
                        'poi': self.poiMap[linelist[2]]
    				})
		stream.close()

	def dealPointState(self, data):
		id = data['id']
		hour = data['hour']
		poi = data['poi']

		# stay 状态更新
		# 判断此记录是否与上次一致
		if id == self.LASTREC[hour]['id']:
			# 判断 poi ID 在指定时段中是否出现过
			if poi not in self.LASTREC[hour]['poi']:
				self.LASTREC[hour]['poi'].append(poi)
				self.MAP[hour][poi][1] += 1  # index, people, number
		else:
			self.LASTREC[hour]['id'] = id
			self.LASTREC[hour]['poi'] = [poi]
			self.MAP[hour][poi][1] += 1

		self.MAP[hour][poi][2] += 1
