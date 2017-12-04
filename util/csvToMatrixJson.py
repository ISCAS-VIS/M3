#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [hares-jat]
# JSON

import logging
import json
import os
from util.preprocess import getCityLocs, formatGridID, formatTime

class csvToMatrixJson(object):
	"""
	Convert CSV file to JSON with given params
		:param object: 
	"""
	def __init__(self, PROP):
		super(csvToMatrixJson, self).__init__()

		self.keys = PROP['keys']  # 暂未使用，通用性未考虑
		self.INUM = PROP['INUM']
		self.DIRECTORY = PROP['DIRECTORY']
		self.FilePrefix = PROP['FilePrefix']

	def run(self):
		resArr = []
		ofile = os.path.join(self.DIRECTORY, "%sat" % self.FilePrefix)
		for x in xrange(0, self.INUM):
			ifile = os.path.join(self.DIRECTORY, '%s%d' % (self.FilePrefix, x))

			with open(ifile, 'rb') as stream:
				for line in stream:
					line = line.strip('\n')
					if line == '':
						continue

					linelist = line.split(',')
					
					# tmpObject, index = {}, 0
					# for each in self.keys:
					# 	tmpObject[each] = linelist[index]

					resArr.append({
						"pid": linelist[0],
						"dev_num": int(linelist[1]),
						"rec_num": int(linelist[2]),
						"segid": int(linelist[3])
					})
			stream.close()
		
		with open(ofile, 'ab') as res:
			json.dump(resArr, res)
		res.close()
