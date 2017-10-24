#!/usr/bin/env python
# -*- coding: utf-8 -*-

def getAdminNumber(admin):
	# 获取行政区划对应数字编号
	districts = {
		# beijing 
		u'东城区': 1,u'西城区':2,u'朝阳区':3,u'丰台区':4,u'石景山区':5,u'海淀区':6,u'门头沟区':7,u'房山区':8,u'通州区':9,u'顺义区':10,u'昌平区':11,u'大兴区':12,u'怀柔区':13,u'平谷区':14,u'密云县':15,u'延庆县':16,

		# tianjin
		u'和平区':17,u'河东区':18,u'河西区':19,u'南开区':20,u'河北区':21,u'红桥区':22,u'东丽区':23,u'西青区':24,u'津南区':25,u'北辰区':26,u'武清区':27,u'宝坻区':28,u'滨海新区':29,u'宁河县':30,u'静海县':31,u'蓟县':32,

		# zhangjiakou
		u'桥东区':33,u'桥西区':34,u'宣化县':35,u'宣化区':35,u'下花园区':36,u'万全县':37,u'崇礼县':38,u'张北县':39,u'康保县':40,u'沽源县':41,u'尚义县':42,u'蔚县':43,u'阳原县':44,u'怀安县':45,u'怀来县':46,u'涿鹿县':47,u'赤城县':48,

		# tangshan
		u'路南区':49,u'路北区':50,u'古冶区':51,u'开平区':52,u'丰南区':53,u'丰润区':54,u'曹妃甸区':55,u'滦县':56,u'滦南县':57,u'乐亭县':58,u'迁西县':59,u'玉田县':60,u'迁安市':61,u'遵化市':62,u'唐海县':63
	}
	
	return str( districts[admin] )
	
def getCityLocs(city):
	# 城市边界信息列表
	newCitylocslist = {
		'beijing': {
			'north': 41.055,
			'south': 39.445,
			'west': 115.422,
			'east': 117.515
		},
		'tianjin': {
			'north': 40.254,
			'south': 38.537,
			'west': 116.691,
			'east': 118.087
		},
		'zhangjiakou': {
			'north': 42.139,
			'south': 39.546,
			'west': 113.807,
			'east': 116.400
		},
		'tangshan': {
			'north': 40.457,
			'south': 38.908,
			'west': 117.488,
			'east': 119.306
		}
	}

	return newCitylocslist[city]

def formatTime(timestr):
	"""格式化时间戳
	
	Args:
		timestr (TYPE): Description
	
	Returns:
		TYPE: Description
	"""
	dateObj = time.localtime( int(timestr)/1000.0 )
	
	date = time.strftime("%m-%d", dateObj)
	hourmin = time.strftime("%H:%M", dateObj)
	day = time.strftime("%w", dateObj)
	period = str( getTimePeriod( time.strftime("%H", dateObj) ) )

	return date + ',' + hourmin + ',' + day + ',' + period

def formatGridID(locs, point, SPLIT = 0.003):
	"""根据经纬度计算城市网格编号
	
	Args:
		locs (TYPE): Description
		point (TYPE): [lng, lat]
	
	Returns:
		TYPE: Description
	"""
	# LATNUM = int((locs['north'] - locs['south']) / SPLIT + 1)
	LNGNUM = int( (locs['east'] - locs['west']) / SPLIT + 1 )
	lngind = int( (float(point[0]) - locs['west']) / SPLIT )
	latind = int( (float(point[1]) - locs['south']) / SPLIT )

	return str(lngind + latind * LNGNUM)
