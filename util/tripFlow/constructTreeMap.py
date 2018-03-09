#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# input
# [gLng, gLat, gdirStr(from or to), speed, recordNum, dLng, dLat, seg(hour ID)]


import os 
import json
import numpy as np
from math import acos, cos, pi
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
		self.keepTreeStructList = []
		
		self.recDict = {}  # record 字典，key 值为 gid 字符串
		self.treeMap = []  # 存储的 treemap 数组

	def run(self):
		input_filename = 'mcres-%s-%d' % (self.dataType, self.index)
		# input_filename = 'mcres-%d' % (self.index)
		output_filename = 'tmres-%s-%d' % (self.dataType, self.index)
		ifile = os.path.join(self.INPUT_PATH, input_filename)
		ofile = os.path.join(self.OUTPUT_PATH, output_filename)
		totalNum = self.iterateFile(ifile)
		usedNum = 0

		for x in xrange(0, self.custom_params['tree_num']):
			# 初始化工作
			if len(self.entries) == 0:
				break

			element = self.entries.pop()
			self.currentData = {
				'lng': element[0],
				'lat': element[1],
				'direction': element[5:7],
				'strength': element[4], 
				'speed': element[3],
				'count': 0
			}

			gid = str(element[-4])
			# 如果之前的操作已经删除了该记录对应的
			if not self.ifNodeExist(gid, element[-1]):
				continue

			self.deleteNode(gid, element[-1])
			res = {
				"root": {
					"id": self.treeNodesID,
					"lng": element[0],
					"lat": element[1],
					"num": 0
				},
				"children": []
			}
			childs = self.BFSOneTreeMap(element[:], element[4], [], element[-4])
			res['children'].append(childs)
			self.treeMap.append(res)

			print "#%d TreeMap Nodes Number: %d" % (x, self.currentData['count']+1)
			usedNum += self.currentData['count'] + 1
		
		print "Edges Uesd Rate: %.4f" % (float(usedNum)/totalNum)
		print "Tree Average Edges Number: %.4f" % (float(usedNum)/self.custom_params['tree_num'])
		self.outputToFile(ofile)

	def iterateFile(self, ifile):
		"""
		遍历文件，构建 gid-record 字典
			:param self: 
			:param ifile: 
		"""
		res = []

		with open(ifile, 'rb') as f:
			nodeID = 0
			for line in f:
				line = line.strip('\n')
				linelist = line.split(',')

				if linelist[2] != 'from':
					continue

				# 
				linelist[0] = float(linelist[0])
				linelist[1] = float(linelist[1])
				formatGID = getFormatGID([linelist[0], linelist[1]])
				# {gid, lngind, latind} = formatGID
				gid = formatGID['gid']
				lngind = formatGID['lngind']
				latind = formatGID['latind']
				# gdirStr = linelist[2]

				linelist[6] = float(linelist[6])
				linelist[5] = float(linelist[5])
				
				linelist[3] = float(linelist[3])
				linelist[4] = int(linelist[4])

				linelist.extend([gid, lngind, latind, nodeID])
				nodeID += 1
				
				res.append(linelist[:])
		f.close()
		
		# 按照 deviceNum 排序
		res.sort(key=lambda x:x[4], reverse=True)
		for i in xrange(0, nodeID):
			currentLine = res[i]
			gidStr = str(currentLine[-4])
			if gidStr in self.recDict.keys():
				self.recDict[gidStr].append(currentLine)
			else:
				self.recDict[gidStr] = [currentLine]
			
			# 筛选种子
			if i < self.custom_params['tree_num']:
				self.entries.append(currentLine[:])

		return len(res)
	
	def BFSOneTreeMap(self, parentNode, recordNum=0, treeQueue=[], currentNodeGID = 0):
		self.treeNodesID += 1
		self.currentData['count'] += 1 

		for each in treeQueue:
			id = "%d-%s" % (each[-4], each[-1])
			if id not in self.keepTreeStructList:
				self.keepTreeStructList.append(id)

		queue = []
		parentNRN = parentNode[4]
		nothing = True

		# 六个交点计算，得出三个 gid，然后匹配方向加入 queue
		point = [parentNode[0], parentNode[1], currentNodeGID]
		direction = [parentNode[5], parentNode[6]]
		tmpStepRes = self.getNextGIDs(point, direction)
		gids = tmpStepRes['res']
		originGid = tmpStepRes['originGid']
		queue += self.getNextDirections(gids, parentNode, originGid)
		queueCopy = queue[:]

		res = {
			"root": {
				"id": self.treeNodesID,
				"lng": gids[0][0],
				"lat": gids[0][1],
				"num": recordNum
			},
			"children": [  ]
		}

		# BFS Looping Condition
		while queue:
			vertex = queue.pop(0)
			
			gidStr = str(vertex[-4])
			nodeID = vertex[-1]

			treeStructID = "%s-%s" % (gidStr, nodeID)
			if treeStructID in self.keepTreeStructList:
				continue

			# print "self.currentData['count']: %d" % self.currentData['count']
			# print "Length of queue: %d" % len(queue)

			node = self.deleteNode(gidStr, nodeID)
			child = self.BFSOneTreeMap(vertex, parentNRN, queueCopy, originGid)
			
			# if 'children' in child.keys():
			nothing = False
			res['children'].append(child)

			# 	self.deleteNode(gidStr, nodeID)
			# else:
			# 	self.appendNode(node, gidStr)

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
		fromGID = point[2]
		parsedObj = parseFormatGID(fromGID)
		baseLatCenter = parsedObj['lat']
		baseLngCenter = parsedObj['lng']

		latDir = 1 if y > 0 else -1
		lngDir = 1 if x > 0 else -1

		jumpPoints = []

		# 计算网格方边交点
		if y != 0:  # 与平行纬度线相交
			k = x / y
			for i in xrange(0, self.custom_params['jump_length']):
				incrementLat = baseLatCenter + self.custom_params['LatSPLIT'] * (0.5 + i) * latDir - fromLat
				iLng = fromLng + incrementLat * k
				iLat = incrementLat + fromLat
				# key = '0,%d' % (i)
				jumpPoints.append([iLng, iLat, 0, i])

		if x != 0:  # 与平行经度线相交
			k = y / x
			for i in xrange(0, self.custom_params['jump_length']):
				incrementLng = baseLngCenter + self.custom_params['LngSPLIT'] * (0.5 + i) * lngDir - fromLng
				iLat = fromLat + incrementLng * k
				iLng = incrementLng + fromLng
				# key = '%d,0' % (i)
				jumpPoints.append([iLng, iLat, i, 0])

		if x != 0 and y != 0:
    		# 根据纬度从小到大排前三
			# for i in xrange(self.custom_params['jump_length'], self.custom_params['jump_length'] * 2):
			# 	current = 0
			# 	while (jumpPoints[i][0] > jumpPoints[current][0]):
			# 		current += 1
			# 		if current == self.custom_params['jump_length']:
			# 			break
				
			# 	if current != self.custom_params['jump_length']:
			# 		for switch in xrange(self.custom_params['jump_length']-1, current):
			# 			jumpPoints[switch] = jumpPoints[switch-1][:]
			# 		jumpPoints[current] = jumpPoints[i][:]
			
			# 
			for i in xrange(self.custom_params['jump_length'], self.custom_params['jump_length'] * 2):
				currentIndex = -1
				currentMax = jumpPoints[i][0]
				
				for jumpIndex in xrange(0, self.custom_params['jump_length']):
					if (jumpPoints[jumpIndex][0] * lngDir) > (currentMax * lngDir):
						currentIndex = jumpIndex
						currentMax = jumpPoints[jumpIndex][0]

				if currentIndex != -1:
					jumpPoints[currentIndex] = jumpPoints[i][:]
		
		# 确定该方向的交点，为最小的交点
		minLng = jumpPoints[0][0]
		minLat = jumpPoints[0][1]
		originGid = 0
		if x != 0 and y != 0:
			for i in xrange(1, self.custom_params['jump_length']):
				if minLng > jumpPoints[i][0]:
					minLng = jumpPoints[i][0]
					minLat = jumpPoints[i][1]

		# 只取三个交点
		updateOriginGid = False
		for i in xrange(0, self.custom_params['jump_length']):
			ilng = jumpPoints[i][0]
			ilat = jumpPoints[i][1]

			if ilng == minLng and ilat == minLat:
				updateOriginGid = True

			if jumpPoints[i][2] == 0:
				ilat += 0.002 * latDir  # 0.002 为一小点偏量
			else:
				ilng += 0.002 * lngDir

			point = getFormatGID([ilng, ilat])
			gid = point['gid']
			if updateOriginGid:
				updateOriginGid = False
				originGid = gid
			res.append([minLng, minLat, gid])
		
		return {
			'res': res,
			'originGid': originGid
		}
	
	def getNextDirections(self, gids, parentNode, originGid):
		"""
		获取接下来最接近条件的 N 个方向并返回， gids 中的 lng/lat 相同
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
				# 更新经纬度到交点，而非原先网格中点
				self.recDict[gid][subIndex][0] = gids[index][0]
				self.recDict[gid][subIndex][1] = gids[index][1]
				# self.recDict[gid][subIndex][-4] = originGid
				rec = self.recDict[gid][subIndex]
				validation = self.judgeRecordLegality(rec, parentNode)
				if validation:
    				# 处理符合条件的方向，进行分叉检查
					if len(topSearchs) < self.custom_params['tree_num']:
						topSearchs.append(rec[:])
						topSearchAngles.append(validation['mixAngle'])
					else:
						maxAngleIndex = -1
						maxAngle = validation['mixAngle']
						for topIndex in xrange(0, self.custom_params['tree_num']):
							tmpAngle = topSearchAngles[topIndex]
							if maxAngle < tmpAngle:
								maxAngleIndex = topIndex
								maxAngle = tmpAngle
						
						# 替换掉当前最大偏差的方向
						if maxAngleIndex != -1:
							topSearchs[maxAngleIndex] = rec[:]
							topSearchAngles[maxAngleIndex] = validation['mixAngle']
		
		return topSearchs

	def judgeRecordLegality(self, rec, parentNode):
		currentDirection = rec[5:7]
		currentStrength = rec[4]

		parentDirection = [parentNode[5], parentNode[6]]
		# parentStrength = parentNode[4]

		currentAngle = acos(cosVector(parentDirection, currentDirection)) * 180 / pi
		if currentAngle < -self.custom_params['search_angle'] or currentAngle > self.custom_params['search_angle']:
			return False
		
		initDirection = self.currentData['direction']
		accumulatedAngle = acos(cosVector(initDirection, currentDirection)) * 180 / pi
		if accumulatedAngle < -self.custom_params['max_curvation'] or accumulatedAngle > self.custom_params['max_curvation']:
			return False

		if currentStrength < self.currentData['strength'] * self.custom_params['seed_strength']:
			return False
		
		mixAngle = cos(currentAngle) * currentStrength

		return {
			'mixAngle': mixAngle,
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
		# res = None
		gid = str(gid)
		# print "Delete GID %s nodeID %s" % (gid, nodeID)

		nodesLen = len(self.recDict[gid])

		for x in xrange(0, nodesLen):
			if self.recDict[gid][x][-1] == nodeID:
				if len(self.recDict[gid]) == 1:
					# res = self.recDict[gid][0][:]
					self.recDict.pop(gid, None) 
				else: 
					# res = self.recDict[gid][x][:]
					del self.recDict[gid][x] 
				return True
	
	def ifNodeExist(self, gid, nodeID):
		"""
		根据 gid 以及 node 编号删除对应记录
			:param self: 
			:param gid: 
			:param nodeID: 
		"""
		# res = None
		gid = str(gid)
		if gid not in self.recDict.keys():
			return False

		nodesLen = len(self.recDict[gid])

		for x in xrange(0, nodesLen):
			if self.recDict[gid][x][-1] == nodeID:
				return True
		
		return False

	def appendNode(self, data, gid):
		if gid in self.recDict.keys():
			self.recDict[gid].append(data)
		else:
			self.recDict[gid] = [data]

	def outputToFile(self, ofile):
		with open(ofile, 'wb') as f:
			json.dump({
				'res': self.treeMap,
				'len': len(self.treeMap)
			}, f)
		f.close()