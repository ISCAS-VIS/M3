#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# input
# [gLng, gLat, gdirStr(from or to), speed, recordNum, dLng, dLat, seg(hour ID)]


import os 
import json
# import numpy as np
import copy
from math import acos, cos, pi, floor
from util.tripFlow.base import getFormatGID
from util.tripFlow.base import parseFormatGID
from util.tripFlow.base import cosVector
from util.tripFlow.base import getRealDistance


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
		# 	'jump_length': 0,
		# 	"seed_unit": 0,
		# 	"grid_dirnum": 0,
		# }
		self.cateKeys = {0: 'from', 1: 'to'}
		self.currentCateName = 'from'

		self.entries = {
			'from': [],
			'to': []
		}  # 起始点集合
		self.currentData = {
			'from': {},
			'to': {}
		} 
		self.keepTreeStructList = {
			'from': [],
			'to': []
		}
		
		self.recDict = {
			'from': {},
			'to': {}
		}  # record 字典，key 值为 gid 字符串
		self.treeMap = {
			'from': [],
			'to': []
		}  # 存储的 treemap 数组

	def run(self):
		delta = "%.2f" % self.custom_params['delta'] 
		input_file = 'mcres-%s-%d-%s' % (self.dataType, self.index, delta)
		# input_filename = 'mcres-%d' % (self.index)
		p1 = self.custom_params['tree_num']
		p2 = self.custom_params['search_angle']
		p3 = self.custom_params['seed_strength']
		p4 = self.custom_params['tree_width']
		p5 = self.custom_params['jump_length']
		p6 = self.custom_params['seed_unit']
		p7 = self.custom_params['grid_dirnum']
		output_suffix = "%.2f_%d_%.2f_%d_%d_%s_%d" % (p1, p2, p3, p4, p5, p6, p7)
		
		output_file = 'tmres-%s-%d_%s' % (self.dataType, self.index, output_suffix)
		ifile = os.path.join(self.INPUT_PATH, input_file)
		ofile = os.path.join(self.OUTPUT_PATH, output_file)
		if not os.path.isfile(ifile):
			return False

		totalNum = self.iterateFile(ifile)
		roundTreeNum = int(totalNum * self.custom_params['tree_num'])
		usedNum = 0
		actualTreeNum = 0

		for dirKey, cateName in self.cateKeys.iteritems():
			self.currentCateName = cateName
			for x in xrange(0, roundTreeNum):
				# 初始化工作
				if len(self.entries[cateName]) == 0:
					break

				element = self.entries[cateName].pop()
				self.currentData[cateName] = {
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
				
				actualTreeNum += 1
				self.deleteNode(gid, element[-1])
				res = {
					"root": {
						"id": self.treeNodesID,
						"lng": element[0],
						"lat": element[1],
						"num": 0,
						"speed": 0,
						"dis": 0
					},
					"children": []
				}
				childs = self.BFSOneTreeMap(element[:], element[4], [])
				res['children'] = childs
				self.treeMap[cateName].append(res)
				self.treeNodesID += 1

				currentEdgeCount = self.currentData[cateName]['count'] + 1
				print "[D-%s]#%d TMNodes Number: %d" % (cateName, x, currentEdgeCount)
				usedNum += currentEdgeCount
		
		if totalNum == 0 or actualTreeNum == 0:
			print "Zero Result!"
			return 0

		print "Edges Uesd Rate: %.4f" % (float(usedNum)/totalNum)
		print "Tree Average Edges Number: %.4f" % (float(usedNum)/actualTreeNum)
		self.outputToFile(ofile)

	def iterateFile(self, ifile):
		"""
		遍历文件，构建 gid-record 字典以及种子方向列表
			:param self: 
			:param ifile: 
		"""
		cateKeys = self.cateKeys

		seedUnit = self.custom_params['seed_unit']
		gridDirNum = self.custom_params['grid_dirnum']

		# 网格列表以及网格与所属记录的对应字典
		gridDevNumDict, gridDevNumList = { 'from': {}, 'to': {} }, { 'from': [], 'to': [] }
		gridRecsDict = { 'from': {}, 'to': {} }

		with open(ifile, 'rb') as f:
			nodeID = 0
			for line in f:
				line = line.strip('\n')
				linelist = line.split(',')

				# 
				linelist[0] = float(linelist[0])
				linelist[1] = float(linelist[1])
				formatGID = getFormatGID([linelist[0], linelist[1]])
				# {gid, lngind, latind} = formatGID
				gid = formatGID['gid']
				lngind = formatGID['lngind']
				latind = formatGID['latind']
				gdirStr = linelist[2]

				linelist[6] = float(linelist[6])
				linelist[5] = float(linelist[5])
				
				linelist[3] = float(linelist[3])
				linelist[4] = int(linelist[4])

				linelist.extend([gid, lngind, latind, nodeID])
				nodeID += 1

				strGID = str(gid)
				if strGID in gridDevNumDict[gdirStr].keys():
					gridDevNumDict[gdirStr][strGID] += linelist[4]
					gridRecsDict[gdirStr][strGID].append(linelist[:])
				else:
					gridDevNumDict[gdirStr][strGID] = linelist[4]
					gridRecsDict[gdirStr][strGID] = [linelist[:]]

				# res[gdirStr].append(linelist[:])
		f.close()

		# 构建 grid 排序数组
		for dirKey, cateName in cateKeys.iteritems():
			for key, val in gridDevNumDict[cateName].iteritems():
				gridDevNumList[cateName].append([key, val])

		# 前 N 方向筛选
		N = self.custom_params['grid_dirnum']
		if N == -1:
			N = 999

		res = {
			'from': [],
			'to': []
		}

		for dirKey, cateName in cateKeys.iteritems():
			for gid, reclist in gridRecsDict[cateName].iteritems():
				reclist.sort(key=lambda x:x[4], reverse=True)
				if len(reclist) >= N:
					res[cateName] += reclist[0:N]
				else:
					res[cateName] += reclist[:]
		
		# 分 from/to 方向，按照 deviceNum 排序
		for dirKey, cateName in cateKeys.iteritems():
			nodeLen = len(res[cateName])
			for i in xrange(0, nodeLen):
				currentLine = res[cateName][i]
				gidStr = str(currentLine[-4])
				if gidStr in self.recDict[cateName].keys():
					self.recDict[cateName][gidStr].append(currentLine)
				else:
					self.recDict[cateName][gidStr] = [currentLine]
				
		resInAll = copy.deepcopy(res)
		resByGID = copy.deepcopy(gridRecsDict)
		self.pickUpSeeds(resInAll, gridDevNumList, resByGID)

		return int(nodeID/2)
	
	def pickUpSeeds(self, resInAll, gridDevNumList, resByGID):
		cateKeys = self.cateKeys

		# basic 方式筛选种子
		for dirKey, cateName in cateKeys.iteritems():
			if self.custom_params['seed_unit'] == 'basic':
				resInAll[cateName].sort(key=lambda x:x[4], reverse=True)
				
				nodeLen = len(resInAll[cateName])
				treeNum = floor(self.custom_params['tree_num'] * nodeLen)
				for i in xrange(0, nodeLen):
					currentLine = resInAll[cateName][i]

					if i < treeNum:
						self.entries[cateName].append(currentLine[:])
			elif self.custom_params['seed_unit'] == 'grid':
				gridDevNumList[cateName].sort(key=lambda x:x[1], reverse=True)

				gridLen = len(gridDevNumList[cateName])
				treeNum = int(floor(self.custom_params['tree_num'] * gridLen))
				
				for i in xrange(0, treeNum):
					gid = gridDevNumList[cateName][i][0]
					self.entries[cateName] += resByGID[cateName][gid][:]


	def BFSOneTreeMap(self, parentNode, recordNum=0, treeQueue=[]):
		cateName = self.currentCateName

		self.treeNodesID += 1
		
		for each in treeQueue:
			id = "%d-%s" % (each[-4], each[-1])
			if id not in self.keepTreeStructList[cateName]:
				self.keepTreeStructList[cateName].append(id)

		queue = []
		# parentNRN = parentNode[4]
		# nothing = True

		# 六个交点计算，得出三个 gid，然后匹配方向加入 queue
		point = [parentNode[0], parentNode[1], parentNode[-4]]
		direction = [parentNode[5], parentNode[6]]
		tmpStepRes = self.getNextGIDs(point, direction)
		gids = tmpStepRes['res']
		intersectionPoint = tmpStepRes['endPoints']
		# originGid = tmpStepRes['originGid']
		queue += self.getNextDirections(gids, parentNode)
		queueCopy = queue[:]

		res = []

		# BFS Looping Condition
		while queue:
			vertex = queue.pop(0)
			
			gidStr = str(vertex[-4])
			nodeID = vertex[-1]

			treeStructID = "%s-%s" % (gidStr, nodeID)
			if treeStructID in self.keepTreeStructList[cateName]:
				continue
			
			self.treeNodesID += 1
			self.currentData[cateName]['count'] += 1 

			# 距离判断 START
			dis = getRealDistance(parentNode[0], parentNode[1], vertex[0], vertex[1])
			if dis > self.custom_params['max_distance'] * 1000:
				continue
			# 距离判断 END

			subres = {
				"root": {
					"id": self.treeNodesID,
					"lng": vertex[0],
					"lat": vertex[1],
					"num": parentNode[4],
					"speed": parentNode[3]
				},
				"children": [  ]
			}

			node = self.deleteNode(gidStr, nodeID)
			childs = self.BFSOneTreeMap(vertex, vertex[4], queueCopy)
			
			# nothing = False
			subres['children'] = childs
			res.append(subres)

		if len(res) == 0:
			self.treeNodesID += 1
			self.currentData[cateName]['count'] += 1 
			res.append({
				"root": {
					"id": self.treeNodesID,
					"lng": intersectionPoint[0],
					"lat": intersectionPoint[1],
					"num": parentNode[4],
					"speed": parentNode[3]
				}
			})
		# result
		# if nothing:
		# 	del res['children']
		
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

		# 存储所有交点数据
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
			for i in xrange(self.custom_params['jump_length'], self.custom_params['jump_length'] * 2):
				currentIndex = -1
				currentMax = jumpPoints[i][0]
				
				for jumpIndex in xrange(0, self.custom_params['jump_length']):
					if (jumpPoints[jumpIndex][0] * lngDir) > (currentMax * lngDir):
						currentIndex = jumpIndex
						currentMax = jumpPoints[jumpIndex][0]

				if currentIndex != -1:
					jumpPoints[currentIndex] = jumpPoints[i][:]
		
		# 确定该方向离圆心最小的交点
		minLng = jumpPoints[0][0]
		minLat = jumpPoints[0][1]
		originGid = 0
		if x != 0 and y != 0:
			for i in xrange(1, self.custom_params['jump_length']):
				if minLng * lngDir > jumpPoints[i][0] * lngDir:
					minLng = jumpPoints[i][0]
					minLat = jumpPoints[i][1]

		# 只取三个交点
		updateOriginGid = False
		for i in xrange(0, self.custom_params['jump_length']):
			ilng = jumpPoints[i][0]
			ilat = jumpPoints[i][1]

			# if ilng == minLng and ilat == minLat:
			# 	updateOriginGid = True

			if jumpPoints[i][2] == 0:
				ilat += 0.002 * latDir  # 0.002 为一小点偏量，使交点在对应网格内而不至于只卡在边界上
			else:
				ilng += 0.002 * lngDir

			point = getFormatGID([ilng, ilat])
			gid = point['gid']
			# if updateOriginGid:
			# 	updateOriginGid = False
			# 	originGid = gid
			res.append([ilng, ilat, gid])
		
		return {
			'res': res,
			'endPoints': [minLng, minLat]
			# 'originGid': originGid
		}
	
	def getNextDirections(self, gids, parentNode):
		"""
		获取接下来最接近条件的 N 个方向并返回， gids 中的 lng/lat 相同
			:param self: 
			:param gids: 
			:param parentNode: 
		"""
		cateName = self.currentCateName
		topSearchs = []
		topSearchAngles = []
		res = []
		gidsLen = len(gids)

		# 每个网格遍历
		for index in xrange(0, gidsLen):
			gid = str(gids[index][2])
			if gid not in self.recDict[cateName].keys():
				continue
			recsLen = len(self.recDict[cateName][gid])

			# 每个网格中的方向遍历
			for subIndex in xrange(0, recsLen):
				# 更新经纬度到交点，而非原先网格中点
				# self.recDict[cateName][gid][subIndex][0] = gids[index][0]
				# self.recDict[cateName][gid][subIndex][1] = gids[index][1]
				rec = self.recDict[cateName][gid][subIndex]
				validation = self.judgeRecordLegality(rec, parentNode)
				if validation:
    				# 处理符合条件的方向，进行分叉检查
					if len(topSearchs) < self.custom_params['tree_width']:
						topSearchs.append(rec[:])
						topSearchAngles.append(validation['mixAngle'])
					else:
						maxAngleIndex = -1
						maxAngle = validation['mixAngle']
						for topIndex in xrange(0, self.custom_params['tree_width']):
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
		cateName = self.currentCateName
		currentDirection = rec[5:7]
		currentStrength = rec[4]

		parentDirection = [parentNode[5], parentNode[6]]
		# parentStrength = parentNode[4]

		currentAngle = acos(cosVector(parentDirection, currentDirection)) * 180 / pi
		if currentAngle < -self.custom_params['search_angle'] or currentAngle > self.custom_params['search_angle']:
			return False
		
		initDirection = self.currentData[cateName]['direction']
		accumulatedAngle = acos(cosVector(initDirection, currentDirection)) * 180 / pi
		if accumulatedAngle < -self.custom_params['max_curvation'] or accumulatedAngle > self.custom_params['max_curvation']:
			return False

		if currentStrength < self.currentData[cateName]['strength'] * self.custom_params['seed_strength']:
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
		cateName = self.currentCateName
		gid = str(gid)
		# print "Delete GID %s nodeID %s" % (gid, nodeID)

		nodesLen = len(self.recDict[cateName][gid])

		for x in xrange(0, nodesLen):
			if self.recDict[cateName][gid][x][-1] == nodeID:
				if len(self.recDict[cateName][gid]) == 1:
					# res = self.recDict[gid][0][:]
					self.recDict[cateName].pop(gid, None) 
				else: 
					# res = self.recDict[gid][x][:]
					del self.recDict[cateName][gid][x] 
				return True
	
	def ifNodeExist(self, gid, nodeID):
		"""
		根据 gid 以及 node 编号删除对应记录
			:param self: 
			:param gid: 
			:param nodeID: 
		"""
		cateName = self.currentCateName
		gid = str(gid)
		if gid not in self.recDict[cateName].keys():
			return False

		nodesLen = len(self.recDict[cateName][gid])

		for x in xrange(0, nodesLen):
			if self.recDict[cateName][gid][x][-1] == nodeID:
				return True
		
		return False

	def appendNode(self, data, gid):
		cateName = self.currentCateName

		if gid in self.recDict[cateName].keys():
			self.recDict[cateName][gid].append(data)
		else:
			self.recDict[cateName][gid] = [data]

	def outputToFile(self, ofile):
		with open(ofile, 'wb') as f:
			json.dump({
				'res': self.treeMap,
				'len': len(self.treeMap['from']) + len(self.treeMap['to'])
			}, f)
		f.close()