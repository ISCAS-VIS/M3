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
from util.preprocess import getCityLocs, formatGridID, getAdminNumber

class UnitGridDistribution(object):
	
	def __init__(self, PROP):
		super(UnitGridDistribution, self).__init__()

		self.INDEX = PROP['INDEX']
		self.CITY = PROP['CITY'] 
		self.DIRECTORY = PROP['DIRECTORY'] 
		self.INUM = PROP['INUM']
		self.ONUM = PROP['ONUM']
		self.GRIDSNUM = PROP['GRIDSNUM']
		self.MATRIX = np.array([np.array([x, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) for x in xrange(0, PROP['GRIDSNUM'])])


	def run(self):
		logging.info('TASK- running...')

		oname = 't%02d-pred-res' % (self.INDEX)
		idir = os.path.join(self.DIRECTORY, '', self.CITY )
		entropyfile = os.path.join(self.DIRECTORY, 'result', self.CITY, oname)


		for x in xrange(0,10000):
			number = self.INDEX + 20 * x
			if number > self.INUM:
				break

			ifilename = 'res-%05d' % number
			logging.info('TASK-%d operates file %s' % (self.INDEX, ifilename))
			self.updateDis(os.path.join(idir, ifilename))
	
	def updateDis(ifile):
		# 
		resnum = 0
		with open(ifile, 'rb') as stream:
			for line in stream:
				resnum += 1
				linelist = line.strip('\n').split(',')
				index = int(linelist[0]) % self.GRIDSNUM

				# reslist[ index ] += linelist[0] + ',' + formatTime(linelist[1]) + ',' + formatAdmin(linelist[4]) + ',' + formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]]) + '\n'
				grid = formatGridID(getCityLocs(self.CITY), [linelist[3], linelist[2]])
				admin = formatAdmin(linelist[4])

				# 

		stream.close()

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

	city, directory, inum, onum, jnum = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records/beijing', 3999, 20, 20
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
	conn, db = connectMongo('tdnormal')
	GRIDSNUM = db['newgrids_%s' % city].count()
	conn.close()

	# @多进程运行程序 START
	manager = Manager()
	jobs = []

	tasks = []
	for x in xrange(0, jnum):
		# jnum 为进程数
		PROP = {
			INDEX: x, 
			CITY: city, 
			DIRECTORY: directory, 
			INUM: inum, 
			ONUM: onum,
			GRIDSNUM: GRIDSNUM
		}

		jobs.append( Process(target=processTask, args=(PROP)) )
		jobs[x].start()

	for job in jobs:
		job.join()

	# 处理剩余数据进文件
	for x in xrange(0, jnum):
		# 合并操作
	# @多进程运行程序 END

if __name__ == '__main__':
	logging.basicConfig(filename='logger-unitGridDistribution.log', level=logging.DEBUG)
	main(sys.argv[1:])