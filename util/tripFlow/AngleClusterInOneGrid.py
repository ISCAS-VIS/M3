#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# input [JSON]
# [gLng, gLat, gid, from/to, speed, direction, angle]


import os 
import json
# import copy
from math import sin, cos
from util.tripFlow.LinkList import LinkList


class AngleClusterInOneGrid(object):
	def __init__(self, PROP):
		super(AngleClusterInOneGrid, self).__init__()
		self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], 'bj-byhour-rec')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'bj-byhour-res')
		self.index = PROP['index']
		self.dbLabel = []
		self.angleList = []

		self.eps = PROP['eps']
		self.min_samples = PROP['min_samples']
		self.dbscanBaseNum = 0
		self.noiseNum = 0
	
	def run(self):
		ifilename = 'triprec-smooth-%d.json' % (self.index)
		ifile = os.path.join(self.INPUT_PATH, ifilename)
		with open(ifile, 'rb') as f:
			edgesData = json.load(f)
			self.constructInput(edgesData)
		f.close()

		# self.constructInput()
		cres = self.clusterAngles()
		self.dbLabel = cres['labels']
		self.noiseNum = cres['noiseNum']
		self.outputToFile()

	def constructInput(self, edgesData):
		cate = 'from'
		count = 0

		for key, itemlist in edgesData[cate].items():
			subLen = len(itemlist)
			for x in xrange(0, subLen):
				linelist = itemlist[x].split(',')
				angle = int(float(linelist[6]))
				self.angleList.append([angle, 1])
				count += 1
		
		print "Total angle number: %d" % (count)

	def clusterAngles(self):
		angleList = [0 for x in xrange(0, 720)]
		labelList = {}
		res = []
		angleArray = self.angleList
		arrayLen = len(angleArray)

		N = self.min_samples
		rho = arrayLen * self.eps / 360  # 每度至少拥有的 trip 数量

		for x in xrange(0, arrayLen):
			angleList[angleArray[x][0]] += 1
			angleList[angleArray[x][0] + 360] += 1
		
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

		cIndex = sIndex
		clusteID = 0
		# print "Start from %d" % cIndex
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
					tRho = (tmpNum + tmptfNum) / (rAngle - tmpItem['index'] + 1)
					if tRho >= rho:
						tmplIndex -= 1
						tmplAngle = tmpItem['index']
						cRho = tRho
						tmptfNum += tmpNum
						endFlag = False
					else:
						break
				
				while tmprIndex < (listLen-1):
					tmpItem = ALL.getitem(tmprIndex+1)
					tmpNum = tmpItem['data']
					tRho = (tmpNum + tmptfNum) / (tmpItem['index'] - lAngle + 1)
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
					endFlag = True
			
			# 满足 cluster 条件，否则放弃
			if tfNum >= N:
				for x in xrange(rIndex, lIndex-1, -1):
					angle = ALL.getitem(x)['index'] % 360
					angle = str(angle)
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
					
					# print "left to the last iteration"
				
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
						lIndex -= 1
					else:
						x += 1
				
				# 只有聚类成功才增加 clusteID
				clusteID += 1
			else:
				cIndex += 1

			# 扫尾工作
			listLen = ALL.getlength()

		# 返回结果计算
		noiseNum = 0
		for x in xrange(0, arrayLen):
			angle = str(angleArray[x][0])
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
		# 从前向后遍历，得到每个类别的起止方向，并计算对应流量所占百分比
		ores = []
		totalLen = len(self.dbLabel)
		
		# 初始化
		id = 0
		currentID = -1
		fromAngle = -1
		toAngle = -1
		currentNum  = 0

		while id < totalLen:
			CID = self.dbLabel[id]

			# 每一次对噪声后的类别开端第一个元素进行初始化
			if currentID == -1 and CID != -1:
				currentID = CID
				fromAngle = self.angleList[id][0]
			
			rate = float(currentNum)/totalLen
			singleItem = {
				'x1': sin(fromAngle),
				'y1': cos(fromAngle),
				'x2': sin(toAngle),
				'y2': cos(toAngle),
				'rate': rate,
				'fromAngle': fromAngle,
				'toAngle': toAngle
			}

			# 根据当前聚类编号进行行为判断
			if CID == currentID:
				currentNum += 1
				toAngle = self.angleList[id][0]
			elif CID != -1:
				ores.append(singleItem)

				currentID = CID
				currentNum = 1
				fromAngle = self.angleList[id][0]
				toAngle = self.angleList[id][0]
			elif CID == -1:
				if currentNum != 0:
					ores.append(singleItem)

					currentID = -1
					currentNum = 0
					fromAngle = -1
					toAngle = -1
			
			id += 1

		# 清零操作
		if currentNum != 0:
			rate = float(currentNum)/totalLen
			ores.append({
				'x1': sin(fromAngle),
				'y1': cos(fromAngle),
				'x2': sin(toAngle),
				'y2': cos(toAngle),
				'rate': rate,
				'fromAngle': fromAngle,
				'toAngle': toAngle
			})

		print "Total numbers: %d" % (self.dbscanBaseNum)
		print "Total noise number: %d" % (self.noiseNum)
		print len(ores)

		# 结果存入 JSON 文件
		ofilename = 'acres-%d' % (self.index)
		ofile = os.path.join(self.OUTPUT_PATH, ofilename)
		with open(ofile, 'wb') as f:
			json.dump(ores, f)
		f.close()