#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [apoint-[x]]
# aid, dev_num, rec_num, seg, hour, weekday
# [aaedge-[x]]
# from_aid, to_aid, dev_num, rec_num, seg, hour, weekday
# 
# 改进后计算脚本，适用于 Admin 区划下的点边信息聚集计算方案

import os
import gc
import logging


class UniAdmDiswithEdgeBasic(object):
	"""
	多进程计算类：输入分天的处理后数据，将定位记录数/人数按照行政区划切分计算并存入文件，一个进程执行一次负责一天24小时时间段的数据处理，结果增量输入至文件，包含点信息以及边信息，最后多进程执行情况下需要做合并操作
		:param object: 
	"""
	def __init__(self, PROP):
		super(UniAdmDiswithEdgeBasic, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.DIRECTORY = PROP['DIRECTORY'] 
		self.SUBOPATH = PROP['SUBOPATH']
		self.INUM = PROP['INUM']
		self.DAY = -1

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
			
			# 处理星期几的存储
			tmpWed = (number+2) % 7
			self.WEEKDAY = 7 if tmpWed == 0 else tmpWed  # 1-7

			# MAP 存储点信息，EMAP 存储边信息
			self.MAP = [self.genAdmMapObj() for e in xrange(0, 24)]
			self.EMAP = [{} for each in xrange(0, 24)]
			self.LASTREC = [{
				'sid': -1,
				'tid': -1,
				'adm': [],
				'travel': '-1'
			} for x in xrange(0, 24)]

			ifilename = 'hares-%d' % number  # 输入文件名称
			logging.info('Job-%d File-%d Operating...' % (self.INDEX, number))
			self.updateDis(os.path.join(idir, ifilename))
		
			# 结果写进文件
			# # MATRIX
			opFile = os.path.join(odir, 'apoint-%d' % (self.INDEX))
			oeFile = os.path.join(odir, 'aaedge-%d' % (self.INDEX))
			self.writeData(opFile, oeFile)
			self.MAP = []
			self.LASTREC = []
			gc.collect()

	def genAdmMapObj(self):
		res = []
		for key in xrange(0, 16):
			res.append([key+1, 0, 0])
		return res
    		
	def updateDis(self, ifile):
		resnum = 0

		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				linelist = line.split(',')

				state = linelist[3]
				fromAid = int(linelist[4])
				toAid = int(linelist[5])
				id = linelist[0]
				hour = int(linelist[1]) % 24
				adm = int(linelist[6])-1  # 0-15

				if state == 'T':
					resnum += 1
					
					mapId = "%s,%s" % (fromAid, toAid)
					self.dealOneEdge({
						'id': id,
						'hour': hour,
						'existidentifier': '%s-%d-%s-%s' % (id, hour, fromAid, toAid),
						'fromAid': fromAid,
						'toAid': toAid,
						'mapId': mapId,
						'adm': adm
					})
				else:
					resnum += 1
					self.dealOnePoint({
						'id': id,
						'hour': hour,
						'adm': adm
					})
		stream.close()
		print "Process %d, day %d, result number %d" % (self.INDEX, self.DAY, resnum)

	def dealOnePoint(self, data):
		id = data['id']
		hour = data['hour']
		adm = data['adm']

		# stay 状态更新
		# 判断此记录是否与上次一致
		if id == self.LASTREC[hour]['sid']:
			# 判断 poi ID 在指定时段中是否出现过
			# print adm, self.LASTREC[hour]
			if adm not in self.LASTREC[hour]['adm']:
				self.LASTREC[hour]['adm'].append(adm)
				self.MAP[hour][adm][1] += 1  # index, people, number
		else:
			self.LASTREC[hour]['sid'] = id
			self.LASTREC[hour]['travel'] = '-1'
			# self.LASTREC[hour]['adm'] = [adm]
			self.MAP[hour][adm][1] += 1

		self.MAP[hour][adm][2] += 1

	def dealOneEdge(self, data):
		"""
		
			:param self: 
			:param data: 
		"""
		id = data['id']
		mapId = data['mapId']
		hour = data['hour']
		fhour = self.DAY * 24 + data['hour']
		fromAid = data['fromAid']
		toAid = data['toAid']
		existidentifier = data['existidentifier']
		
		# 人未变
		if id == self.LASTREC[hour]['tid']:
			# 同一个人新纪录，如果记录相同则不作处理
			if existidentifier != self.LASTREC[hour]['travel']:
				self.LASTREC[hour]['travel'] = existidentifier
				self.updateEMap(mapId, hour, [fromAid, toAid, fhour, 1, 0])
		else:
			self.LASTREC[hour]['tid'] = id
			self.LASTREC[hour]['travel'] = existidentifier
			
			self.updateEMap(mapId, hour, [fromAid, toAid, fhour, 1, 0])
		
		self.EMAP[hour][mapId][4] += 1

	def updateEMap(self, key, hour, val):
		"""
		更新边信息矩阵函数
			:param self: 
			:param key: 
			:param hour: 
			:param val: 
		"""
		if key in self.EMAP[hour]:
			self.EMAP[hour][key][3]  += 1
		else:
			self.EMAP[hour][key] = val

	def writeData(self, pointFile, edgeFile):
		resArr = []

		with open(edgeFile, 'ab') as res:
			# 24 时间段
			for hour in xrange(0, 24):

				for key, value in self.EMAP[hour].iteritems():
					resArr.append('%s,%s,%d,%d,%d,%d,%d' % (value[0], value[1], value[3], value[4], value[2], hour, self.WEEKDAY))
			
			res.write('\n'.join(resArr) + '\n')
		res.close()

		resString = []
		with open(pointFile, 'ab') as res:
		# 24 时间段
			for x in xrange(0, 24):
				seg = self.DAY * 24 + x

				for oneRec in self.MAP[x]:
					singleRes = "%s,%d,%d,%d,%d,%d" % (oneRec[0], oneRec[1], oneRec[2], seg, x, self.WEEKDAY)
					resString.append(singleRes)

			res.write('\n'.join(resString) + '\n')
		res.close()