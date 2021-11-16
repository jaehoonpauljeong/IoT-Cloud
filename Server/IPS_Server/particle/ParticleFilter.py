import logging, sys, os
import csv
import numpy as np
import math
import pprint
import random as rand
from numpy.random import random

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# currentdir = os.path.dirname(os.path.realpath(__file__))
# print(currentdir)
# parentdir = os.path.dirname(currentdir)
# sys.path.append(parentdir)

from particle.Particle import Particle
from Scene import Scene
# from Beacon import Beacon


DOWN_COEFFEC = 0.3
# logging.basicConfig(level=logging.DEBUG)
# logging.disable(level=logging.DEBUG)

class ParticleFilter:
	"""docstring for ParticleFilter"""

	def __init__(	self, 
					scene,
					apcount,
					parNoise
					):
		super(ParticleFilter, self).__init__()
		self.scene = scene
		self.apcount = apcount
		self.numParticles = 0
		self.particles = []
		self.weightMap = []
		self.parNoise = parNoise

	def readWeightMap(self, weighMapFilePath):
		# read weight_map.csv file to initialize weightMap, 30*55
		with open(str(weighMapFilePath)) as csvfile:
			weightMapReader = csv.reader(csvfile)		
			for row in weightMapReader:
				self.weightMap.append([float(i) for i in row])
		
		# pprint.pprint(self.weightMap, indent=1, width=80, compact=True)

	def initializeParticles(self, num):
		self.numParticles = num
		self.particles = [Particle("p"+str(i), self.scene, self.apcount, self.parNoise) for i in range(num)]

	def resample(self, aps, ax):

		# new_particles = Particle[numParticles]
		new_particles = [Particle("pn"+str(i), self.scene, self.apcount, self.parNoise) for i in range(self.numParticles)]

		# weightSum = 0
		
		for i in range(self.numParticles):
			self.particles[i].measurementProb(aps)
			# self.particles[i].updateWeight(aps)
			# self.particles[i].updateWeightSP(aps)

			logging.debug("  before combined: i: %d, %s, w: %f, coor: %f, %f", i,self.particles[i].mId, self.particles[i].probability, self.particles[i].mCoor[0], self.particles[i].mCoor[1])
			
			# check the weight of a location where a particle resides in the weighMap of a room
			# TODO: particle coordinates mapping to weight map
			# print(self.particles[i].mCoor)
			self.particles[i].combinWeight(self.getWeightMap(self.particles[i].mCoor))
			# logging.debug("  after combined: %s, w: %f", self.particles[i].mId, self.particles[i].probability)
		
		# for showing 3d particles
		# plt.cla()
		# plt.grid(True)
		# fig2 = plt.figure(2)
		# ax = fig2.add_subplot(111, projection='3d')
		# pCoorX = [self.particles[x].mCoor[0] for x in range(self.numParticles)]
		# pCoorY = [self.particles[x].mCoor[1] for x in range(self.numParticles)]
		# pWeigh = [self.particles[x].probability for x in range(self.numParticles)]
		# ax.scatter(pCoorX, pCoorY, pWeigh)
		# # plot true location
		# # ax.scatter([4], [3], [0], 'r^')
		# ax.set_xlabel('Room Length (m)')
		# ax.set_ylabel('Room Width (m)')
		# ax.set_zlabel('Weight')
		# plt.show()

		best = self.getBestParticle()

		B = 0.0
		# generate random index for particles
		# index = (int) gen.nextFloat() * numParticles
		index = int(random() * self.numParticles)
		for i in range(self.numParticles):
			# resampling wheel
			# B += np.random.rand() * (self.numParticles*2.0) * best.probability
			B += random() * best.probability * 2.0

			# print(self.particles[index].probability)
			while B > self.particles[index].probability:
				B -= self.particles[index].probability
				index = self.circle(index + 1, self.numParticles)
				# index = (index+1) % N

			# print(index)
			# new_particles[i] = Particle(self.particles[index].mId, self.scene)
			new_particles[i].mId = self.particles[index].mId
			
			new_particles[i].setInfo(	self.particles[index].mCoor, 
										self.particles[index].orientation, 
										self.particles[index].probability)

			# print(new_particles[i].mCoor)

		self.particles = new_particles

		return self.particles

	def resampleSUS(self, aps, ax):
		# new_particles = Particle[numParticles]
		new_particles = [Particle("pn"+str(i), self.scene, self.apcount, self.parNoise) for i in range(self.numParticles) ]

		pWeight=[]
		for i in range(self.numParticles):
			pWeight.append(self.particles[i].probability)

		pIndex=[]
		'''resampling algorithm'''
		pIndex = self.systematic_resample(pWeight) 
		# print(f'pIndex: {len(pIndex)}')
		# print(f'pIndex: {pIndex}')
		
		i = 0
		for index in pIndex:
			new_particles[i].setInfo(	self.particles[index].mCoor, 
										self.particles[index].orientation, 
										1/self.numParticles)
			i += 1

		self.particles = new_particles

		return self.particles

	def resampleMultinomial(self, aps, ax):

		# new_particles = Particle[numParticles]
		new_particles = [Particle("pn"+str(i), self.scene, self.apcount, self.parNoise) for i in range(self.numParticles)]

		pWeight=[]
		for i in range(self.numParticles):
			pWeight.append(self.particles[i].probability)

		pIndex=[]
		'''resampling algorithm'''
		pIndex = self.multinomial_resample(pWeight) 

		i = 0
		for index in pIndex:
			new_particles[i].setInfo(	self.particles[index].mCoor, 
										self.particles[index].orientation, 
										self.particles[index].probability)
			i += 1

		self.particles = new_particles

		return self.particles

	def downgradeWeight(self):
		for i in range(self.numParticles):
			x = self.particles[i].probability
			self.particles[i].probability += -1 * (x - 1/self.numParticles) * DOWN_COEFFEC


		pWeight = []
		for i in range(self.numParticles):
			pWeight.append(self.particles[i].probability)

		pSumWeigh = sum(pWeight)
		logging.debug('pSumWeigh: %f', pSumWeigh)

		for i in range(self.numParticles):
			self.particles[i].probability = self.particles[i].probability/pSumWeigh
		

	def getBestParticle(self):
		particle = self.particles[0]
		for i in range(self.numParticles):
			if self.particles[i].probability > particle.probability:
				particle = self.particles[i]

		return particle

	def getAvgParticle(self):
		p = Particle("pAvg", self.scene, self.apcount, self.parNoise)
		x = 0
		y = 0
		orient = 0
		prob = 0

		for i in range(self.numParticles):
			x += self.particles[i].getX() * self.particles[i].probability
			#x += self.particles[i].getX()
			y += self.particles[i].getY() * self.particles[i].probability
			#y += self.particles[i].getY()
			orient += self.particles[i].orientation
			prob += self.particles[i].probability

		#x /= self.numParticles
		#y /= self.numParticles
		orient /= self.numParticles
		prob /= self.numParticles
		
		p.setInfo([round(x,2), round(y,2)], orient, prob)

		# p.setNoise(	self.particles[0].forwardNoise, 
		# 			self.particles[0].turnNoise, 
		# 			self.particles[0].senseNoise)

		return p

	def move(self, moveX, moveY):
		for i in range(self.numParticles):
			# dX = math.floor(np.random.rand()*moveX) - moveX/2
			# dY = math.floor(np.random.rand()*moveY) - moveY/2
			
			dX = np.random.uniform(-1, 1)*moveX
			dY = np.random.uniform(-1, 1)*moveY
			
			logging.debug("move(): dX: %f, dY: %f", dX, dY)

			self.particles[i].move(dX, dY)

	def getWeightMap(self, coor):

		# x = round(coor[0], 1) * 10
		# y = round(coor[1], 1) * 10

		x = math.floor(round(coor[0],1) * 10)
		y = math.floor(round(coor[1],1) * 10)

		# print([x, y])
		# print(len(self.weightMap))
		# print(len(self.weightMap[y]))
		if y < len(self.weightMap) and x < len(self.weightMap[y]):
			return self.weightMap[y][x]
		else:
			print([x, y])
			sys.exit("Error in ParticleFilter.py: can't find weight in the " \
				"weightMap, exceeding bounds.")
			return False

	def circle(self, num, length):
		while num > length-1:
			num -= length

		while num < 0:
			num += length
		return num

# new functions
	def effeSampleSize(self):
		"""Compute effective sample size for determining resampling or not, it should be used with a threshold.

		Returns:
			float -- [description]
		"""
		total = 0.0
		for ele in self.particles:
			total += ele.probability**2

		return 1.0/total


# Baseline, SP

	def initialWeight(self):
		"""Initialize all particles' weight with 1/N
		"""
		for ele in self.particles:
			ele.probability = 1.0/self.numParticles

	# def initialWeightBoost(self):
	# 	"""Initialize all particles' weight with 1/N
	# 	"""
	# 	for i in range(self.numParticles):
	# 		# self.particles[i].updateWeightSP(aps)
	# 		self.particles[i].updateWeight(aps)

	# 	'''normalize weights for particles'''
	# 	pWeight = []
	# 	for i in range(self.numParticles):
	# 		pWeight.append(self.particles[i].probability)

	# 	pSumWeigh = sum(pWeight)
	# 	logging.debug('pSumWeigh: %f', pSumWeigh)

	# 	for i in range(self.numParticles):
	# 		self.particles[i].probability = self.particles[i].probability/pSumWeigh
	# 		logging.debug(" Normalized weight: %f", self.particles[i].probability)

	# 	return self.particles

	def updateWeight(self, aps):
		"""Update weight of each particle at each step.
		"""
		for i in range(self.numParticles):
			#self.particles[i].updateWeightSP(aps)
			self.particles[i].updateWeightMG(aps)
			#self.particles[i].updateWeightExp(aps)
			# self.particles[i].updateWeight(aps)

		'''normalize weights for particles'''
		pWeight = []
		for i in range(self.numParticles):
			pWeight.append(self.particles[i].probability)

		pSumWeigh = sum(pWeight)
		logging.debug('pSumWeigh: %f', pSumWeigh)

		for i in range(self.numParticles):
			try:
				self.particles[i].probability = self.particles[i].probability/pSumWeigh
			except ZeroDivisionError:
				self.particles[i].probablilty = 1
			logging.debug(" Normalized weight: %f", self.particles[i].probability)

		return self.particles

	def updateMotion(self, d_angle, d_acc):
		# calibarating acc 
		d_acc *= 0.7

		print("Heading Direction {}".format(d_angle))
		print("Acceralation: {}".format(d_acc))

		spreadRange = 180 if d_acc == 0 else 30
		
		if d_acc == 0: d_acc = 0.005

		for i in range(self.numParticles):
			theta = d_angle + rand.randrange(-spreadRange,spreadRange)
			move_X = math.sin(math.pi * (theta / 180)) * abs(d_acc) 	
			move_Y = math.cos(math.pi * (theta / 180)) * abs(d_acc)
			dX= self.particles[i].getX() + move_X
			dY= self.particles[i].getY() + move_Y
			if dX > 0 and dX < self.scene.getSceneX() and dY > 0 and dY < self.scene.getSceneY():
				self.particles[i].mCoor=[dX,dY]
			else:
    			#dX
				if dX < 0:  dX = 0
				elif dX > self.scene.getSceneX(): dX = self.scene.getSceneX()

				#dY
				if dY < 0:  dY = 0
				elif dY > self.scene.getSceneX(): dY = self.scene.getSceneY()
				self.particles[i].mCCoor=[dX, dY]
			
	

	def multinomial_resample(self, weights):
		""" This is the naive form of roulette sampling where we compute the cumulative sum of the weights and then use binary search to select the resampled point based on a uniformly distributed random number. Run time is O(n log n). You do not want to use this algorithm in practice; for some reason it is popular in blogs and online courses so I included it for reference.

		Parameters
		----------

		weights : list-like of float list of weights as floats

		Returns
		-------

		indexes : ndarray of ints array of indexes into the weights defining the resample. i.e. the index of the zeroth resample is indexes[0], etc.
		"""
		cumulative_sum = np.cumsum(weights)
		# cumulative_sum[-1] = 1.  # avoid round-off errors: ensures sum is exactly one
		# return np.searchsorted(cumulative_sum, random(len(weights)))
		return np.searchsorted(cumulative_sum, random(len(weights)))

	def systematic_resample(self, weights):
		""" Performs the systemic resampling algorithm used by particle filters. This algorithm separates the sample space into N divisions. A single random offset is used to to choose where to sample from for all divisions. This guarantees that every sample is exactly 1/N apart.

		Parameters
		----------
		weights : list-like of float list of weights as floats

		Returns
		-------

		indexes : ndarray of ints
			array of indexes into the weights defining the resample. i.e. the
			index of the zeroth resample is indexes[0], etc.
		"""
		N = len(weights)

		# make N subdivisions, and choose positions with a consistent random offset
		positions = (random() + np.arange(N)) / N

		indexes = np.zeros(N, 'i')
		cumulative_sum = np.cumsum(weights)
		i, j = 0, 0
		while i < N:
			if positions[i] < cumulative_sum[j]:
				indexes[i] = j
				i += 1
			else:
				j += 1
		return indexes
