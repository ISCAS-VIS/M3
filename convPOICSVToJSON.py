#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# 将 POI 类/ Admin 类文件（例如 uniPOIDistribution.py）中生成的 CSV / [node 或者 edge] 结果转化成 JSON 格式并汇集到一个文件，准备存入 mongoDB

import sys
import time
from util.csvToMatrixJson import csvToMatrixJson

if __name__ == '__main__':
	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	# CSV -> Mongo.node.sample.js[matrix]
	# csvToMatrixJson({
	# 	'keys': [],
	# 	'DIRECTORY': '/enigma/tao.jiang/datasets/JingJinJi/records/bj-newvis-sg',
	# 	'FilePrefix': 'hares-j',
	# 	'INUM': 20,
	# 	'type': 'node'
	# }).run()

	# CSV -> Mongo.edge.sample.js[ppedge] 
	csvToMatrixJson({
		'keys': [],
		'DIRECTORY': '/enigma/tao.jiang/datasets/JingJinJi/records/bj-newvis-sg',
		'FilePrefix': 'ppedge-',
		'INUM': 20,
		'type': 'edge'
	}).run()

	# CSV -> [apoint]

	# CSV -> [aaedge]

	print "END TIME: %s" % time.time()
