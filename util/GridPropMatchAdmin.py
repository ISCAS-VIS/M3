#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [grid-res]
# nid, aid

import os
from util.preprocess import getCityLocs, getFormatGID, parseFormatGID
from shapely.geometry import Point, Polygon
import logging


class GridPropMatchAdmin(object):
	"""
	遍历网格, 计算其所属行政区划信息，构成有效网格映射关系表
		:param object: 
	"""
	def __init__(self, PROP):
		super(GridPropMatchAdmin, self).__init__()

		self.basepath = PROP['basepath']
		self.INDEX = PROP['INDEX']
		self.city = PROP['city']
		self.MATRIX = PROP['MATRIX']
		self.BOUNDARIES = PROP['BOUNDARIES']
		self.gridList = []

	def run(self):
		# begin
		gridLen = 10000
		count = 1
		cityLocs = getCityLocs('beijing')

		# 遍历每个实例充实带小区属性的网格数据
		for id in xrange(0, gridLen):
			self.updGrids({
				'id': id,
				'cityLocs': cityLocs
			})
			
			count += 1

		# 网格数据归一化存入文件，处理结果
		ofile = os.path.join(self.basepath, "BJ-MID-SQL", "grid-admin-j%d" % self.INDEX)
		self.writeToFile(ofile)

		# end
	
	def updGrids(self, props):
		"""
		计算指定编号网格所属行政区划
			:param self: 
			:param props: 
		"""
		# 获取围栏边界
		for index, item in enumerate(self.BOUNDARIES):
			polygon = Polygon(item['coordinates'])
			point = parseFormatGID(props['cityLocs'], props['id'])

			if polygon.contains(Point(point['lng'], point['lat'])):
				newGridRec = "%d,%s" % (props['id'], index)  # gid, aid
				return self.MATRIX.append(newGridRec)

	def writeToFile(self, file):
		"""
		将结果写入文件
			:param self: 
			:param file: 
		"""
		with open(file, 'ab') as f:
			f.write('\n'.join(self.MATRIX))
		f.close()
