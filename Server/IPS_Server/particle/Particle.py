import logging,sys
from scipy.spatial import distance
import numpy as np
import math

from Beacon import Beacon
from Scene import Scene
from particle.Point import Point

# logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.INFO)
# logging.disable(level=logging.DEBUG)
# logging.disable(level=logging.INFO)

class Particle:
	"""docstring for Particle"""

	def __init__(	self, 
					name,
					scene,
					apcount,
					measNoise=1.2
					):
		super(Particle, self).__init__()
		# Scene info
		self.scene = scene
		self.apcount = apcount
		self.mId = name
		self.worldEndX = scene.getSceneX()
		self.worldEndY = scene.getSceneY()
		# Particle info
		if self.apcount > 2:
			self.mCoor = [round(np.random.rand() * (scene.getSceneX()-0.1), 3), 
						round(np.random.rand() * (scene.getSceneY()-0.1), 3)]
		else:
			self.mCoor = [round(np.random.rand() * (scene.getSceneX()-0.1), 3), 
						0.0]			
		self.orientation = 0.0
		if self.apcount > 2:
			self.maxDist = distance.euclidean(scene.getSceneOri(), scene.getSceneXY())
		else:
			self.maxDist = scene.getSceneX()

		self.probability = 0.0
		self.measNoise = measNoise
		# not used
		self.forwardNoise = 0.0
		self.turnNoise = 0.0
		self.senseNoise = 0.0

	def getX(self):
		return self.mCoor[0]
	
	def getY(self):
		return self.mCoor[1]

	def setX(self, xpos):
		self.mCoor[0] = xpos
	
	def setY(self, ypos):
		self.mCoor[1] = ypos

	def setXY(self, xpos, ypos):
		self.mCoor[0] = xpos
		self.mCoor[1] = ypos

	# def measurementProb(self, beacons):
	def measurementProb(self, aps):
		probSum = 0
		filteredAps = []

		if len(aps) > 0:
			for i in range(len(aps)):
				# print(aps[i].mIPAddr, aps[i].mRcvdBeacon.rssi, aps[i].mRcvdBeacon.lastSeq, aps[i].mRcvdBeacon.getDist())
				if aps[i].mRcvdBeacon.getDist() > 0.0001:
					filteredAps.append(aps[i])


		    # sort
			filteredAps.sort(key=lambda x: x.mRcvdBeacon.getDist())

			# print(filteredAps)
			distMax = filteredAps[len(filteredAps)-1].mRcvdBeacon.getDist()

			# print("distMax:", distMax)

			for i in range(len(filteredAps)):
				# the distance between this particle and an AP that received a beacon
				dist = distance.euclidean(self.mCoor, filteredAps[i].mCoor)

				# print("dist: ", self.mCoor, filteredAps[i].mCoor)
				# dist = MathX.distance(x, y, filteredBeacons.get(i).getPoint().x, filteredBeacons.get(i).getPoint().y)
				distFromBeacon = filteredAps[i].mRcvdBeacon.getDist()

				distWeight = dist / self.maxDist # normalize
				distFromBeaconWeight = distFromBeacon / distMax # normalize
				diff = np.abs(distWeight - distFromBeaconWeight)
				closeWeight = math.exp(-distFromBeacon/2)
				# closeWeight = 1 # = math.exp(-distFromBeacon/2)

				probSum += (1-diff) * closeWeight

				# print("FilteredAPs: ")
				# print("    distMax:", distMax, "self.maxDist:", self.maxDist)
				# print("    dist:", dist, "distFromBeacon:", distFromBeacon)
				# print("    coor:", self.mCoor, "apCoor:", filteredAps[i].mCoor)
				# print("    distWeight:", distWeight, "distFromBeaconWeight:", distFromBeaconWeight)
				# print("    diff:", diff, "closeWeight:", closeWeight)
				# print("    probSum:", probSum)
				
				logging.debug('FilteredAPs:')
				logging.debug("  filteredAP count: %d, len(ap): %d", len(filteredAps),len(aps))
				logging.debug("  distMax: %f, self.maxDist: %f", distMax, self.maxDist)
				logging.debug("  distFromBeacon: %f, dist: %f", distFromBeacon, dist)
				logging.debug("  particle coor: {0[0]} {0[1]}, apCoor: {1[0]} {1[1]}".format(self.mCoor, filteredAps[i].mCoor))
				logging.debug("  distFromBeaconWeight: %f, distWeight: %f", distFromBeaconWeight, distWeight)
				logging.debug("  diff: %f, closeWeight: %f", diff, closeWeight)
				logging.debug("  probSum: %f", probSum)

			self.probability = probSum / len(filteredAps)
			
			logging.debug("@@@ Final weight: %f", self.probability)
			logging.debug("  ###############################################")

		return self.probability

	def combinWeight(self, weight):
		if weight < 0.7:
			self.probability = 0.1

	def setInfo(self, coor, orientation, prob):
		if coor[0] < 0.0 or coor[0] >= self.worldEndX:
			print(coor)
			sys.exit("X coordinate out of bounds")

		if coor[1] < -0.0 or coor[1] >= self.worldEndY+0.000001:
			print(coor)
			sys.exit("Y coordinate out of bounds")

		if orientation < 0 or orientation >= 2*math.pi:
			print(orientation)
			sys.exit("oritentation out of bounds")

		self.mCoor = coor
		self.orientation = orientation
		self.probability = prob

	def setNoise(self, Fnoise, Tnoise, Snoise):
		self.forwardNoise = Fnoise
		self.turnNoise = Tnoise
		self.senseNoise = Snoise

	def move(self, moveX, moveY):
		logging.debug("before move(): X: %f, Y: %f", self.mCoor[0], self.mCoor[1])
		
		self.mCoor[0] = self.guideLine(self.mCoor[0], moveX, self.worldEndX)
		self.mCoor[1] = self.guideLine(self.mCoor[1], moveY, self.worldEndY)
		
		logging.debug("after move(): X: %f, Y: %f", self.mCoor[0], self.mCoor[1])
	
	def guideLine(self, curr, move, border):
		if curr + move <= 0.0 or \
			curr + move >= border:
			curr -=	move
		else:
			curr += move
		return curr

# Combined:
	def updateWeight(self, aps):

		probSum = 0.0
		filteredAps = []	

		if len(aps) > 0:
			for i in range(len(aps)):
				# print(aps[i].mIPAddr, aps[i].mRcvdBeacon.rssi, aps[i].mRcvdBeacon.lastSeq, aps[i].mRcvdBeacon.getDist())
				if aps[i].mRcvdBeacon.getDist() > 0.0001:
					filteredAps.append(aps[i])

			# sort
			filteredAps.sort(key=lambda x: x.mRcvdBeacon.getDist())

			# print(filteredAps)
			distBeaconMax = filteredAps[len(filteredAps)-1].mRcvdBeacon.getDist()

			# print("distMax:", distMax)

			for i in range(len(filteredAps)):
				# the distance between this particle and an AP that received a beacon
				distParticle = distance.euclidean(self.mCoor, filteredAps[i].mCoor) # particle
				distBeacon = filteredAps[i].mRcvdBeacon.getDist() # beacon

				# normalize
				distParticleWeightNormal = distParticle / self.maxDist # normalize particle
				distBeaconWeightNormal = distBeacon / distBeaconMax # normalize beacon
				
				# square absolute difference
				diff = np.abs(distParticleWeightNormal - distBeaconWeightNormal)
				
				# closeWeight = math.exp( (-0.5*diff) / ((self.measNoise)**2) )
				closeWeight = math.exp(-distBeacon/2)

				probSum += (1-diff) * closeWeight

				logging.debug('FilteredAPs:')
				logging.debug("  filteredAP count: %d, len(ap): %d", len(filteredAps),len(aps))
				logging.debug("  particle coor: {0[0]} {0[1]}, apCoor: {1[0]} {1[1]}".format(self.mCoor, filteredAps[i].mCoor))
				logging.debug("  distBeaconMax: %f, self.maxDist: %f", distBeaconMax, self.maxDist)
				logging.debug("  distParticle: %f, distBeacon: %f", distParticle, distBeacon)
				logging.debug("  distParticleWeightNormal: %f,distBeaconWeightNormal: %f", distParticleWeightNormal, distBeaconWeightNormal)
				logging.debug("  diff: %f, closeWeight: %f", diff, closeWeight)
				logging.debug("  probSum: %f", probSum)
			
			self.probability = probSum / len(filteredAps)
			logging.debug("@@@ Final weight: %f", self.probability)
			logging.debug("###############################################")

		return self.probability

# Baseline:
	def updateWeightSP(self, aps):
		"""Baseline: smart parking paper, update weight

		Arguments:
			aps {dict} -- AP dict to store APs information

		Returns:
			float -- my probability
		"""

		# probSum = 0.0
		filteredAps = []	

		if len(aps) > 0:
			for i in range(len(aps)):
				# print(aps[i].mIPAddr, aps[i].mRcvdBeacon.rssi, aps[i].mRcvdBeacon.lastSeq, aps[i].mRcvdBeacon.getDist())
				if aps[i].mRcvdBeacon.getDist() > 0.000001:
					filteredAps.append(aps[i])

			# sort
			# filteredAps.sort(key=lambda x: x.mRcvdBeacon.getDist())

			# print(filteredAps)
			# distBeaconMax = filteredAps[len(filteredAps)-1].mRcvdBeacon.getDist()

			# print("distMax:", distMax)

			gainFactorSum = 0.0
			for i in range(len(filteredAps)):
				# the distance between this particle and an AP that received a beacon
				distParticle = distance.euclidean(self.mCoor, filteredAps[i].mCoor) # particle
				distBeacon = filteredAps[i].mRcvdBeacon.getDist() # beacon

				# normalize
				# distParticleWeightNormal = distParticle / self.maxDist # normalize particle
				# distBeaconWeightNormal = distBeacon / distBeaconMax # normalize beacon
				
				# square absolute difference
				# diff = (math.fabs(distParticleWeightNormal - distBeaconWeightNormal))**2.0
				
				diff = (math.fabs(distParticle-distBeacon)**2.0)

				# logging.debug( '~~~~ Parameter: %f', (-0.5*diff) / math.pow(self.measNoise,2) )

				gainFactor = math.exp((-0.5*diff) / ( self.measNoise ** 2))
				# gainFactor = math.exp((-0.5*diff) / ( 1.2 ** 2))

				gainFactorSum += gainFactor

				logging.debug('FilteredAPs:')
				logging.debug("  filteredAP count: %d, len(ap): %d", len(filteredAps),len(aps))
				logging.debug("  particle coor: {0[0]} {0[1]}, apCoor: {1[0]} {1[1]}".format(self.mCoor, filteredAps[i].mCoor))
				# logging.debug("  distBeaconMax: %f, self.maxDist: %f", distBeaconMax, self.maxDist)
				logging.debug("  distParticle: %f, distBeacon: %f", distParticle, distBeacon)
				# logging.debug("  distParticleWeightNormal: %f,distBeaconWeightNormal: %f", distParticleWeightNormal, distBeaconWeightNormal)
				logging.debug("  diff: %f, gainFactor: %f", diff, gainFactor)
				logging.debug("  gainFactorSum: %f", gainFactorSum)
			
			avgGainFactor = gainFactorSum / len(filteredAps)
			self.probability = self.probability * avgGainFactor

			logging.debug("@@@ Final weight: %f, avgGainFactor: %f", self.probability, avgGainFactor)
			logging.debug("###############################################")

		return self.probability


	def updateWeightMG(self, aps):
		"""Baseline: update weight

		Arguments:
			aps {dict} -- AP dict to store APs information

		Returns:
			float -- my probability
		"""

		# probSum = 0.0
		filteredAps = []	

		if len(aps) > 0:
			for i in range(len(aps)):
				# print(aps[i].mIPAddr, aps[i].mRcvdBeacon.rssi, aps[i].mRcvdBeacon.lastSeq, aps[i].mRcvdBeacon.getDist())
				if aps[i].mRcvdBeacon.getDist() > 0.000001:
					filteredAps.append(aps[i])

			# sort
			filteredAps.sort(key=lambda x: x.mRcvdBeacon.getDist())

			# print(filteredAps)
			distBeaconMax = filteredAps[len(filteredAps)-1].mRcvdBeacon.getDist()

			# print("distMax:", distMax)

			diffSum = 0.0
			for i in range(len(filteredAps)):
				# the distance between this particle and an AP that received a beacon
				distParticle = distance.euclidean(self.mCoor, filteredAps[i].mCoor) # particle
				distBeacon = filteredAps[i].mRcvdBeacon.getDist() # beacon

				# normalize
				distParticleWeightNormal = distParticle / self.maxDist # normalize particle
				distBeaconWeightNormal = distBeacon / distBeaconMax # normalize beacon
				
				# square absolute difference
				# diff = (math.fabs(distParticleWeightNormal - distBeaconWeightNormal))**2.0
				# diff = math.fabs(distParticle-distBeacon)**2.0

				# diff = math.fabs(distParticle-distBeacon)
				diff = math.fabs(distParticleWeightNormal - distBeaconWeightNormal)

				diffSum += diff
				
				# logging.debug( '~~~~ Parameter: %f', (-0.5*diff) / math.pow(self.measNoise,2) )

				logging.debug('FilteredAPs:')
				logging.debug("  filteredAP count: %d, len(ap): %d", len(filteredAps),len(aps))
				logging.debug("  particle coor: {0[0]} {0[1]}, apCoor: {1[0]} {1[1]}".format(self.mCoor, filteredAps[i].mCoor))
				logging.debug("  distBeaconMax: %f, self.maxDist: %f", distBeaconMax, self.maxDist)
				logging.debug("  distParticle: %f, distBeacon: %f", distParticle, distBeacon)
				logging.debug("  distParticleWeightNormal: %f,distBeaconWeightNormal: %f", distParticleWeightNormal, distBeaconWeightNormal)

			# avgDiffSum = ((1-diffSum) / len(filteredAps))**2
			avgDiffSum2 = ( diffSum / len(filteredAps) )**2
			gainFactor = math.exp((-0.5*avgDiffSum2) / ( self.measNoise ** 2))
			
			self.probability = self.probability * gainFactor
			
			logging.debug("  diffSum: %f", diffSum)
			logging.debug("  gainFactor: %f", gainFactor)
			logging.debug("@@@ Final weight: %f, avgDiffSum2: %f", self.probability, avgDiffSum2)
			logging.debug("###############################################")

		return self.probability

	def updateWeightExp(self, aps):
		"""Baseline: update weight

		Arguments:
			aps {dict} -- AP dict to store APs information

		Returns:
			float -- my probability
		"""

		# probSum = 0.0
		filteredAps = []	

		if len(aps) > 0:
			for i in range(len(aps)):
				# print(aps[i].mIPAddr, aps[i].mRcvdBeacon.rssi, aps[i].mRcvdBeacon.lastSeq, aps[i].mRcvdBeacon.getDist())
				if aps[i].mRcvdBeacon.getDist() > 0.000001:
					filteredAps.append(aps[i])

			# sort
			filteredAps.sort(key=lambda x: x.mRcvdBeacon.getDist())

			# print(filteredAps)
			distBeaconMax = filteredAps[len(filteredAps)-1].mRcvdBeacon.getDist()

			# print("distMax:", distMax)

			diffSum = 0.0
			for i in range(len(filteredAps)):
				# the distance between this particle and an AP that received a beacon
				distParticle = distance.euclidean(self.mCoor, filteredAps[i].mCoor) # particle
				distBeacon = filteredAps[i].mRcvdBeacon.getDist() # beacon

				# normalize
				distParticleWeightNormal = distParticle / self.maxDist # normalize particle
				distBeaconWeightNormal = distBeacon / distBeaconMax # normalize beacon
				
				# square absolute difference
				# diff = (math.fabs(distParticleWeightNormal - distBeaconWeightNormal))**2.0
				# diff = math.fabs(distParticle-distBeacon)**2.0

				# diff = math.fabs(distParticle-distBeacon)
				diff = math.fabs(distParticleWeightNormal - distBeaconWeightNormal)

				diffSum += diff
				
				# logging.debug( '~~~~ Parameter: %f', (-0.5*diff) / math.pow(self.measNoise,2) )

				logging.debug('FilteredAPs:')
				logging.debug("  filteredAP count: %d, len(ap): %d", len(filteredAps),len(aps))
				logging.debug("  particle coor: {0[0]} {0[1]}, apCoor: {1[0]} {1[1]}".format(self.mCoor, filteredAps[i].mCoor))
				# logging.debug("  distBeaconMax: %f, self.maxDist: %f", distBeaconMax, self.maxDist)
				logging.debug("  distParticle: %f, distBeacon: %f", distParticle, distBeacon)
				# logging.debug("  distParticleWeightNormal: %f,distBeaconWeightNormal: %f", distParticleWeightNormal, distBeaconWeightNormal)

			# avgDiffSum = ((1-diffSum) / len(filteredAps))**2
			avgDiffSum2 = math.fabs(diffSum / len(filteredAps))
			# gainFactor = math.exp((-0.5*avgDiffSum2) / ( self.measNoise ** 2))

			gainFactor = math.exp(-avgDiffSum2 / self.measNoise)

			self.probability = self.probability * gainFactor

			logging.debug("  diffSum: %f", diffSum)
			logging.debug("  gainFactor: %f", gainFactor)
			logging.debug("@@@ Final weight: %f, avgDiffSum2: %f", self.probability, avgDiffSum2)
			logging.debug("###############################################")

		return self.probability