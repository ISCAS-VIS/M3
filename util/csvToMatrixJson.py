#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [hares-jat]
# JSON
# 
# CSV -> Mongo.node.sample.js[ppoint]
# CSV -> Mongo.edge.sample.js[ppedge]

import json
import os


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
		self.type = PROP['type']

	def run(self):
		ofile = os.path.join(self.DIRECTORY, "%sat" % self.FilePrefix)
		
		with open(ofile, 'ab') as res:
			if self.type == 'node':
				json.dump(self.convertNode(), res)
			else:
				json.dump(self.convertEdge(), res)
		res.close()

	def convertNode(self):
		resArr = []
		for x in xrange(0, self.INUM):
			ifile = os.path.join(self.DIRECTORY, '%s%d' % (self.FilePrefix, x))

			with open(ifile, 'rb') as stream:
				for line in stream:
					line = line.strip('\n')
					if line == '':
						continue

					linelist = line.split(',')
					
					resArr.append({
						"pid": linelist[0],
						"dev_num": int(linelist[1]),
						"rec_num": int(linelist[2]),
						"segid": int(linelist[3])
					})
			stream.close()
		
		return resArr

	def convertEdge(self):
		resArr = []
		for x in xrange(0, self.INUM):
			ifile = os.path.join(self.DIRECTORY, '%s%d' % (self.FilePrefix, x))

			with open(ifile, 'rb') as stream:
				for line in stream:
					line = line.strip('\n')
					if line == '':
						continue

					linelist = line.split(',')
					
					resArr.append({
						"from_nid": linelist[0],
						"to_nid": linelist[1],
						"dev_num": int(linelist[2]),
						"rec_num": int(linelist[3]),
						"segid": int(linelist[4])
					})
			stream.close()
		
		return resArr
