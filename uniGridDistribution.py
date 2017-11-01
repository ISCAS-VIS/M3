#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import getopt
import numpy as np
from multiprocessing import Process  # , Manager
# from util.dbopts import connectMongo
from util.preprocess import getCityLocs, formatGridID, formatTime
from util.preprocess import mergeMatrixs, writeMatrixtoFile, writeObjecttoFile


class UnitGridDistribution(object):
	
	def __init__(self, PROP):
		super(UnitGridDistribution, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.DIRECTORY = PROP['DIRECTORY'] 
		self.SUBPATH = PROP['SUBPATH']
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.DAY = PROP['DAY']
		self.HOUR = PROP['HOUR']
		self.TimeIndex = (self.DAY - 185) * 24 + self.HOUR
		self.GRIDSNUM = PROP['GRIDSNUM']
		self.MATRIX = np.array([np.array([x, 0, 0]) for x in xrange(0, PROP['GRIDSNUM'])])  # index, people, number
		self.RECS = {}  # fromgid, togid, people, number
		self.LASTREC = {
			'id': -1,
			'grid': [],
			'travel': ''
		}

	def run(self):
		logging.info('TASK-%d running...' % (self.INDEX))

		oname = 'mres-t%02d-ti%d' % (self.INDEX, self.TimeIndex)
		orecsaname = 'rres-t%02d-ti%d' % (self.INDEX, self.TimeIndex)
		idir = os.path.join(self.DIRECTORY, 'result')
		ofile = os.path.join(self.DIRECTORY, self.SUBPATH, oname)

		for x in xrange(0, 10000):
			number = self.INDEX + 20 * x
			if number > self.INUM:
				break

			ifilename = 'part-%05d' % number
			logging.info('TASK-%d operates file %s' % (self.INDEX, ifilename))
			self.updateDis(os.path.join(idir, ifilename))
		
		# 结果写进文件
		# MATRIX
		writeMatrixtoFile(self.CITY, self.MATRIX, ofile, True)
		# RECORDS
		writeObjecttoFile(self.RECS, os.path.join(self.DIRECTORY, self.SUBPATH, orecsaname))

	def updateDis(self, ifile):
		# 
		resnum = 0
		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				resnum += 1
				linelist = line.split(',')

				grid = formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]])
				fromGid = formatGridID(getCityLocs(self.CITY), [linelist[6], linelist[5]])
				toGrid = formatGridID(getCityLocs(self.CITY), [linelist[8], linelist[7]])
				state = linelist[4]

				# 无效 Travel 状态信息
				if state == 'T' and (line[6] == '0' or line[5] == '0' or line[8] == '0' or line[7] == '0'):
					continue
	
				tmp = formatTime(linelist[1])
				ydayCurrent = tmp['day']
				hourCurrent = tmp['hour']

				# ydayBase = self.WEEK * 7 + 185

				if ydayCurrent == self.DAY:
					self.dealPointState({
						'id': linelist[0],
						'state': state, 
						'day': ydayCurrent,
						# 'admin': admin, 
						'grid': grid, 
						'fromGrid': fromGid, 
						'toGrid': toGrid
					})
					print self.HOUR
		stream.close()
	
	def dealPointState(self, data):
		"""
		将当前记录更新到 distribution 以及存在的旅行记录更新到出行轨迹上
			:param self: 
			:param data: 
		"""
		print "Deal one point with state: " + str(data['state'])
		grid = data['grid']
		id = data['id']
		if data['state'] == 'S':
			# stay 状态更新
			if id == self.LASTREC['id']:
				if grid not in self.LASTREC['grid']:
					self.LASTREC['grid'].append(grid)
					self.MATRIX[grid][1] += 1
			else:
				self.LASTREC['id'] = id
				self.LASTREC['grid'] = [grid]
				self.MATRIX[grid][1] += 1

			self.MATRIX[grid][2] += 1
		elif data['state'] == 'T':
			day = data['day']
			fromGrid = data['fromGrid']
			toGrid = data['toGrid']
			lastidentifier = '%s-%d-%d-%d' % (id, day, fromGrid, toGrid)
			existidentifier = '%d,%d' % (fromGrid, toGrid)

			if existidentifier in self.RECS:
				if lastidentifier != self.LASTREC['travel']:
					self.LASTREC['travel'] = lastidentifier
					self.RECS[existidentifier][2] += 1
				self.RECS[existidentifier][3] += 1
			else:
				self.LASTREC['travel'] = lastidentifier
				self.RECS[existidentifier] = [fromGrid, toGrid, 1, 1]

			
def processTask(x, city, directory, inum, onum, judDay, judHour, GRIDSNUM, subpath): 
	PROP = {
		'INDEX': x, 
		'CITY': city, 
		'DIRECTORY': directory, 
		'INUM': inum, 
		'ONUM': onum,
		'DAY': judDay,
		'HOUR': judHour,
		'GRIDSNUM': GRIDSNUM,
		'SUBPATH': subpath
	}
	task = UnitGridDistribution(PROP)
	task.run()


def usage():
	"""
	使用说明函数
	"""
	print '''Usage Guidance
help	-h	get usage guidance
city	-c	city or region name, such as beijing
directory	-d	the root directory of records and results, such as /China/beijing
inum	-i	number of input files
onum	-o	number of output files
'''


def main(argv):
	"""
	主入口函数
		:param argv: city 表示城市， directory 表示路径， inum 表示输入文件总数， onum 表示输出文件总数， jnum 表示处理进程数，通常和 onum 一致， subpath 为结果存储的子目录名字
	"""
	try:
		opts, args = getopt.getopt(argv, "hc:d:i:o:j:x:y:", ["help", "city=", 'directory=', 'inum=', 'onum=', 'jnum='])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory, inum, onum, jnum, subpath = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records', 3999, 20, 20, 'bj-newvis'
	dayBase, judDay, judHour = 185, 1, 11
	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-c", "--city"):
			city = arg
		elif opt in ("-d", "--directory"):
			directory = arg
		elif opt in ('-i', '--inum'):
			inum = int(arg)
		elif opt in ('-o', '--onum'):
			onum = int(arg)
		elif opt in ('-j', '--jnum'):
			jnum = int(arg)
		elif opt in ('-x'):
			judDay = int(arg)
		elif opt in ('-y'):
			judHour = int(arg)

	judDay += dayBase
	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	# 连接数据获取网格信息，包括总数，具有有效POI的网格
	# conn, db = connectMongo('tdnormal')
	# 固定到北京大小
	GRIDSNUM = 33650
	# conn.close()

	# @多进程运行程序 START
	jobs = []

	for x in xrange(0, jnum):
		# jnum 为进程数
		PROP = {
			'INDEX': x, 
			'CITY': city, 
			'DIRECTORY': directory, 
			'INUM': inum, 
			'ONUM': onum,
			'GRIDSNUM': GRIDSNUM,
			'SUBPATH': subpath
		}

		jobs.append(Process(target=processTask, args=(x, city, directory, inum, onum, judDay, judHour, GRIDSNUM, subpath)))
		jobs[x].start()

	for job in jobs:
		job.join()

	# 处理剩余数据进文件
	# 合并操作
	mergeMatrixs(city, GRIDSNUM, directory, subpath, (judDay - 185) * 24 + judHour)

	# @多进程运行程序 END


if __name__ == '__main__':
	logging.basicConfig(filename='logger-unitGridDistribution.log', level=logging.DEBUG)
	main(sys.argv[1:])