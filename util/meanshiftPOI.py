#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 

import os
import numpy as np
from sklearn.cluster import MeanShift, estimate_bandwidth
from preprocess import getAdjacentMatrix


class MeanshiftPOI(object):
	def __init__(self, PROP):
		super(MeanshiftPOI, self).__init__()

		self.INPUT_PATH = os.path.join(PROP['IDIRECTORY'], 'clusterPOI')
		self.OUTPUT_PATH = os.path.join(PROP['ODIRECTORY'], 'clusterPOI')
		self.PIDList = []
		self.PFMatrix = []
		self.mstype = PROP['mstype']  # 记录 meanshift 聚类类别，用于构建不同的特征矩阵
		self.adjacentMatrix = getAdjacentMatrix()

	def run(self):
		if self.mstype == 'c12_t1':
			ifile = os.path.join(self.INPUT_PATH, 'paedge_%s.csv' % (self.mstype))
			self.constructPOIMatrix(ifile)
		self.meanShiftProcess()
		
	def constructPOIMatrix(self, file):
		with open(file, 'rb') as f:
			currentPID = ''
			currentPFVec = [0.0 for x in xrange(0, 16)]
			currentPFSum = 0
			for line in f:
				line = line.strip('\n')
				linelist = line.split(',')

				pid = linelist[0]
				aid = int(linelist[1])-1
				num = float(linelist[2])

				if currentPID != pid:
					self.PIDList.append(currentPID)
					singleVec = currentPFVec
					if currentPFSum != 0:
						singleVec = [each/currentPFSum for each in currentPFVec]
					
					self.PFMatrix.append(singleVec)
					currentPFVec = [0.0 for x in xrange(0, 16)]
					currentPFSum = 0
					currentPID = pid
				else:
					currentPFSum += num
					currentPFVec[aid] += num
			
			if self.PIDList[-1] != currentPID:
				self.PIDList.append(currentPID)
				singleVec = currentPFVec
				if currentPFSum != 0:
					singleVec = [each/currentPFSum for each in currentPFVec]
				self.PFMatrix.append(singleVec)
		f.close()

		self.PFMatrix = np.array(self.PFMatrix)

	def meanShiftProcess(self):
		# ###################################################
		# 通用 MeanShift 聚类函数

		# The following bandwidth can be automatically detected using
		bandwidth = estimate_bandwidth(self.PFMatrix, quantile=0.2, n_samples=500)

		ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
		ms.fit(self.PFMatrix)
		labels = ms.labels_
		# cluster_centers = ms.cluster_centers_

		labels_unique = np.unique(labels)
		n_clusters_ = len(labels_unique)

		print("number of estimated clusters : %d" % n_clusters_)

		A = np.array(self.PIDList)[:, np.newaxis]
		B = np.array(labels)[:, np.newaxis]
				
		res = np.hstack((A, B))
		self.OutputToFile(res)

	def OutputToFile(self, res):
		"""
		通用输出文件函数
			:param self: 
			:param res: 
		"""
		ostream = '\n'.join(["%s,%s" % (e[0], e[1]) for e in res])

		ofile = os.path.join(self.OUTPUT_PATH, 'meanshiftResult_%s' % (self.mstype))
		with open(ofile, 'ab') as f:
			f.write(ostream)
		f.close()