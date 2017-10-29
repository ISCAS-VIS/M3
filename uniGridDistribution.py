#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import getopt
import numpy as np
from multiprocessing import Process, Manager
from util.dbopts import connectMongo
from util.preprocess import getCityLocs, formatGridID, getAdminNumber, formatTime
from util.preprocess import mergeMatrixs

class UnitGridDistribution(object):
	
	def __init__(self, PROP):
		super(UnitGridDistribution, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.DIRECTORY = PROP['DIRECTORY'] 
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.GRIDSNUM = PROP['GRIDSNUM']
		self.WEEK = PROP['WEEK']
		self.MATRIX = np.array([np.array([x, 0, 0]) for x in xrange(0, PROP['GRIDSNUM'])]) # index, people, number
		self.RECS = ''
		self.LASTREC = {
			'id': -1,
			'grid': [],
			'travel': ''
		}

	def run(self):
		logging.info('TASK-%d running...' % (self.INDEX))

		oname = 't%02d-pred-res' % (self.INDEX)
		idir = os.path.join(self.DIRECTORY, '', self.CITY)
		ofile = os.path.join(self.DIRECTORY, 'result', self.CITY, oname)

		for x in xrange(0, 10000):
			number = self.INDEX + 20 * x
			if number > self.INUM:
				break

			ifilename = 'res-%05d' % number
			logging.info('TASK-%d operates file %s' % (self.INDEX, ifilename))
			self.updateDis(os.path.join(idir, ifilename))
		
		# 结果写进文件
		# MATRIX
		# RECORDS
	
	def updateDis(self, ifile):
		# 
		resnum = 0
		with open(ifile, 'rb') as stream:
			for line in stream:
				line = line.strip('\n')
				resnum += 1
				linelist = line.split(',')

				grid = formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]])
				fromGid = formatGridID(getCityLocs(self.CITY), [linelist[7], linelist[6]])
				toGrid = formatGridID(getCityLocs(self.CITY), [linelist[9], linelist[8]])
				admin = getAdminNumber(linelist[4])
				state = linelist[5]
				ydayCurrent = formatTime(linelist[1])
				ydayBase = self.WEEK * 7 + 185

				if ydayCurrent >= ydayBase and ydayCurrent < (ydayBase + 7):
					self.dealPointState({
						'id': linelist[0],
						'state': state, 
						'day': ydayCurrent,
						'admin': admin, 
						'grid': grid, 
						'fromGrid': fromGid, 
						'toGrid': toGrid,
						'string': line
					})
		stream.close()
	
	def dealPointState(self, data):
		"""
		将当前记录更新到 distribution 以及存在的旅行记录更新到出行轨迹上
			:param self: 
			:param data: 
		"""
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
			identifier = '%s-%s-$s' % (day, fromGrid, toGrid)
			if identifier != self.LASTREC['travel']:
				self.LASTREC['travel'] = identifier
				self.RECS += '%s,%d,%s,%s,%s,%s\n' % (id, data['day'], grid, data['admin'], fromGrid, toGrid)
			


def processTask(PROP): 
	task = augmentRawDatainMultiProcess(PROP)
	task.run()


def usage():
	print '''Usage Guidance
help	-h	get usage guidance
city	-c	city or region name, such as beijing
directory	-d	the root directory of records and results, such as /China/beijing
inum	-i	number of input files
onum	-o	number of output files
'''


def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hc:d:i:o:", ["help", "city=", 'directory=', 'inum=', 'onum='])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory, inum, onum, jnum, weekSep = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records/beijing', 3999, 20, 20, 0
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
			'WEEK': weekSep
		}

		jobs.append(Process(target=processTask, args=(PROP)))
		jobs[x].start()

	for job in jobs:
		job.join()

	# 处理剩余数据进文件
	# 合并操作
	mergeMatrixs()
	

	# @多进程运行程序 END


if __name__ == '__main__':
	logging.basicConfig(filename='logger-unitGridDistribution.log', level=logging.DEBUG)
	main(sys.argv[1:])