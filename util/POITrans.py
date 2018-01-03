#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Output Format:
# [POI-Mongo-Import]
# JSON
# 原始 POI 处理成导入数据库的格式 [MongoDB/MySQL]

import json
import os


class POIExec(object):
	"""
	将原始 JSON 文件转化成预定格式、适合导入 mongoDB 的 GeoJSON 格式
		:param object: 
	"""
	def __init__(self, PROP):
		super(POIExec, self).__init__()
		self.POITypes = PROP['POITypes']
		self.basepath = PROP['basepath']
		self.type = PROP['type']
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

			if self.type == 'json':
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
			else:
				for each in geoCollection:
					pid = "%s%s" % (ptype, each['id'])
					name = each['name']
					business_area = each['business_area']
					address = each['address']
					cpstr = "%s,%s" % (str(each['cp'][0]), str(each['cp'][1]))

					singlerec = "%s,%s,%s,%s,%s,%s" % (pid, ptype, name, business_area, address, cpstr)
					self.RES.append(singlerec)

					count += 1	
			print "Total %d POIs" % count
		stream.close()

	def outputRes(self, props):
		with open(props['output'], 'ab') as res:
			if self.type == 'json':
				res.write(json.dumps(self.RES).encode('utf-8'))
			else:
				res.write('\n'.join(self.RES))
		res.close()
