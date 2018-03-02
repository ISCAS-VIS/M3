#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Data Format
# [lng, lat, gid, from/to, speed, direction]
# 
# Output data format
# 分方向分 Grid 聚集的结果
# [clusterID, lng, lat, gid, gLng, gLat, from/to, speed, direction]

import os
from util.tripFlow.base import parseFormatGID
from util.tripFlow.LinkList import LinkList


class LineTFIntersections(object):
	def __init__(self, PROP):
		super(LineTFIntersections, self).__init__()
		# self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], 'bj-byhour-tf')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'bj-byhour-res')
		self.index = PROP['index']
		self.dataType = 'angle'
		self.resByAng = PROP['resByAng']

		self.typeNum = 1  # 暂时为1
		self.dbLabel = [[] for x in xrange(0, self.typeNum)]
		self.dbInput = [[] for x in xrange(0, self.typeNum)]
		self.subInfo = [[] for x in xrange(0, self.typeNum)]

		self.eps = PROP['eps']
		self.min_samples = PROP['min_samples']
		self.dbscanBaseNum = 0
	
	def run(self):
		noiseRate = self.iterateRes()
		ofilename = self.outputToFile()

		return noiseRate, ofilename 

	def iterateRes(self):
		cateKeys = {0: 'from', 1: 'to'}
		
		for x in xrange(0, self.typeNum):
			accumulator = 0
			totalNum, noiseNum = 0, 0
			for gid, tripsArray in self.resByAng[cateKeys[x]].iteritems():
				tripsLen = len(tripsArray)
				totalNum += tripsLen
				tmpLngLat, tmpAngle, tmpSubInfo = [], [], []
				for index in xrange(0, tripsLen):
					linelist = tripsArray[index].split(',')

					# lng = float(linelist[0])
					# lat = float(linelist[1])
					gid = int(linelist[2])
					gdirStr = linelist[3]
					speed = linelist[4]
					direction = linelist[5]
					angle = int(float(linelist[6]))
					gidInfo = parseFormatGID(gid, 'e')
					gLat = gidInfo['lat']
					gLng = gidInfo['lng']
					
					tmpLngLat.append(linelist[0] + ',' + linelist[1])
					tmpAngle.append(angle)
					subprops = "%s,%s,%s" % (gdirStr, speed, direction)
					tmpSubInfo.append("%d,%.6f,%.6f,%s" % (gid, gLng, gLat, subprops))

				self.dbInput[x] += tmpLngLat
				self.subInfo[x] += tmpSubInfo

				# DBScan result
				dbres = self.lineCLusterCalculation(tmpAngle)
				noiseNum += dbres['noiseNum']
				self.dbLabel[x] += dbres['labels']

				accumulator += 1
			
			noiseRate = float(noiseNum) / totalNum
			print '''
===	DBScan Info	===
Number of dbscan clusters in all:	%d
Grid ID number: %d
Records(total):	%d
Noise Rate:	%f
===	DBScan Info	===
''' % (self.dbscanBaseNum, accumulator, totalNum, noiseRate)

		return noiseRate

	def lineCLusterCalculation(self, angleArray):
		angleList = [0 for x in xrange(0, 720)]
		# visitedList = [0 for x in xrange(0, 720)]
		labelList = {}
		res = []
		arrayLen = len(angleArray)

		N = self.min_samples
		rho = arrayLen * self.eps / 360  # 每度至少拥有的 trip 数量

		for x in xrange(0, arrayLen):
			angleList[angleArray[x]] += 1
			angleList[angleArray[x] + 360] += 1
		
		initLinkList = []
		for x in xrange(0, 720):
			if angleList[x] != 0:
				initLinkList.append({
					'index': x,
					'data': angleList[x]
				})
		
		ALL = LinkList()
		ALL.initlist(initLinkList)
		listLen = ALL.getlength()
		sIndex = 0
		while(ALL.getitem(sIndex)['index'] < 180):
			sIndex += 1
		# eIndex = sIndex+1
		# while(ALL.getitem(eIndex)['index'] < 540):
		# 	eIndex += 1
		# eIndex -= 1

		cIndex = sIndex
		clusteID = 0
		while(cIndex < listLen):
			base = ALL.getitem(cIndex)
			tfNum, lIndex, rIndex = base['data'], cIndex, cIndex
			lAngle, rAngle = base['index'], base['index']

			if rAngle >= 540:
				break

			# 左右循环直至没有新元素加入则停止，并做好标记和删除工作
			cRho = tfNum / (rAngle - lAngle + 1)
			endFlag = True
			# 密度符合条件的情况下则一直向两边遍历
			while (cRho >= rho):
				tmplIndex, tmprIndex = lIndex, rIndex
				tmplAngle, tmprAngle = lAngle, rAngle
				tmptfNum = tfNum
				tRho = cRho
				while tmplIndex > 0:
					tmpItem = ALL.getitem(tmplIndex-1)
					tmpNum = tmpItem['data']
					tRho = (tmpNum + tfNum) / (rAngle - tmpItem['index'] + 1)
					if tRho >= rho:
						tmplIndex -= 1
						tmplAngle = tmpItem['index']
						cRho = tRho
						tmptfNum += tmpNum
						endFlag = False
					else:
						break
				
				while tmprIndex < listLen:
					tmpItem = ALL.getitem(tmprIndex+1)
					tmpNum = tmpItem['data']
					tRho = (tmpNum + tfNum) / (tmpItem['index'] - lAngle + 1)
					if tRho >= rho:
						tmprIndex += 1
						tmprAngle = tmpItem['index']
						cRho = tRho
						tmptfNum += tmpNum
						endFlag = False
					else:
						break
					
				if endFlag:
					# 没有新增
					break
				else:
					lIndex, rIndex = tmplIndex, tmprIndex
					lAngle, rAngle = tmplAngle, tmprAngle
					tfNum = tmptfNum
			
			# 满足 cluster 条件，否则放弃
			if tfNum >= N:
				for x in xrange(lIndex, rIndex+1):
					angle = ALL.getitem(x)['index'] % 360
					if angle not in labelList.keys():
						labelList[angle] = clusteID + self.dbscanBaseNum
					ALL.delete(x)
				
				lAngle %= 360
				rAngle %= 360
				i = lIndex
				x = lIndex
				while(x < ALL.getlength()):
					tmpItem = ALL.getitem(x)
					tmpAngle = tmpItem['index'] % 360
					notCross = tmpAngle >= lAngle and tmpAngle <= rAngle
					comeCross = rAngle < lAngle and (tmpAngle >= lAngle or tmpAngle <= rAngle)
					if notCross or comeCross:
						ALL.delete(x)
					else:
						x += 1
				
				cIndex = lIndex
				x = 0
				while(x < lIndex):
					tmpItem = ALL.getitem(x)
					tmpAngle = tmpItem['index'] % 360
					notCross = tmpAngle >= lAngle and tmpAngle <= rAngle
					comeCross = rAngle < lAngle and (tmpAngle >= lAngle or tmpAngle <= rAngle)
					if notCross or comeCross:
						ALL.delete(x)
						cIndex -= 1
					else:
						x += 1
			else:
				cIndex += 1

			# 扫尾工作
			clusteID += 1
			listLen = ALL.getlength()

		# 返回结果计算
		noiseNum = 0
		for x in xrange(0, arrayLen):
			angle = angleArray[x]
			if angle in labelList.keys():
				res.append(labelList[angle])
			else:
				noiseNum += 1
				res.append(-1)
		
		# 更新 cluster ID 基数
		self.dbscanBaseNum += clusteID

		return {
			'labels': res, 
			'noiseNum': noiseNum
		}

	def outputToFile(self):
		ores = []
		i = 0
		for i in xrange(0, self.typeNum):
			for j in xrange(0, len(self.dbLabel[i])):
				label = self.dbLabel[i][j]
				lngLatStr = self.dbInput[i][j]
				subInfoStr = self.subInfo[i][j]
				onerecStr = "%s,%s,%s" % (label, lngLatStr, subInfoStr)
				ores.append(onerecStr)

		ofilename = 'tfres-%s-%d' % (self.dataType, self.index)
		ofile = os.path.join(self.OUTPUT_PATH, ofilename)
		with open(ofile, 'wb') as f:
			f.write('\n'.join(ores))
		f.close()

		return ofilename
		