#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# 生成 POI Json 文件，适合存入 mongoDB

import sys
import time
import logging
import getopt
from util.POITrans import POIJson


def usage():
	pass


def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hd:", ["help", 'directory='])
	except getopt.GetoptError as err:
		print str(err)
		usage()
		sys.exit(2)

	city, directory = 'beijing', '/home/tao.jiang/datasets/JingJinJi/records'
	POITypes = ['120203', '120301', '120302']
	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
		elif opt in ("-d", "--directory"):
			directory = arg

	STARTTIME = time.time()
	print "Start approach at %s" % STARTTIME

	task = POIJson({
		'POITypes': POITypes,
		'basepath': directory
	})
	task.run()

	print "END TIME: %s" % time.time()


if __name__ == '__main__':
	logging.basicConfig(filename='logger-gennewpoijson.log', level=logging.DEBUG)
	main(sys.argv[1:])