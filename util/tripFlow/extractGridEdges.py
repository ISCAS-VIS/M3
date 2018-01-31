#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Input Data Format
# [hour, id, time, lat, lng, from_lat, from_lng, from_time, to_lat, to_Lng, to_time]
# 
# Output Data Format
# [lng, lat, gid, from/to, speed, direction]

import os
from util.tripFlow.base import getFormatGID
from util.tripFlow.base import getRealDistance
from util.tripFlow.base import getDirection
from util.tripFlow.base import parseFormatGID


class ExtractGridEdges(object):
	def __init__(self, PROP):
		super(ExtractGridEdges, self).__init__()
		self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], 'bj-byhour-tf')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'bj-byhour-rec')
		self.index = PROP['index']
		self.res = {'e': {}, 'n': {}, 'w': {}, 's': {}}
    
	def run(self):
		ifile = os.path.join(self.INPUT_PATH, 'traveldata-%d' % (self.index))
		
		self.iterateFile(ifile)
		return self.outputToFile()
		
	def iterateFile(self, file):
		count = 0
		with open(file, 'rb') as f:
			firstLine = True
			currentNo = -1
			fromLat = -1
			fromLng = -1
			fromTime = -1

			for line in f:
				count += 1
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
						# 如果当前点位置不变则继续遍历
						if (fromLat == toLat and fromLng == toLng) or fromTime == toTime:
							continue

						fPoint = [fromLng, fromLat]
						tPoint = [toLng, toLat]

						fromGid = getFormatGID(fPoint)['gid']
						toGid = getFormatGID(tPoint)['gid']
						distance = getRealDistance(fromLng, fromLat, toLng, toLat)
						speed = distance / (toTime-fromTime)
						direction = getDirection(fPoint, tPoint)  # w n s e 四个字符之一

						# 处理相交点
						fGidIPoint, tGidIPoint = self.getIntersection(fPoint, tPoint, fromGid, toGid, direction)
						fGidIPointStr = "%.6f,%.6f" % (fGidIPoint[0], fGidIPoint[1])
						tGidIPointStr = "%.6f,%.6f" % (tGidIPoint[0], tGidIPoint[1])

						# 结果字符串
						fromVecStr = "%s,%d,from,%f,%s" % (fGidIPointStr, fromGid, speed, direction)
						toVecStr = "%s,%d,to,%f,%s" % (tGidIPointStr, toGid, speed, direction)

						if fromGid in self.res[direction].keys():
							self.res[direction][fromGid].append(fromVecStr)
						else:
							self.res[direction][fromGid] = [fromVecStr]

						if toGid in self.res[direction].keys():
							self.res[direction][toGid].append(toVecStr)
						else:
							self.res[direction][toGid] = [toVecStr]
						
						fromLat = toLat
						fromLng = toLng
						fromTime = toTime
					else:  # 新旅程第一个点
						currentNo = no
						fromLat = toLat
						fromLng = toLng
						fromTime = toTime

		f.close()
		print "Total %d records in this file." % (count)

	def getIntersection(self, fPoint, tPoint, fromGid, toGid, direction):
		# [lng, lat]

		fGIPoint, tGIPoint = [], []
		fromLat = float(fPoint[1])
		fromLng = float(fPoint[0])
		toLat = float(tPoint[1])
		toLng = float(tPoint[0])

		# 处理 from/to
		toDirection = {
			'n': 's',
			's': 'n',
			'w': 'e',
			'e': 'w'
		}
		pfRes = parseFormatGID(fromGid, direction)
		ptRes = parseFormatGID(toGid, toDirection[direction])
		fGidLine = pfRes['dlinePoint']
		tGidLine = ptRes['dlinePoint']
		fLng = pfRes['lng']
		fLat = pfRes['lat']
		tLng = ptRes['lng']
		tLat = ptRes['lat']

		# 计算交点
		if direction in ['n', 's']:  # 与平行维度线相交
			k = (toLng - fromLng) / (toLat - fromLat)
			b1, b2 = fLng, tLng
			fIlng = b1 + (fGidLine - fromLat) * k
			fGIPoint = [fIlng, fGidLine]
			tIlng = b2 + (tGidLine - fromLat) * k
			tGIPoint = [tIlng, tGidLine]
		else:  # 与平行经度线相交
			k = (toLat - fromLat) / (toLng - fromLng)
			b1, b2 = fLat, tLat
			fIlat = b1 + (fGidLine - fromLng) * k
			fGIPoint = [fGidLine, fIlat]
			tIlat = b2 + (tGidLine - fromLng) * k
			tGIPoint = [tGidLine,tIlat]

		return fGIPoint, tGIPoint
	
	def outputToFile(self):
		"""
		通用输出文件函数
			:param self: 
			:param res: 
		"""
		
		# 待更新
		ores = []
		i = 0
		gidNum, recNum = 0, 0
		memres = [[] for x in xrange(0, 4)]
		for key, val in self.res.iteritems():  # 东西南北四个方向遍历
			for subkey ,subval in val.iteritems():  # 每个方向里不同 gid 数据遍历
				gidNum += 1
				recNum += len(subval)
				ores.append('\n'.join(subval))
				memres[i] += subval
			i += 1
		
		print "Total %d gids and %d records in four directions" % (gidNum, recNum)

		ofile = os.path.join(self.OUTPUT_PATH, 'triprec-%d' % (self.index))
		with open(ofile, 'wb') as f:
			f.write('\n'.join(ores))
		f.close()

		return memres