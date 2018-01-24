#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import os
from base import parseFormatGID, getFormatGID


class ExtractGridEdges(object):
	def __init__(self, PROP):
		super(ExtractGridEdges, self).__init__()
		self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], 'clusterPOI')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'clusterPOI')
		self.index = PROP['index']
    
	def run(self):
		pass

		ifile = 'rawdata-hour-%d' % (self.index)
		with open(ifile, 'rb') as f:
			firstLine = True
			currentNo = -1
			fromGid_old = -1
			fromTime = -1
			for line in f:
				line = line.strip('\n')
				linelist = line.split(',')

				no = "%s-%s" % (linelist[7], linelist[8])
				toGid_old = int(linelist[4])
				toTime = linelist[0]
				if firstLine:  # 第一行初始化
					firstLine = False
					currentNo = no
					fromGid_old = toGid_old
				else:
					if currentNo == no:  # 同一段旅程
						self.calOneEdgeVec(fromGid_old, toGid_old, fromTime, toTime)
						# 计算速度、方向，组成边向量
						# [fromGid, toGid, speed, direction]

					else:  # 新旅程第一个点
						currentNo = no
						fromGid_old = toGid_old

		f.close()
	
	def calOneEdgeVec(self, fromGid, toGid, fromTime, toTime):
