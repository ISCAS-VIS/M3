#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [grid-res]
# nid, pid, lng, lat, x, y

import os
from util.preprocess import getCityLocs, getFormatGID, parseFormatGID
from shapely.geometry import Point, Polygon
from shapely.geometry import shape
import logging


class GridPropSup(object):
	"""
	遍历 POI 增加有属性的网格信息
		:param object: 
	"""
	def __init__(self, PROP):
		super(GridPropSup, self).__init__()

		self.basepath = PROP['basepath']
		self.pidList = PROP['pidList']
		self.INDEX = PROP['INDEX']
		self.city = PROP['city']
		self.MATRIX = []
		self.gridList = []

	def run(self):
		# begin
		pidLen = len(self.pidList)
		count = 1

		# 遍历每个实例充实带小区属性的网格数据
		for each in self.pidList:
			self.updGrids({
				'pid': each['pid'],
				'boundary': each['coordinates']
			})
			# break
			logging.info("Finish %d - poi %d, %f percent in total." % (self.INDEX, count, count * 100.0 / pidLen))
			count += 1

		# 网格数据归一化存入文件，处理结果
		ofile = os.path.join(self.basepath, "BJ-MID-SQL", "grid-j%d" % self.INDEX)
		self.writeToFile(ofile)

		# end
	
	def updGrids(self, props):
		"""
		根据给定 POI 进行网格更新
			:param self: 
			:param props: 
		"""
		# 获取围栏边界
		edgePoints = self.getPoiEdgePoints(props['boundary'])
		pid = props['pid']
		polygon = Polygon(props['boundary'])
		
		# shape({
		# 	'type': 'Polygon',
		# 	"coordinates": [props['boundary']]
		# 	# "coordinates": [[[0,0],[0,1],[1,1],[1,0],[0,0]]]
		# })

		# 遍历小格判断
		cityLocs = getCityLocs('beijing')
		swIndex = getFormatGID(cityLocs, edgePoints['sw'])
		neIndex = getFormatGID(cityLocs, edgePoints['ne'])

		for x in xrange(swIndex['lngind'], neIndex['lngind']+1):
			for y in xrange(swIndex['latind'], neIndex['latind']+1):
				point = parseFormatGID(cityLocs, {'x': x, 'y': y})
				# print point['lng'], point['lat']

				if polygon.contains(Point(point['lng'], point['lat'])):
					# print 'yes'
					self.gridList.append(pid)
					newGridRec = "%d,%d" % (point['nid'], pid)
					# newGridRec = "%d,%d,%f,%f,%d,%d" % (point.nid, pid, point.lng, point.lat, x, y)
					self.MATRIX.append(newGridRec)

	def getPoiEdgePoints(self, boundary):
		"""
		计算一个围栏东南西北的边缘位置
			:param self: 
			:param boundary: 
		"""

		res = {
			'w': 180,
			'e': 0,
			'n': 0,
			's': 90
		}

		for each in boundary:
			if each[0] > res['e']:
				res['e'] = each[0]
			elif each[0] < res['w']:
				res['w'] = each[0]
			
			if each[1] > res['n']:
				res['n'] = each[1]
			elif each[1] < res['s']:
				res['s'] = each[1]
		
		return {
			'sw': [res['w'], res['s']],
			'ne': [res['e'], res['n']]
		}
	
	def writeToFile(self, file):
		"""
		将结果写入文件
			:param self: 
			:param file: 
		"""
		with open(file, 'ab') as f:
			f.write('\n'.join(self.MATRIX))
		f.close()
