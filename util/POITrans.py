#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [POI-Mongo-Import]
# JSON
# 

import json
import os


class POIJson(object):
	"""
	将原始 JSON 文件转化成预定格式、适合导入 mongoDB 的 GeoJSON 格式
		:param object: 
	"""
	def __init__(self, PROP):
		super(POIJson, self).__init__()
		self.POITypes = PROP['POITypes']
		self.basepath = PROP['basepath']
		self.RES = []

	def run(self):
		print 'Start to process POI files...'
		for each in self.POITypes:
			input = os.path.join(self.basepath, '%s.json' % (each))
			output = os.path.join(self.basepath, 'mongoUTF8.json')
			self.iterateFile({
				'input': input
			})
		self.outputRes({
			'output': output
		})

	def iterateFile(self, props):
		"""
		遍历文件中 POI 对象并整理成 mongo 导入所需 JSON 形式
			:param self: 
			:param props: 
		"""
		count = 1

		print "%s loading..." % (props['input'])
		with open(props['input'], 'rb') as stream:
			data = json.loads(stream.read().decode('utf-8-sig'))
			ptype = data['type']
			geoCollection = data['poi']

			for each in geoCollection:
				self.RES.append({
					"pid": "%s%s" % (ptype, each['id']),
					"coordinates": each['coordinates'],
					"properties": {
						"district": each['district'],
						"ptype": ptype,
						"name": each['name'],
						"business_area": each['business_area'],
						"address": each['address'],
						"cp": each['cp']
					}
				})

				count += 1
			print "Total %d POIs" % count
		stream.close()

	def outputRes(self, props):
		with open(props['output'], 'ab') as res:
			res.write(json.dumps(self.RES).encode('utf-8'))
		res.close()
