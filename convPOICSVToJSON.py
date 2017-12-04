#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# 将 uniPOIDistribution.py 中生成的结果转化成 JSON 格式并汇集到一个文件，准备存入 mongoDB

import sys
import time
from util.csvToMatrixJson import csvToMatrixJson

if __name__ == '__main__':
	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	csvToMatrixJson({
		'keys': [],
		'DIRECTORY': '/enigma/tao.jiang/datasets/JingJinJi/records/bj-newvis-sg',
		'FilePrefix': 'hares-j',
		'INUM': 20
	}).run()

	print "END TIME: %s" % time.time()