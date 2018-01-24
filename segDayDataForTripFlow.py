#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# 将切分成天的数据按照小时进行切分存储，且只保留 travel 状态数据

import os

def main():
	INPUT_DIRECTORY = '/datahouse/tao.jiang/bj-byday-tf'
	OUTPUT_DIRECTORY = '/datahouse/tao.jiang/bj-byhour-onlytrip'

	for x in xrange(0, 87):
		print "Processing File-%d" % (x)
		res = [[] for i in xrange(0, 24)]  # 存储当天数据结果
		ifile = os.path.join(INPUT_DIRECTORY, 'rawdata-%d' % (x))
		with open(ifile, 'rb') as f:
			for line in f:
				line = line.strip('\n')
				linelist = line.split(',')
				hour = int(linelist[0])

				res[hour].append(line)
		f.close()

		# 存储结果
		for i in xrange(0, 24):
			seg = x * 24 + i
			ofile = os.path.join(OUTPUT_DIRECTORY, 'travelData-seg-%d' % (seg))
			with open(ofile, 'wb') as f:
				f.write('\n'.join(res[i]))
			f.close()


if __name__ == '__main__':
    main()