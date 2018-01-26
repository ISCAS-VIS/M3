#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Data Format
# [hour, id, time, lat, lng, from_lat, from_lng, from_time, to_lat, to_Lng, to_time]

import os
from util.tripFlow.base import getFormatGID
from util.tripFlow.base import haversine


class ExtractGridEdges(object):
	def __init__(self, PROP):
		super(ExtractGridEdges, self).__init__()
		self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], 'bj-byhour-tf')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'bj-byhour-rec')
		self.index = PROP['index']
		# self.SAFECOUNT = PROP['SAFECOUNT']
		self.res = {'o': {}, 'd': {}}
    
	def run(self):
		ifile = os.path.join(self.INPUT_PATH, 'traveldata-%d' % (self.index))
		
		self.iterateFile(ifile)
		self.outputToFile()
		
	def iterateFile(self, file):	
		with open(file, 'rb') as f:
			firstLine = True
			currentNo = -1
			# count = 0
			fromLat = -1
			fromLng = -1
			fromTime = -1
			for line in f:
				line = line.strip('\n')
				linelist = line.split(',')

				no = "%s-%s-%s-%s" % (linelist[5], linelist[6], linelist[8], linelist[9])
				toLat = linelist[3]
				toLng = linelist[4]
				toTime = int(linelist[2])

				if firstLine:  # 第一行初始化
					firstLine = False
					currentNo = no
					fromLat = toLat
					fromLng = toLng
					fromTime = toTime
				else:
					if currentNo == no:  # 同一段旅程
						# count += 1
						fromGid = getFormatGID([fromLng, fromLat])['gid']
						toGid = getFormatGID(toLng, toLat)['gid']
						distance = haversine(fromLng, fromLat, toLng, toLat)
						speed = distance / (toTime-fromTime)
						direction = ''
						vecStr = "%d,%d,%f,%s" % (fromGid, toGid, speed, direction)

						if fromGid in self.res['o'].keys():
							self.res['o'][fromGid].append(vecStr)
						else:
							self.res['o'][fromGid] = [vecStr]

						if toGid in self.res['d'].keys():
							self.res['d'][toGid].append(vecStr)
						else:
							self.res['d'][toGid] = [vecStr]
						# 计算速度、方向，组成边向量
						
						fromLat = toLat
						fromLng = toLng
						fromTime = toTime
					else:  # 新旅程第一个点
						currentNo = no
						fromLat = toLat
						fromLng = toLng
						fromTime = toTime

		f.close()
	
	def outputToFile(self):
		"""
		通用输出文件函数
			:param self: 
			:param res: 
		"""
		ofile = os.path.join(self.OUTPUT_PATH, 'triporec-%d' % (self.index))
		dfile = os.path.join(self.OUTPUT_PATH, 'tripdrec-%d' % (self.index))
		ores, dres = [], []
		
		for key, value in self.res['o'].iteritems():
			ores.append('\n'.join(value))
		for key, value in self.res['d'].iteritems():
			dres.append('\n'.join(value))

		with open(ofile, 'wb') as f:
			f.write('\n'.join(ores))
		f.close()
		with open(dfile, 'wb') as f:
			f.write('\n'.join(dres))
		f.close()