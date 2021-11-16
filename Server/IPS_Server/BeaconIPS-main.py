#!/home/chris/anaconda3/bin/python

import logging,os
import sys
import numpy as np
import math
import time
import argparse
from scipy.spatial import distance

# plotting
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.tri as tri

from Beacon import Beacon
from APClass import AP
from TagClass import Tag
from Scene import Scene
from particle.ParticleFilter import ParticleFilter
from particle.Particle import Particle

from SysSolver import SysSolver

# coeffA = 0.00002803
# coeffB = -0.1409

PORT = 6000

WEIGHT_MAP_PATH = "data/weight_map3.csv"
# APCount = 4
AP_COUNT = 4
# TagCount = 1
TAG_COUNT = 1

PARTICLE_COUNT = 1000

RANDOM_WALK_CNT = 5

EFFPARATIO = 0.5

PAMEASNOISE = 1.2

# path=[
# [2,1],[2,1.1],[2,1.2],[2,1.3],[2,1.4],[2,1.5],[2,1.6],[2,1.7],[2,1.8],[2,1.9],
# [2,2],[2,2.1],[2,2.2],[2,2.3],[2,2.4],[2,2.5],[2,2.6],[2,2.7],[2,2.8],[2,2.9],
# [2,3],[2,3.1],[2,3.2],[2,3.3],[2,3.4],[2,3.5],[2,3.6],[2,3.7],[2,3.8],[2,3.9],
# [2,4],[2,4.1],[2,4.2],[2,4.3],[2,4.4],[2,4.5],[2,4.6],[2,4.7],[2,4.8],[2,4.9],
# [2,5],[2,5.1],[2,5.2],[2,5.3],[2,5.4],[2,5.5],[2,5.6],[2,5.7],[2,5.8],[2,5.9],
# [2,6], 
# [2,7], 
# [2,8]
# [3,8], [4,8], [5,8], [6,8], [7,8], [8,8], [9,8], [10,8],
# [10,7], [10,6], [10,5], [10,4], [10,3], [10,2], [11,2],
# [12,2], [13,2], [14,2], [15,2], [16,2], [17,2], [17,3],
# [17,4], [17,5], [17,6], [17,7], [17,8]
# ]
pathInd = 0
# plot 1: scene map
# pltmap, ax = plt.subplots()

def parseArgments():
	parser = argparse.ArgumentParser(description='Set up parameters for PF-based IPS.')
	parser.add_argument('--path', type=str, nargs=1, help='Log data path')
	parser.add_argument('-d', type=str, dest='dSwitch', nargs=1, default=['INFO'], help='Debug option: INFO; DEBUG')
	parser.add_argument('--show', dest='visu', action='store_true', help='Turn on visualization')
	parser.add_argument('--sigma', dest='sigma', type=int, default=[1], nargs=1, help='Sigma for RSSI noise')
	parser.add_argument('--KFoff', dest='KFoff', action='store_true', help='Turn off Kalman Filter')
	parser.add_argument('--APCount', dest='APCount', type=int, default=[4],nargs=1, help='Number of APs deployed, should be 2, 4, or 6')
	parser.add_argument('--tagCount', dest='TagCount', type=int, default=[1],nargs=1, help='Number of Tags to localize')
	parser.add_argument('--tagCoord', dest='TagCoord', type=float, default=[5.0,4.0], nargs=2, help='Coordinates of a Tag to localize')
	parser.add_argument('--pCount', dest='PCount', type=int, default=[1000],nargs=1, help='Number of Particles shall be generateds')
	parser.add_argument('--resample', type=str, dest='resamplingWay', nargs=1,default=['SUS'], help='Resampling approach option: MN (Multinomial); SUS (Systematic Univeral Sampling)')
	parser.add_argument('--scheme', type=str, dest='scheme', nargs=1, default=['IPS'], help='Resampling approach option: ips; sp; oips; tril')
	parser.add_argument('--effPaRatio', dest='effPaRatio', type=float, default=[0.5], nargs=1, help='effective sample size ratio')
	parser.add_argument('--paMeasNoise', dest='paMeasNoise', type=float, default=[1.2], nargs=1, help='particle measurement noise')
	parser.add_argument('--MovePathOn', dest='MovePathOn', action='store_true', help='Turn on move path of a tag')
	parser.add_argument('--seed', dest='seed', type=int, default=[0], nargs=1, help='seed for simulation')
	return parser
	# args = parser.parse_args()

def initAPs(scene, APDict, APcount):
	for i, j in zip(range(APcount), scene.genAPPos(APcount=APcount)):
		apId = "ap" + str(i)
		ap = AP(apId, j, PORT)	
		APDict[apId] = ap
		logging.info(f'AP INFO: {apId}, {j}')

def genPath(start, end):
	path=[]
	if start[0] == end[0]:
		n=np.abs(end[1]-start[1])/0.1
		path=[[start[0],y] for y in np.linspace(start[1], end[1], num=int(n))]
		return path
	elif start[1] == end[1]:
		n=np.abs(end[0]-start[0])/0.1
		path=[[x,start[1]] for x in np.linspace(start[0], end[0], num=int(n))]
		return path
	else:
		logging.error('start and end must have one same point, either x or y.')
		sys.exit()

def genPathRect(scene, start):
	path=[]
	path += genPath(start, [start[0], scene[1]-2])
	path += genPath([start[0], scene[1]-2], [scene[0]-2, scene[1]-2])
	path += genPath([scene[0]-2, scene[1]-2], [scene[0]-2, start[1]])
	path += genPath([scene[0]-2, start[1]], start)
	return path

def evaluate(t, p, world):
	"""evaluate performance. t: tag, p:particles, world_size"""
	sum = 0.0
	for i in range(len(p)):  # calculate mean error
		dx = (p[i].getX() - t.getX() + (world.getSceneX()/2.0)
		      ) % world.getSceneX() - (world.getSceneX()/2.0)
		dy = (p[i].getY() - t.getY() + (world.getSceneY()/2.0)
		      ) % world.getSceneY() - (world.getSceneY()/2.0)
		err = math.sqrt(dx * dx + dy * dy)
		sum += err
	return sum / float(len(p))

def evaluateAccu(t, p):
	"""evaluate performance. t: tag, p:estimate pos, world_size"""
	# print(t.mCoor, p.mCoor)
	errDist = distance.euclidean(t.mCoor, p.mCoor)
	# errDist = np.sqrt( np.power(t.mCoor[0] - p.mCoor[0], 2) + np.power(t.mCoor[1] - p.mCoor[1], 2) )
	return errDist

def projectXY(angle, mag):
	"""projecting mag to x and y axis by the angle

	Args:
		angle (float): angle of vector
		mag (float): magnitude of vector

	Returns:
		list: projected x and y
	"""
	x=np.cos(angle)*mag
	y=np.sin(angle)*mag
	return [x,y]

def combine2XYVec(vec1, vec2):
	"""combine two vectors having x and y coordinates into one vector

	Args:
		vec1 (list): vector with 2 elements
		vec2 (list): vector with 2 elements

	Returns:
		list: combined vector with 2 elements, i.e., x and y coordinates
	"""
	vn1=np.array(vec1)
	vn2=np.array(vec2)
	return vn1+vn2

def getCombAngleMag(combVec):
	"""get the angle of a given vector

	Args:
		combVec (list): a 2-dim vector with x and y

	Returns:
		list: [mag, angle], angle in radian
	"""
	ang=np.arctan2(combVec[1], combVec[0])
	mag=np.sqrt(combVec[0]**2+combVec[1]**2)
	return [mag, ang]

# this is the main entry point of this script
if __name__ == "__main__":
# def main():

	parser = parseArgments()
	para = parser.parse_args()
	# print(para.dSwitch)
	if para.dSwitch[0] == 'INFO':
		logging.basicConfig(level=logging.INFO)
		logging.info(f'Debug Level: {para.dSwitch[0]}')
	elif para.dSwitch[0] == 'DEBUG':
		logging.basicConfig(level=logging.DEBUG)
		logging.info(f'Debug Level: {para.dSwitch[0]}')
	else:
		pass
	
	visualize = False
	logging.info(f'Visualization: {para.visu}')
	if para.visu == True:
		visualize = True
	elif para.visu == False:
		visualize = False
	else:
		pass

	EFFPARATIO=para.effPaRatio[0]
	PAMEASNOISE=para.paMeasNoise[0]
	AP_COUNT=para.APCount[0]
	TAG_COUNT=para.TagCount[0]
	PARTICLE_COUNT=para.PCount[0]
	TAG_COORD=[float(para.TagCoord[0]), float(para.TagCoord[1])]
	logging.info(f'EffPaRatio:{EFFPARATIO}')
	logging.info(f'paMeasNoise:{PAMEASNOISE}')
	logging.info(f'AP number: {AP_COUNT}')
	logging.info(f'Tag number: {TAG_COUNT}')
	logging.info(f'Particle Number: {PARTICLE_COUNT}')
	logging.info(f'Tag coordinates: {TAG_COORD}')

	'''sigma for added normal noise'''
	logging.info(f'sigma: {para.sigma[0]}')
	logging.info(f'KF Off: {para.KFoff}')
	logging.info(f'Resampling approach: {para.resamplingWay[0]}')
	resamplingWay = para.resamplingWay[0]

	schemeName = para.scheme[0]
	if schemeName not in ['ips', 'sp', 'oips', 'tril']:
		logging.error(f'scheme name is not recognized, should be one of ips; oips; centroid; trai')
		sys.exit()

	pe=[]
	# 1 generate 20*10 room layout
	scene = Scene([20.00, 10.00])

	# pltmap = plt.figure(1)

	# fig1 = plt.figure(1)

	# plt.axis([-0.5, 20.5, -0.5, 10.5])
	# plt.grid(True)
	# ax1 = fig1.add_subplot(111, projection='3d')

	# initialize APs
	APDict = {}
	if AP_COUNT == 2:
		scene = Scene([20.00, 0.0])
	elif AP_COUNT > 2:
		scene = Scene([20.00, 10.00])
	
	initAPs(scene, APDict, AP_COUNT)
	# elif AP_COUNT == 6:
	# 	initAPs(scene, APDict, AP_COUNT)
	# print(APDict)
	logging.info(APDict)

	if para.MovePathOn:
		path=genPathRect(scene.getSceneXY(), [2,2])
		logging.info(f'generated path: {path}')

	# initialize tags
	TagDict = {}
	for i in range(TAG_COUNT):
		tagId = "tag" + str(i)
		# randCoor = [round(np.random.rand() * scene.getSceneX(), 2), 
					# round(np.random.rand() * scene.getSceneY(), 2)]

		randCoor = TAG_COORD
		tag = Tag(tagId, randCoor)
		TagDict[tagId] = tag
		logging.info(f'Tag INFO: {tagId}, {randCoor}')
		# ax1.scatter(randCoor[0], randCoor[1], [0], s=100, c='r',
		             # marker='^', label='True location')

	# 2 start simulation
	simulatedTimestamp = 0.0

	# initialize particle filter
	parFilter = ParticleFilter(scene, AP_COUNT, PAMEASNOISE)

	parFilter.readWeightMap(WEIGHT_MAP_PATH)

	parFilter.initializeParticles(PARTICLE_COUNT)

	parFilter.initialWeight()

	# debugParticles = []
	# for i in parFilter.particles:
	# 	debugParticles.append(i.mCoor)
	# 	print(i.mId, i.mCoor, parFilter.getWeightMap(i.mCoor))
	# 	x, y = zip(*debugParticles)

	randomWalkCnt = 0
	# initialize estimate
	# manPoint = parFilter.getAvgParticle()
	manPoint = Particle("pman", scene, AP_COUNT, PAMEASNOISE)
	
	while simulatedTimestamp <= 10.0:
		logging.info('\n')
		logging.info(f"#######  timestep: {simulatedTimestamp} #######")
		simulatedTimestamp += 0.1
		round(simulatedTimestamp, 2)
		
		randomWalkCnt += 1
		
		'''visulization'''
		# fig1= plt.figure(1)
		if AP_COUNT > 2:
			plt.axis([-0.5, scene.getSceneX()+0.5, -0.5, scene.getSceneY()+0.5])
		else:
			plt.axis([-0.5, scene.getSceneX()+0.5, -5, 5])
		plt.grid(True)
		fig1 = plt.figure(1, dpi=300, figsize=(10, 7))
		# ax1=fig.add_axes(projection='3d')
		ax1 = fig1.add_subplot(1, 1, 1, projection='3d')

		# fig, ax1 = plt.subplots(1,1, projection='3d')

		# ax1 = plt.axes(projection='3d')
		# ax1 = axes.Axes(fig1, projection='3d')

		for j in TagDict.values():
			if para.MovePathOn:
				j.mCoor=path[pathInd]
				pathInd+=1
			logging.info(f"{j.mId} True location: {j.getX()}, {j.getY()}")


		# trilateration
		sysMat=[]

		combVec = [0.0, 0.0]
		# 2.1 generate rssi data
		for i in APDict.values():
			ax1.scatter(i.getX(), i.getY(), [0], s=40, c='y', marker='s')
			ax1.text( i.getX(), i.getY(), 0, i.mId )
			apLoc = [i.getX(), i.getY()]

			for j in TagDict.values():
				# rssi = i.generateExactRSSI(j.getExactLocation())
				rssiNormal = i.generateErrorRSSI_Normal(j.getExactLocation(), sigma=para.sigma[0])
				rssiNormal = int(rssiNormal)
				# logging.info(f'rssiWNormal: {rssiNormal} for AP {i.mId}')
				# update
				if i.mRcvdBeacon != None:
					i.mRcvdBeacon.rssi = rssiNormal
					i.mRcvdBeacon.rssiHis.append(rssiNormal)
					i.mRcvdBeacon.lastTimeStamp = simulatedTimestamp
					if para.KFoff == True:
						i.mRcvdBeacon.applyAvgRssi()
						i.mRcvdBeacon.rssiHisFil.append(i.mRcvdBeacon.filteredRssi)
					else:
						#i.mRcvdBeacon.applyKF4Rssi()   
						#[j]
						i.mRcvdBeacon.applyMA()
						i.mRcvdBeacon.rssiHisFil.append(i.mRcvdBeacon.filteredRssi)
						# i.mRcvdBeacon.applyKFAvgRssi()
						
				else: # new
					beacon = Beacon(size=scene.getSceneXY(), _from = APDict[addr[0]].mIPAddr)
					beacon.rssi = rssiNormal
					beacon.rssiHis.append(rssiNormal)
					i.mRcvdBeacon = beacon
					i.mRcvdBeacon.lastTimeStamp = simulatedTimestamp
					if para.KFoff == True:
						i.mRcvdBeacon.applyAvgRssi()
						i.mRcvdBeacon.rssiHisFil.append(i.mRcvdBeacon.filteredRssi)
					else:
    					#i.mRcvdBeacon.applyMA()	
						#[j] 
						i.mRcvdBeacon.applyKF4Rssi()
						i.mRcvdBeacon.rssiHisFil.append(i.mRcvdBeacon.filteredRssi)
						# i.mRcvdBeacon.applyKFAvgRssi()
				
				# print(rssi, rssiNormal)
				# print(i.mRcvdBeacon.rssi, i.mRcvdBeacon.filteredRssi)
				
				# i.mRcvdBeacon.rssiHis
				# rssiH = i.mRcvdBeacon.rssiHis
				# rssiHF = i.mRcvdBeacon.rssiHisFil

				# res = [rssiH[a + 1] - rssiH[a]for a in range(len(rssiH)-1)]
				# res2 = [res[a + 1] - res[a] for a in range(len(res)-1)]

				# resf = [rssiHF[a + 1] - rssiHF[a]for a in range(len(rssiHF)-1)]
				# resf2 = [resf[a + 1] - resf[a] for a in range(len(resf)-1)]

				# resf=i.mRcvdBeacon.getGrad()
				# resf=i.mRcvdBeacon.gradButterFilter()

				# logging.info(f"rssiH: {rssiH}")
				# logging.info(f"diff: {res}")
				# logging.info(f"acc: {res2}")

				# logging.info(f"rssiHF: {rssiHF}")
				# logging.info(f"f-diff: {resf}")
				# logging.info(f"f-acc: {resf2}")

				# angle and magnitude calculation
				# instMag = i.mRcvdBeacon.getCurrMag()
				# angle = i.angle2Me(tCoor=manPoint.mCoor) # manPoint.mCoor

				# xyProj = projectXY(angle, instMag)
				# combVec = combine2XYVec(combVec, xyProj)

				# degee = math.degrees(angle)
				# logging.info(f"{i.mId}, magnitude: {instMag}, angle: {angle}, ({round(degee,2)})")
				# logging.info(" ")

				ax1.scatter(j.getX(), j.getY(), [0], s=100, c='r',
				            marker='^', label='True location')
				ax1.text( j.getX(), j.getY(), 0, f'{j.mId}: ({j.getX()}, {j.getY()})' )

			# i.mRcvdBeacon.setSize(scene.getSceneXY())
			apLoc.append(i.mRcvdBeacon.getRawDist())
			sysMat.append(apLoc)

		if schemeName == 'tril':
			# trilateration
			trilaterSolver = SysSolver()
			triEstPos = trilaterSolver.runSolver(sysMat=sysMat)
			
			if triEstPos[0] > scene.getSceneX():
				triEstPos[0] = scene.getSceneX()
			elif triEstPos[1] > scene.getSceneY():
				triEstPos[1] = scene.getSceneY()
			elif triEstPos[0] < 0.0:
				triEstPos[0] = 0.1
			elif triEstPos[1] < 0.0:
				triEstPos[1] = 0.1

			manPoint.setXY(round(float(triEstPos[0]),2), round(float(triEstPos[1]),2))
			# logging.info(f'tril: {schemeName}, {sysMat}, {triEstPos}, {manPoint.getX()}, {manPoint.getY()}')

		# 2.2 particle filter

		# combMagAng=getCombAngleMag(combVec)
		# logging.info(f"combined vector mag, {combMagAng[0]} angle: {combMagAng[1]}, (deg:{round(math.degrees(combMagAng[1]),1)}), combVec: {combVec}")

		# ax1.quiver(manPoint.getX(), manPoint.getY(), 0, manPoint.getX()+combVec[0], manPoint.getY()+combVec[1], 0)
		# ax1.quiver(10, 5, 10+combVec[0], 5+combVec[1], scale=1)

		# ax1.quiverkey(qu,)
		if para.MovePathOn:
			parFilter.updateMotion(np.multiply(combVec,4))

		if schemeName == 'oips':
			if randomWalkCnt == RANDOM_WALK_CNT:
				# manPoint = parFilter.getAvgParticle()
				parFilter.move( 1.0, 1.0)
				randomWalkCnt = 0

				# 2.3 particle filter resampling process
				parFilter.resample(list(APDict.values()), ax1)
				# parFilter.resampleSUS(list(APDict.values()), ax1)
			# estimated location
			manPoint = parFilter.getAvgParticle()

		elif schemeName == 'ips':

			'''update particles' weights'''
			parFilter.updateWeight(list(APDict.values()))

			# if randomWalkCnt == RANDOM_WALK_CNT:
			# 	# manPoint = parFilter.getAvgParticle()
			# 	parFilter.move( 0.5, 0.5)
			# 	randomWalkCnt = 0

			# 2.3 particle filter resampling process
			effeSZ = parFilter.effeSampleSize()
			logging.info(f"effecSampleSize: {effeSZ}")
			if effeSZ < PARTICLE_COUNT*EFFPARATIO:
				if resamplingWay == 'MN':
					parFilter.resampleMultinomial(list(APDict.values()), ax1)
				elif resamplingWay == 'SUS':
					parFilter.resampleSUS(list(APDict.values()), ax1)
				else:
					logging.error(f' unrecognized resampling approach: {resamplingWay}')
					sys.exit()

			# estimated location
			manPoint = parFilter.getAvgParticle()
		
		# plot estimated location
		ax1.scatter(manPoint.getX(), manPoint.getY(), s=100, c='g', marker='v', label='Estimated location')
		ax1.text( manPoint.getX(), manPoint.getY(), 0, f'Est.: ({manPoint.getX()}, {manPoint.getY()})' )
		
		if para.MovePathOn:
			ax1.quiver(manPoint.getX(), manPoint.getY(), 0, manPoint.getX()+combVec[0], manPoint.getY()+combVec[1], 0, length=0.5)

		logging.info(f"Tag Estimated Location: {manPoint.getX()}, {manPoint.getY()}" )

		'''for visualization'''
		pCoorX = [parFilter.particles[x].mCoor[0] for x in range(parFilter.numParticles)]
		pCoorY = [parFilter.particles[x].mCoor[1] for x in range(parFilter.numParticles)]
		pWeigh = [parFilter.particles[x].probability for x in range(parFilter.numParticles)]
		logging.debug( pWeigh )
		ax1.scatter(pCoorX, pCoorY, pWeigh)

		# to draw contour
		# ax1.plot_surface(pCoorX, pCoorY, pWeigh, rstride=4, cstride=4, alpha=0.25)



		# ax1.contour(pCoorX, pCoorY, pWeigh, zdir='z', levels=14, linewidths=1, cmap=plt.cm.hot)
		# cntr2 = ax1.tricontourf(pCoorX, pCoorY, pWeigh, levels=14, cmap="RdBu_r")
		# fig1.colorbar(cntr2, ax=ax1)

		ax1.set_xlabel('Room Length (m)')
		ax1.set_ylabel('Room Width (m)')
		ax1.set_zlabel('Weight')

		# evaluate average errors of particles
		tagList = list(TagDict.values())
		# error = round(evaluate(tagList[0], parFilter.particles, scene), 2)
		error = 0.0
		if manPoint:
			accur = round(evaluateAccu(tagList[0], manPoint), 2)
		logging.info(f'RMSE: {error}, Accur: {accur}')
		pe.append([error, accur, str(manPoint.getX())+' '+str(manPoint.getY())])

		# for showing 2d particles
		# debugParticles = []
		# for i in parFilter.particles:
		# 	debugParticles.append(i.mCoor)
		# 	# print(i.mId, i.mCoor, parFilter.getWeightMap(i.mCoor))
		# x, y = zip(*debugParticles)
		# ax1.scatter(x, y, [0]*len(x), c='b')

		# fig1.tight_layout()
		# plt.draw()
		# plt.pause(0.1)
		if visualize:
			fig1.tight_layout()
			# ax1.tricontour(pCoorX, pCoorY, pWeigh, zdir='z', levels=14, linewidths=1, cmap=plt.cm.hot)			
			plt.show()
		# plt.clf()

	if para.KFoff:
		schemeName = 'sp'

	fileName = f'pe/peData-{schemeName}-ap-{AP_COUNT}-sigma-{para.sigma[0]}-coor-{TAG_COORD[0]}-{TAG_COORD[1]}-s-{para.seed[0]}.csv'
	with open(fileName, 'w') as f:
		f.write(f'seed,{para.seed[0]}\n')
		f.write(f'effPaRatio,{EFFPARATIO}\n')
		f.write(f'paMeasNoise,{PAMEASNOISE}\n')
		f.write(f'ap,{AP_COUNT}\n')
		f.write(f'tag,{TAG_COUNT}\n')
		f.write(f'tag coord,{TAG_COORD[0]}-{TAG_COORD[1]}\n')
		f.write(f'sigma,{para.sigma[0]}\n')
		f.write(f'particle,{PARTICLE_COUNT}\n')
		f.write(f'kfoff,{para.KFoff}\n')
		f.write(f'rs,{resamplingWay}\n')
		f.write(f'simulation time,{simulatedTimestamp}\n')
		f.write(f'estimate loc,{manPoint.getX()} {manPoint.getY()}\n')
		for i in pe:
			f.write(f'rmse,{i[0]},error,{i[1]}, estimate loc,{i[2]}\n')

	# 3. particle filter
	# parFilter = ParticleFilter(scene)

	# parFilter.readWeightMap(WEIGHT_MAP_PATH)

	# parFilter.initializeParticles(PARTICLE_COUNT)

	# debugParticles = []
	# for i in parFilter.particles:
	# 	debugParticles.append(i.mCoor)
	# 	# print(i.mId, i.mCoor, parFilter.getWeightMap(i.mCoor))
	# x, y = zip(*debugParticles)
	# plt.scatter(x, y)

	# parFilter.particles.sort(key=lambda x: x.getX())
	# for i in parFilter.particles:
	# 	print(i.mId, i.mCoor, parFilter.getWeightMap(i.mCoor))
	
	# plt.show()

# def init():


# def animate(i):
