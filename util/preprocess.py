#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# 预处理方法类，包括文件存储、数据计算转换等等方法

import numpy as np
import os
import time


def getAdminNumber(admin):
	"""
	获取行政区划对应数字编号
		:param admin: 
	"""

	districts = {
		# beijing 
		'东城区': 1,'西城区':2,'朝阳区':3,'丰台区':4,'石景山区':5,'海淀区':6,'门头沟区':7,'房山区':8,'通州区':9,'顺义区':10,'昌平区':11,'大兴区':12,'怀柔区':13,'平谷区':14,'密云县':15,'延庆县':16,'密云区':15,'延庆区':16
	}
	
	return districts[admin]
	

def getCityLocs(city):
	"""
	城市边界信息列表
		:param city: 
	"""
	newCitylocslist = {
		'beijing': {
			'north': 41.0500,  # 41.050,
			'south': 39.4570,  # 39.457,
			'west': 115.4220,  # 115.422,
			'east': 117.5000,  # 117.500
		}
	}

	return newCitylocslist[city]


def getAdjacentMatrix(args):
	adminAdjacencyMatrix = [
		[],
		[2, 3, 4],
		[1, 3, 4, 6],
		[1, 4, 6, 9, 10, 11, 12],
		[1, 2, 3, 5, 6, 7, 8, 12],
		[4, 6, 7],
		[2, 3, 4, 5, 7, 11],
		[4, 5, 6, 8, 11],
		[7, 8, 12],
		[3, 10, 12],
		[3, 9, 11, 13, 14, 15],
		[3, 6, 7, 10, 13, 16],
		[3, 4, 8, 9],
		[10, 11, 15, 16],
		[10, 15],
		[10, 13, 14],
		[11, 13]
	]

	return adminAdjacencyMatrix

def formatTime(timestr):
	"""格式化时间戳
	
	Args:
		timestr (TYPE): Description
	
	Returns:
		TYPE: Description
	"""
	dateObj = time.localtime(int(timestr))
	
	return {
		'hour': dateObj[3],
		'yday': dateObj[7],
		'wday': dateObj[6]
	}


def formatGridID(locs, point, SPLIT=0.0005):
	"""
	根据经纬度计算城市网格编号
	
	Args:
		locs (TYPE): Description
		point (TYPE): [lng, lat]
	
	Returns:
		TYPE: Description
	"""
	if point[0] == '0' and point[1] == '0':
		return 0
	else:
		# LATNUM = int((locs['north'] - locs['south']) / SPLIT + 1)
		LNGNUM = int( (locs['east'] - locs['west']) / SPLIT + 1 )
		lngind = int( (float(point[0]) - locs['west']) / SPLIT )
		latind = int( (float(point[1]) - locs['south']) / SPLIT )

		return lngind + latind * LNGNUM

def calGridID(locs, id, SPLIT = 0.0005):
	"""
	根据城市网格编号还原经纬度信息
		:param locs: 
		:param id: 
		:param SPLIT=0.05: 
	"""
	
	centerincrement = SPLIT/2.0
	LNGNUM = int((locs['east'] - locs['west']) / SPLIT + 1)
	latind = int(id / LNGNUM)
	lngind = id - latind * LNGNUM
	lat = (locs['south'] + latind * SPLIT)
	lng = (locs['west'] + lngind * SPLIT)
	lngcen = (lng + centerincrement)
	latcen = (lat + centerincrement)

	return "%.3f,%.3f" % (latcen, lngcen)
	# {
	# 	'lat': latcen,
	# 	'lng': lngcen
	# }

def getFormatGID(locs, point, SPLIT = 0.0005):
	"""
	[NEW] 根据经纬度计算城市网格编号
	
	Args:
		locs (TYPE): Description
		point (TYPE): [lng, lat]
	
	Returns:
		TYPE: Description
	"""
	if point[0] == '0' and point[1] == '0':
		return 0
	else:
		# LATNUM = int((locs['north'] - locs['south']) / SPLIT + 1)
		LNGNUM = int( (locs['east'] - locs['west']) / SPLIT + 1 )
		lngind = int( (float(point[0]) - locs['west']) / SPLIT )
		latind = int( (float(point[1]) - locs['south']) / SPLIT )

		return {
			'gid': lngind + latind * LNGNUM,
			'lngind': lngind,
			'latind': latind
		}

def parseFormatGID(locs, id, SPLIT = 0.0005):
	"""
	[NEW] 根据城市网格编号还原经纬度信息，注意：经纬度为中心点信息并非西南角信息
		:param locs: 
		:param id: 
		:param SPLIT=0.05: 
	"""

	centerincrement = SPLIT/2.0
	LNGNUM = int((locs['east'] - locs['west']) / SPLIT + 1)
	latind = 0
	lngind = 0
	nid = 0

	if isinstance(id, int):
		latind = int(id / LNGNUM)
		lngind = id - latind * LNGNUM
		nid = id
	else:
		latind = id['y']
		lngind = id['x']
		nid = lngind + latind * LNGNUM
	
	lat = (locs['south'] + latind * SPLIT)
	lng = (locs['west'] + lngind * SPLIT)
	lngcen = (lng + centerincrement)
	latcen = (lat + centerincrement)

	return {
		'lat': latcen,
		'lng': lngcen,
		'nid': nid,
		'pid': -1,
		'y': latind,
		'x': lngind
	}

def mergeMatrixs(city, GRIDSNUM, directory, subpath, time):
	"""
	合并 CityGrids 信息,分别读取文件,最后需将叠加的信息处理存入一个合并的文件
	
	Args:
	    city (TYPE): Description
	    GRIDSNUM (TYPE): Description
	
	Returns:
	    TYPE: Description
	"""
	
	matrix = np.array([np.array([x, 0.0, 0.0, 0, 0, time]) for x in xrange(0, GRIDSNUM)])
	baseurl = os.path.join(directory, subpath)

	for x in xrange(0, 20):
		with open(os.path.join(baseurl, 'mres-t%02d-ti%d' % (x, time)), 'rb') as stream:
			for each in stream:
				line = np.array(each.split(','), dtype='f')
				id = int(line[0])
				line[0] = 0
				line[5] = 0
				if x != 0:
					line[1] = 0
					line[2] = 0
				matrix[ id ] = np.add(line, matrix[id])
		stream.close()

	resString = []
	for x in xrange(0,GRIDSNUM):
		if matrix[x][3] != 0:
			resString.append(str(int(matrix[x][0])) + ',%.4f' % (matrix[x][1]) + ',%.4f,' % (matrix[x][2]) + str(int(matrix[x][3])) + ',' + str(int(matrix[x][4])) + ',' + str(int(matrix[x][5])))

	if len(resString) != 0:	
		with open(os.path.join(baseurl, 'mares-at'), 'ab') as res:
			res.write('\n'.join(resString) + '\n')
		res.close()

	print "%d lines into matrix file" % len(resString)

def mergeSmallRecords(city, directory, subpath, time):
	"""
	通过逐行读取的方式合并记录数
		:param city: 
		:param directory: 
		:param subpath: 
		:param time: 
	"""
	resString = []

	baseurl = os.path.join(directory, subpath)
	for x in xrange(0, 20):
		with open(os.path.join(baseurl, 'rres-t%02d-ti%d' % (x, time)), 'rb') as stream:
			for each in stream:
				resString.append(each.strip('\n'))
		stream.close()
	
	with open(os.path.join(baseurl, 'rares-at'), 'ab') as res:
		res.write('\n'.join(resString) + '\n')
	res.close()


def mergeMultiProcessMatFiles(directory, subpath, jnum):
	"""
	通过整个文件读取的方式合并记录数，与 mergeLargeRecords 方法的不同点在于该方法不存在分时段的文件遍历，只需要遍历每个进程的唯一结果
		:param directory: 
		:param subpath: 
		:param jnum: 
	"""
	baseurl = os.path.join(directory, subpath)
	
	with open(os.path.join(baseurl, 'hares-at'), 'ab') as output:
		for jobId in xrange(0, 20):
			with open(os.path.join(baseurl, 'hares-j%d' % (jobId)), 'rb') as input:
				output.write(input.read())
			input.close()
	output.close()

def writeMatrixtoFile(city, data, filename, zero):
	"""
	将矩阵转换成逗号分隔的字符串并写入文件, zero 表示是否需要过滤 0， 取值 true表示需要
		:param data: 
		:param filename: 
	"""
	length = len(data)
	resString = []
	for x in xrange(0, length):
		resString.append(str(data[x][0]) + ',' + calGridID(getCityLocs(city), data[x][0], 0.05) + ',' + str(data[x][1]) + ',' + str(data[x][2]) + ',0')

	with open(filename, 'ab') as res:
		res.write('\n'.join(resString))
	res.close()

def writeObjecttoFile(data, filename):
	"""
	将对象转成逗号分隔字符串写入文件，对象不同 key 对应的 value 均为 Array 格式
		:param data: 
		:param filename: 
	"""
	resString = []
	for key in data.iterkeys():
		resString.append(','.join([str(each) for each in data[key]]))
	
	with open(filename, 'ab') as res:
		res.write('\n'.join(resString))
	res.close()

def writeDayMatrixtoFile(index, city, data, opath, day):
	"""
	将进程中单天所有时间单位的网格分布数据转化为字符串存储进文件
		:param index: 
		:param city: 
		:param data: 
		:param opath: 
		:param day: 
	"""
	with open(os.path.join(opath, 'hares-j%d' % (index)), 'ab') as res:
		# 24 时间段
		for x in xrange(0, 24):
			resString = []
			rawLen = len(data[x])
			seg = day * 24 + x

			# 网格数遍历
			for i in xrange(0, rawLen):
				oneRec = data[x][i]

				# 只记录有人定位的有效网格
				if oneRec[1] != 0:
					singleRes = "%d,%s,%d,%d,%d" % (oneRec[0], calGridID(getCityLocs(city), oneRec[0], 0.003), oneRec[1], oneRec[2], seg)
					resString.append(singleRes)

			res.write('\n'.join(resString) + '\n')
	res.close()


