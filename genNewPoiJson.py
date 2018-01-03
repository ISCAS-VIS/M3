#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# 生成 POI Json 文件，适合存入 mongoDB 或者 MySQL

import sys
import time
import logging
import getopt
from util.POITrans import POIExec


def usage():
	print "python a.py -d /data -t json"


def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hd:t:", ["help", 'directory=', 'type='])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records'
	exectype = "json"
	POITypes = ['120203', '120301', '120302']
	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-d", "--directory"):
			directory = arg
		elif opt in ("-t", "--type"):
			exectype = opt

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	rawdata = {
		'POITypes': POITypes,
		'basepath': directory,
		'type': exectype
	}
	task = POIExec(rawdata)
	task.run()

	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-gennewpoi.log', level=logging.DEBUG)
	main(sys.argv[1:])