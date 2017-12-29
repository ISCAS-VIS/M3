#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Format:
# 1 id: 'String',
# 2 seg: 'Number',
# 3 hour: 'Number', // 0-23
# 4 wday: 'Number', // 0-6
# 5 gid: 'Number',
# 6 state: 'S/T',
# 7 admin: 'Number', // 1-16
# 8 from_gid: 'Number',
# 9 to_gid: 'Number',
# 10 from_aid: 'Number',
# 11 to_aid: 'Number'
# 
# Output Format:
# [hares-j[x]]
# nid, lat, lng, dev_num, rec_num, seg
# 
# 改进后计算脚本，适用于 0.0005 精度 Grid 映射 POI 的聚集数据计算方案

import os
import gc
import logging


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
		self.INPUT_DIR = os.path.join(self.DIRECTORY, 'bj-byday-sg')
		self.OUTPUT_DIR = os.path.join(self.DIRECTORY, PROP['SUBOPATH'])
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.DAY = -1
		self.poiMap = PROP['poiMap']

	def run(self):
		logging.info('TASK-%d running...' % (self.INDEX))

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

			ifilename = 'rawdata-%d' % number
			logging.info('Job-%d File-%d Operating...' % (self.INDEX, number))
			self.updateDis(os.path.join(self.INPUT_DIR, ifilename))
		
			# 结果写进文件
			# # MATRIX
			self.writeDayObjecttoFile()
			self.MAP = []
			self.LASTREC = []
			gc.collect()

	def genPOIMapObj(self):
		res = {}
		for key in self.poiMap:
			val = self.poiMap[key]
			res[val] = [val, 0, 0]
		return res
    		
	def updateDis(self, ifile):
		resnum = 0

		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				linelist = line.split(',')

				state = linelist[3]
				if state == 'T':
					continue
                
				# print linelist[2]
				gid = int(linelist[2])
				if gid in self.poiMap:
					resnum += 1
					self.dealPointState({
						'id': linelist[0],
						'hour': int(linelist[2]),
						'poi': self.poiMap[gid]
					})
		stream.close()
		print "Process %d, day %d, result number %d" % (self.INDEX, self.DAY, resnum)

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

	def writeDayObjecttoFile(self):
		"""
		将进程中单天所有时间单位的 POI 分布数据转化为字符串存储进文件
		"""
		data = self.MAP
		with open(os.path.join(self.OUTPUT_DIR, 'ppoint-j%d' % (self.INDEX)), 'ab') as res:
			# 24 时间段
			for x in xrange(0, 24):
				resString = []
				seg = self.DAY * 24 + x

				# 网格数遍历
				for i in data[x]:
					oneRec = data[x][i]

					# 只记录有人定位的有效网格
					if oneRec[1] != 0:
						singleRes = "%s,%d,%d,%d" % (oneRec[0], oneRec[1], oneRec[2], seg)
						resString.append(singleRes)

				res.write('\n'.join(resString) + '\n')
		res.close()