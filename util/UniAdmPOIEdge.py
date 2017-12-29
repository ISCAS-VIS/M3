#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [ppedge-[x]]
# from_pid, to_pid, dev_num, rec_num, seg, hour, wday
# 改进后计算脚本，适用于 Admin - POI 下的点边信息聚集计算方案

import os
import gc
import logging


class UniAdmPOIEdge(object):
	"""
	POI Edge
		:param object: 
	"""
	def __init__(self, PROP):
		super(UniAdmPOIEdge, self).__init__()
		
		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.MATRIX = [{} for each in xrange(0, 24)]
		self.poiMap = PROP['poiMap']
		self.DIRECTORY = PROP['DIRECTORY'] 
		self.INPUT_DIR = os.path.join(self.DIRECTORY, 'bj-byday-sg')
		self.OUTPUT_DIR = os.path.join(self.DIRECTORY, PROP['stdoutdir'])
		self.INUM = PROP['INUM']
		self.WDAY = -1

	def run(self):
		logging.info('Starting...')

		# 遍历文件 0 - 86 中一个
		for x in xrange(0, 10000):
			number = self.INDEX + 20 * x
			if number > self.INUM:
				break

			# 结果处理完成重新初始化
			self.DAY = number
			self.MAP = [{} for each in xrange(0, 24)]
			self.LASTREC = [{
				'id': '-1',
				'travel': '-1'
			} for x in xrange(0, 24)]

			ifilename = 'rawdata-%d' % number
			logging.info('Job-%d File-%d Operating...' % (self.INDEX, number))
			self.updateEdge(os.path.join(self.INPUT_DIR, ifilename))

			self.writeData(os.path.join(self.OUTPUT_DIR, 'apedge-%d' % (self.INDEX)))
			self.MAP = []
			self.LASTREC = []
			gc.collect()
	
	def updateEdge(self, ifile):
		resnum = 0
		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				linelist = line.split(',')

				if self.WDAY == -1:
					self.WDAY = int(linelist[3])

				state = linelist[5]
				fromAid = int(linelist[9])
				toGid = int(linelist[8])
				if state == 'S':
					continue
                
				if toGid in self.poiMap:
					toPid = self.poiMap[toGid]
					resnum += 1
					hour = int(linelist[2])
					mapId = "%s,%s" % (fromAid, toPid)
					self.dealOneEdge({
						'id': linelist[0],
						'hour': hour,
						'existidentifier': '%s-%d-%s-%s' % (id, hour, fromAid, toPid),
						'fromAid': fromAid,
						'toPid': toPid,
						'mapId': mapId
					})
		stream.close()
		print "Process %d, day %d, result number %d" % (self.INDEX, self.DAY, resnum)

	def dealOneEdge(self, data):
		"""
		判断处理单条记录函数
			:param self: 
			:param data: 
		"""
		id = data['id']
		mapId = data['mapId']
		hour = data['hour']
		fhour = self.DAY * 24 + data['hour']
		fromAid = data['fromAid']
		toPid = data['toPid']
		existidentifier = data['existidentifier']
		
		# 人未变
		if id == self.LASTREC[hour]['id']:
			# 同一个人新纪录，如果记录相同则不作处理
			if existidentifier != self.LASTREC[hour]['travel']:
				self.LASTREC[hour]['travel'] = existidentifier
				self.updateMap(mapId, hour, [fromAid, toPid, fhour, 1, 0])
		else:
			self.LASTREC[hour] = {
				'id': id,
				'travel': existidentifier
			}
			self.updateMap(mapId, hour, [fromAid, toPid, fhour, 1, 0])
		
		self.MAP[hour][mapId][4] += 1

	def updateMap(self, key, hour, val):
		"""
		根据单条消息更新 MAP, 如果存在则加一，否则插入初始化值
			:param self: 
			:param key: 
			:param hour: 
			:param val: 
		"""
		if key in self.MAP[hour]:
			self.MAP[hour][key][3]  += 1
		else:
			self.MAP[hour][key] = val

	def writeData(self, ofile):
		resArr = []

		with open(ofile, 'ab') as res:
			# 24 时间段
			for hour in xrange(0, 24):
				for key, value in self.MAP[hour].iteritems():
					resArr.append('%s,%s,%d,%d,%d,%d,%d' % (value[0], value[1], value[3], value[4], value[2], hour, self.WDAY))
			
			res.write('\n'.join(resArr) + '\n')
		res.close()