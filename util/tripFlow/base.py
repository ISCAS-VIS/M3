#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

from math import radians, cos, sin, asin, sqrt  

def getRealDistance(lon1, lat1, lon2, lat2):  # 经度1，纬度1，经度2，纬度2 （十进制度数）  
	""" 
	Calculate the great circle distance between two points  
	on the earth (specified in decimal degrees) 
	"""  
	# 将十进制度数转化为弧度
	lon1 = float(lon1)
	lat1 = float(lat1)
	lon2 = float(lon2)
	lat2 = float(lat2)
	
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])  

	# haversine公式  
	dlon = lon2 - lon1   
	dlat = lat2 - lat1   
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2  
	c = 2 * asin(sqrt(a))   
	r = 6371  # 地球平均半径，单位为公里  
	return c * r * 1000.0 


def getFormatGID(point, LngSPLIT=0.0064, LatSPLIT=0.005, locs={
	'north': 41.0500,  # 41.050,
	'south': 39.4570,  # 39.457,
	'west': 115.4220,  # 115.422,
	'east': 117.5000,  # 117.500
}):
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
		LNGNUM = int( (locs['east'] - locs['west']) / LngSPLIT + 1 )
		lngind = int( (float(point[0]) - locs['west']) / LngSPLIT )
		latind = int( (float(point[1]) - locs['south']) / LatSPLIT )

		return {
			'gid': lngind + latind * LNGNUM,
			'lngind': lngind,
			'latind': latind
		}

def parseFormatGID(id, direction, LngSPLIT=0.0064, LatSPLIT=0.005, locs={
	'north': 41.0500,  # 41.050,
	'south': 39.4570,  # 39.457,
	'west': 115.4220,  # 115.422,
	'east': 117.5000,  # 117.500
}):
	"""
	[NEW] 根据城市网格编号还原经纬度信息，注意：经纬度为中心点信息并非西南角信息
		:param locs: 
		:param id: 
		:param SPLIT=0.05: 
	"""

	LNGNUM = int((locs['east'] - locs['west']) / LngSPLIT + 1)
	latind = 0
	lngind = 0
	nid = 0

	latind = int(id / LNGNUM)
	lngind = id - latind * LNGNUM
	nid = id
	
	lat = (locs['south'] + latind * LatSPLIT)
	lng = (locs['west'] + lngind * LngSPLIT)
	lngcen = (lng + LngSPLIT/2.0)
	latcen = (lat + LatSPLIT/2.0)
	dlineDict = {
		'n': lat + LatSPLIT,
		's': lat,
		'e': lng + LngSPLIT,
		'w': lng
	}

	return {
		'lat': latcen,
		'lng': lngcen,
		'nid': nid,
		'pid': -1,
		'y': latind,
		'x': lngind,
		'dlinePoint': dlineDict[direction]
	}


def getDirection(fPoint, tPoint):
	# 获取方向信息
	# [Lng, Lat]
	fromLat = float(fPoint[1])
	fromLng = float(fPoint[0])
	toLat = float(tPoint[1])
	toLng = float(tPoint[0])

	absLat = abs(toLat-fromLat)
	absLng = abs(toLng-fromLng)

	if toLng >= fromLng and absLng > absLat:  # 向右半边运动
		return 'e'
	elif toLng < fromLng and absLng > absLat:
		return 'w'
	elif toLat >= fromLat and absLng > absLat:
		return 'n'
	else:
		return 's'
    		
def calLineIntersection():
	# y = 