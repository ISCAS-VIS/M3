#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [ppedge-[x]]
# from_pid, to_pid, dev_num, rec_num, seg

import os
import gc
import logging


class UniPOIEdgeBasic(object):
	"""
	POI Edge
		:param object: 
	"""
	def __init__(self, PROP):
		super(UniPOIEdgeBasic, self).__init__()
		
		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.MATRIX = [{} for each in xrange(0, 24)]
		self.poiMap = PROP['poiMap']
		self.DIRECTORY = PROP['DIRECTORY'] 
		self.SUBOPATH = PROP['SUBOPATH']
		self.INUM = PROP['INUM']

	def run(self):
		logging.info('Starting...')

		# 遍历文件 0 - 86 中一个
		idir = os.path.join(self.DIRECTORY, 'bj-byday-sg')
		odir = os.path.join(self.DIRECTORY, self.SUBOPATH)

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

			ifilename = 'hares-%d' % number
			logging.info('Job-%d File-%d Operating...' % (self.INDEX, number))
			self.updateEdge(os.path.join(idir, ifilename))

			self.writeData(os.path.join(odir, 'ppedge-%d' % (number)))
			self.MAP = []
			self.LASTREC = []
			gc.collect()
	
	def updateEdge(self, ifile):
		resnum = 0
		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				linelist = line.split(',')

				state = linelist[3]
				fromGrid = int(linelist[4])
				toGrid = int(linelist[5])
				invalidTState = state == 'T' and (fromGrid == 0 or toGrid == 0)
				if state == 'S' or invalidTState:
					continue
                
				linelist[2] = int(linelist[2])
				if fromGrid in self.poiMap and toGrid in self.poiMap:
					fromPid = self.poiMap[fromGrid]
					toPid = self.poiMap[toGrid]
					resnum += 1
					hour = int(linelist[1]) % 24
					mapId = "%s,%s" % (fromPid, toPid)
					self.dealOneEdge({
						'id': linelist[0],
						'hour': hour,
						'existidentifier': '%s-%d-%s-%s' % (id, hour, fromPid, toPid),
						'fromPid': fromPid,
						'toPid': toPid,
						'mapId': mapId
					})
		stream.close()
		print "Process %d, day %d, result number %d" % (self.INDEX, self.DAY, resnum)

	def dealOneEdge(self, data):
		id = data['id']
		mapId = data['mapId']
		hour = data['hour']
		fromPid = data['fromPid']
		toPid = data['toPid']
		existidentifier = data['existidentifier']
		
		# 人未变
		if id == self.LASTREC[hour]['id']:
			# 同一个人新纪录，如果记录相同则不作处理
			if existidentifier != self.LASTREC[hour]['travel']:
				self.LASTREC[hour]['travel'] = existidentifier
				self.updateMap(mapId, hour, [fromPid, toPid, self.DAY * 24 + hour, 1, 0])
		else:
			self.LASTREC[hour] = {
				'id': id,
				'travel': existidentifier
			}
			self.updateMap(mapId, hour, [fromPid, toPid, self.DAY * 24 + hour, 1, 0])

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
					resArr.append('%s,%s,%d,%d' % (value[0], value[1], value[2], value[3]))
			
			res.write('\n'.join(resArr) + '\n')
		res.close()