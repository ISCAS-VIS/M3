#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# input
# [gLng, gLat, gdirStr(from or to), speed, recordNum, dLng, dLat, seg(hour ID)]


import os 
import json
from math import acos, pi
from util.tripFlow.base import getFormatGID
from util.tripFlow.base import parseFormatGID
from util.tripFlow.base import cosVector


class ConstructTreeMap(object):
	def __init__(self, PROP):
		super(ConstructTreeMap, self).__init__()
		self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], 'bj-byhour-res')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'bj-byhour-res')
		self.dataType = PROP['dataType']
		self.index = PROP['index']
		self.custom_params = PROP['custom_params']
		self.treeNodesID = 0
		# Custom Patams Foramt
		# {
		# 	'tree_num': 0,
		# 	'search_angle': 0,
		# 	'seed_strength': 0,
		# 	'max_curvation': 0,
		# 	'tree_width': 0,
		# 	'jump_length': 0
		# }
		self.entries = []  # 起始点集合
		self.currentData = {}
		self.recDict = {}  # record 字典，key 值为 gid 字符串
		self.treeMap = []  # 存储的 treemap 数组

	def run(self):
		input_filename = 'mcres-%s-%d' % (self.dataType, self.index)
		output_filename = 'tmres-%s-%d' % (self.dataType, self.index)
		ifile = os.path.join(self.INPUT_PATH, input_filename)
		ofile = os.path.join(self.OUTPUT_PATH, output_filename)
		self.iterateFile(ifile)

		for x in xrange(0, self.custom_params['tree_num']):
			# 初始化工作
			element = self.entries.pop()
			self.currentData = {
				'lng': element[0],
				'lat': element[1],
				'direction': element[5:7],
				'strength': element[4], 
				'speed': element[3]
			}

			res = self.BFSOneTreeMap(element[:], 0)
			if res:
				self.treeMap.append(res)
		
		self.outputToFile(ofile)

	def iterateFile(self, ifile):
		"""
		遍历文件，构建 gid-record 字典
			:param self: 
			:param ifile: 
		"""
		with open(ifile, 'rb') as f:
			nodeID = 0
			for line in f:
				line = line.strip('\n')
				linelist = line.split(',')

				# 
				lng = float(linelist[0])
				lat = float(linelist[1])
				formatGID = getFormatGID([lng, lat])
				{gid, lngind, latind} = formatGID
				# gdirStr = linelist[2]

				linelist[6] = float(linelist[6])
				linelist[5] = float(linelist[5])
				
				linelist[3] = float(linelist[3])
				linelist[4] = int(linelist[4])

				linelist.extend([gid, lngind, latind, nodeID])
				nodeID += 1
				gidStr = str(gid)
				if gidStr in self.recDict.keys():
					self.recDict[gidStr].append(linelist)
				else:
					self.recDict[gidStr] = [linelist]
					self.entries.append(linelist[:])
		f.close()
	
	def BFSOneTreeMap(self, parentNode, recordNum=0):
		queue = []
		parentNRN = parentNode[4]

		res = {
			"root": {
				"id": self.treeNodesID,
				"lng": parentNode[0],
				"lat": parentNode[1],
				"num": recordNum
			},
			"children": []
		}
		self.treeNodesID += 1
		nothing = True

		# 六个交点计算，得出三个 gid，然后匹配方向加入 queue
		point = [parentNode[0], parentNode[1], parentNode[-4]]
		direction = [parentNode[5], parentNode[6]]
		gids = self.getNextGIDs(point, direction)
		queue += self.getNextDirections(gids, parentNode)

		# BFS Looping Condition
		while queue:
			vertex = queue.pop(0)
			
			child = self.BFSOneTreeMap(vertex, parentNRN)
			if child:
				nothing = False
				res['children'].append(child)

				gidStr = vertex[-4]
				nodeID = vertex[-1]
				self.deleteNode(gid, nodeID)

		# result
		if nothing:
			del res['children']
		
		return res
	
	def getNextGIDs(self, point, direction):
		"""
		获取方向后续的前 N 个交点
			:param self: 
			:param point: [lng, lat, gid] 
			:param direction: 
		"""
		res = []
		[x, y] = direction
		fromLat = point[1]
		fromLng = point[0]

		latDir = 1 if y > 0 else -1
		lngDir = 1 if x > 0 else -1

		jumpPoints = []

		# 计算网格方边交点
		if y != 0:  # 与平行纬度线相交
			k = x / y
			for i in xrange(0, self.custom_params['jump_length']):
				incrementLat = self.custom_params['LatSPLIT'] * (0.5 + i) * latDir
				iLng = fromLng + incrementLat * k
				iLat = incrementLat + fromLat
				# key = '0,%d' % (i)
				jumpPoints.append([iLng, iLat, 0, i])

		if x != 0:  # 与平行经度线相交
			k = y / x
			for i in xrange(0, self.custom_params['jump_length']):
				incrementLng = self.custom_params['LngSPLIT'] * (0.5 + i) * lngDir
				iLat = fromLat + incrementLng * k
				iLng = incrementLng + fromLng
				key = '%d,0' % (i)
				jumpPoints[key] = [iLng, iLat, i, 0]

		if x != 0 and y != 0:
    		# 根据纬度从小到大排前三
			for i in xrange(self.custom_params['jump_length'], self.custom_params['jump_length'] * 2):
				current = 0
				while (jumpPoints[i][0] > jumpPoints[current][0]):
					current += 1
					if current == self.custom_params['jump_length']:
						break
				
				if current != self.custom_params['jump_length']:
					for switch in xrange(self.custom_params['jump_length']-1, current):
						jumpPoints[switch] = jumpPoints[switch-1][:]
					jumpPoints[current] = jumpPoints[i][:]
		
		# 只取三个交点
		for i in xrange(0, self.custom_params['jump_length']):
			lng = jumpPoints[i][0]
			lat = jumpPoints[i][1]
			if jumpPoints[i][2] == 0:
				ilat = lat + 0.002 * latDir  # 0.002 为一小点偏量
			else:
				ilng = lng + 0.002 * lngDir

			point = getFormatGID([ilng, ilat])
			gid = point['gid']
			res.append([lng, lat, gid])
		
		return res
	
	def getNextDirections(self, gids, parentNode):
		"""
		获取接下来最接近条件的 N 个方向并返回
			:param self: 
			:param gids: 
			:param parentNode: 
		"""
		topSearchs = []
		topSearchAngles = []
		res = []
		gidsLen = len(gids)

		# 每个网格遍历
		for index in xrange(0, gidsLen):
			gid = str(gids[index][2])
			if gid not in self.recDict.keys():
				continue
			recsLen = len(self.recDict[gid])

			# 每个网格中的方向遍历
			for subIndex in xrange(0, recsLen):
				rec = self.recDict[gid][subIndex]
				validation = self.judgeRecordLegality(rec, parentNode)
				if validation:
    				# 处理符合条件的方向，进行分叉检查
					if len(topSearchs) < self.custom_params['tree_num']:
						topSearchs.append(rec[:])
						topSearchAngles.append(validation['currentAngle'])
					else:
						maxAngleIndex = -1
						maxAngle = validation['currentAngle']
						for topIndex in xrange(0, self.custom_params['tree_num']):
							tmpAngle = topSearchAngles[topIndex]
							if maxAngle < tmpAngle:
								maxAngleIndex = topIndex
								maxAngle = tmpAngle
						
						# 替换掉当前最大偏差的方向
						if maxAngleIndex != -1:
							topSearchs[maxAngleIndex] = rec[:]
							topSearchAngles[maxAngleIndex] = validation['currentAngle']
		
		return topSearchs

	def judgeRecordLegality(self, rec, parentNode):
		currentDirection = rec[5:7]
		currentStrength = rec[4]

		parentDirection = [parentNode[5], parentNode[6]]
		parentStrength = parentNode[4]

		currentAngle = acos(cosVector(parentDirection, currentDirection)) * 180 / pi
		if currentAngle < -self.custom_params['search_angle'] or currentAngle > self.custom_params['search_angle']:
			return False
		
		initDirection = self.currentData['direction']
		accumulatedAngle = acos(cosVector(initDirection, currentDirection)) * 180 / pi
		if accumulatedAngle < -self.custom_params['max_curvation'] or accumulatedAngle > self.custom_params['max_curvation']:
			return False

		if currentStrength < parentStrength * self.custom_params['seed_strength']:
			return False
		
		return {
			'currentAngle': currentAngle,
			'accumulatedAngle': accumulatedAngle
		}

	def deleteNode(self, gid, nodeID):
		"""
		根据 gid 以及 node 编号删除对应记录
			:param self: 
			:param gid: 
			:param nodeID: 
		"""
		nodesLen = len(self.recDict[gid])

		for x in xrange(0, nodesLen):
			if self.recDict[gid][x][-1] == nodeID:
				if len(self.recDict[gid]) == 1:
					self.recDict.pop(gid, None) 
				else: 
					del self.recDict[gid][x] 
				return True
	
	def outputToFile(self, ofile):
		with open(ofile, 'wb') as f:
			json.dump({
				'res': self.treeMap,
				'len': len(self.treeMap)
			}, f)
		f.close()