#!/usr/bin/env python3

import logging, os
import sys
import numpy as np
import math
import time
import threading
import socket
import argparse
from scipy.spatial import distance

# plotting
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d.proj3d import proj_transform
from mpl_toolkits.mplot3d.axes3d import Axes3D

from Beacon import Beacon
from APClass import AP
from TagClass import Tag
from Scene import Scene
from particle.ParticleFilter import ParticleFilter
from particle.Particle import Particle

from SysSolver import SysSolver

class Arrow3D(FancyArrowPatch):
    
    def __init__(self, x, y, z, dx, dy, dz, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._xyz = (x, y, z)
        self._dxdydz = (dx, dy, dz)

    def draw(self, renderer):
        x1, y1, z1 = self._xyz
        dx, dy, dz = self._dxdydz
        x2, y2, z2 = (x1 + dx, y1 + dy, z1 + dz)

        xs, ys, zs = proj_transform((x1, x2), (y1, y2), (z1, z2), self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        super().draw(renderer)

def _arrow3D(ax, x, y, z, dx, dy, dz, *args, **kwargs):
    '''Add an 3d arrow to an `Axes3D` instance.'''

    arrow = Arrow3D(x, y, z, dx, dy, dz, *args, **kwargs)
    ax.add_artist(arrow)




# coeffA = 0.00002803
# coeffB = -0.1409

WEIGHT_MAP_PATH = "data/weight_map3.csv"
TOTAL_AP = 5
AP_COUNT = 0

APDict = {}

PORT = 6000

# TagCount = 1
TAG_COUNT = 1

PARTICLE_COUNT = 10

RANDOM_WALK_CNT = 5

SCENE_SIZE = None
SCENE_X = 8.5
SCENE_Y = 5.6
EFFPARATIO = 0.3

DEVICE_IP = ""
DEVICE_ANGLE =0
DEVICE_ACC = 0
PAMEASNOISE = 1.2

# plot 1: scene map
# pltmap, ax = plt.subplots()
# pltmap = plt.figure(1)

def parseArgments():
	parser = argparse.ArgumentParser(description='Specify log data path.')
	parser.add_argument('--path', type=str, nargs=1, help='Log data path')
	parser.add_argument('-d', type=str, dest='dSwitch', nargs=1, default=['INFO'], help='Debug option: INFO; DEBUG')
	parser.add_argument('--show', dest='visu', action='store_true', help='Turn on visualization')
	parser.add_argument('--sigma', dest='sigma', type=int, default=[2], nargs=1, help='Sigma for RSSI noise')
	parser.add_argument('--KFoff', dest='KFoff', action='store_true', help='Turn off Kalman Filter')
	parser.add_argument('--APCount', dest='APCount', type=int, default=[4],nargs=1, help='Number of APs deployed, should be 2, 4, or 6')
	parser.add_argument('--tagCount', dest='TagCount', type=int, default=[1],nargs=1, help='Number of Tags to localize')
	parser.add_argument('--tagCoord', dest='TagCoord', type=float, default=[3.0,4.0], nargs=2, help='Coordinates of a Tag to localize')
	parser.add_argument('--pCount', dest='PCount', type=int, default=[500],nargs=1, help='Number of Particles shall be generateds')
	parser.add_argument('--resample', type=str, dest='resamplingWay', nargs=1,default=['SUS'], help='Resampling approach option: MN (Multinomial); SUS (Systematic Univeral Sampling)')
	parser.add_argument('--scheme', type=str, dest='scheme', nargs=1, default=['IPS'], help='Resampling approach option: ips; sp; oips; centroid; tril')
	parser.add_argument('--effPaRatio', dest='effPaRatio', type=float, default=[0.5], nargs=1, help='effective sample size ratio')
	parser.add_argument('--paMeasNoise', dest='paMeasNoise', type=float, default=[0.2], nargs=1, help='particle measurement noise')
	parser.add_argument('--MovePathOn', dest='MovePathOn', action='store_true', default=True, help='Turn on move path of a tag')
	parser.add_argument('--seed', dest='seed', type=int, default=[0], nargs=1, help='seed for simulation')
	return parser
	# args = parser.parse_args()

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
	errDist = distance.euclidean(t.mCoor, p.mCoor)
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

def ip2Coor(ipAddr):
	splIPAddr = ipAddr.split('.')
	# print("The last digit of ipAddr:", splIPAddr[len(splIPAddr)-1])
	if str(splIPAddr[len(splIPAddr)-1]) == '44':
		return [0.00, SCENE_Y]
	elif str(splIPAddr[len(splIPAddr)-1]) == '74':
		return [SCENE_X, SCENE_Y]
	elif str(splIPAddr[len(splIPAddr)-1]) == '103':
		return [0.0, 0.00]
	elif str(splIPAddr[len(splIPAddr)-1]) == '38':
		return [SCENE_X, 0.00]
	elif str(splIPAddr[len(splIPAddr)-1]) == '79':
		return [3.6, 3.0]
	else:
		logging.error(f'cannot find a coord for AP: {ipAddr}')
		# thrObject.join()
		stop_threads = True
		sys.exit()

def ip2Coor1D(ipAddr):
	splIPAddr = ipAddr.split('.')
	# print("The last digit of ipAddr:", splIPAddr[len(splIPAddr)-1])
	if str(splIPAddr[len(splIPAddr)-1]) == '13':
		return [0.00, 0.00]
	elif str(splIPAddr[len(splIPAddr)-1]) == '14':
		return [6.30, 0.00]
	else:
		logging.error(f'cannot find a coord for AP: {ipAddr}')
		# thrObject.join()
		stop_threads = True
		sys.exit()
def receiveFromAPs():
	global AP_COUNT
	global expectAPCount
	global DEVICE_IP
	global DEVICE_ACC
	global DEVICE_ANGLE

	client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	client.bind(("", PORT))

	debugRssiRaw={}

	f = open("앞면.txt", 'w')

	while True:
		# data, addr = server.recv(1024).decode('utf-8')
		data, addr = client.recvfrom(1024)
		# print("addr:", addr)
		decodedData = data.decode("utf-8")
		# print("received message:", decodedData)

		splitedDataList = decodedData.split(',')
		#print(splitedDataList)
		DEVICE_IP = splitedDataList[3]
		groupedData = list(zip(*[iter(splitedDataList)] * 6))
		# print(groupedData)

		if addr[0] not in APDict:
			# print(addr[0])
			# APDict[addr[0]] = "ap"+str(AP_COUNT)

			# APDict[addr[0]] = dict(id="ap"+str(AP_COUNT), coord=[1,1], tagInfo={})

			apId = "ap"+str(AP_COUNT)
			if expectAPCount > 2:
				apCoor = ip2Coor(addr[0])
			elif expectAPCount == 2:
				apCoor = ip2Coor1D(addr[0])
			
			print(addr[0], apId, apCoor)

			APDict[addr[0]] = AP(apId, apCoor, PORT)
			APDict[addr[0]].mIPAddr = addr[0]

			for unitData in groupedData:
				# APDict[addr[0]]["tagInfo"][unitData[0]] = [unitData[1], unitData[2]] 
				beacon = Beacon(size=SCENE_SIZE)
				# print(float(unitData[1]), int(unitData[2]))
				beacon.rssi = float(unitData[1])
				beacon.rssiHis.append(float(unitData[1]))
				beacon.lastSeq = int(unitData[2])
				DEVICE_ANGLE = int(unitData[4])
				DEVICE_ACC = int(unitData[5])
				APDict[addr[0]].mRcvdBeacon = beacon
				# logging.info(f'ap:{apId}, rssi: {beacon.rssi}')
			AP_COUNT += 1
			# APDict[addr[0]]["tagInfo"][""]
			# debugRssiRaw[apId]=[APDict[addr[0]].mRcvdBeacon.rssi]
		else:
			for unitData in groupedData:
				APDict[addr[0]].mRcvdBeacon.rssi = float(unitData[1])
				APDict[addr[0]].mRcvdBeacon.rssiHis.append(float(unitData[1]))
				APDict[addr[0]].mRcvdBeacon.lastSeq = int(unitData[2])
				DEVICE_ANGLE = int(unitData[4])
				DEVICE_ACC = int(unitData[5])
				# logging.info(f'ap:{APDict[addr[0]].mId}, rssi: {APDict[addr[0]].mRcvdBeacon.rssi }')
				
				# APDict[addr[0]].mRcvdBeacon.applyKF4Rssi()
				# print(APDict[addr[0]].mRcvdBeacon.rssi + ', ' + APDict[addr[0]].mRcvdBeacon.filteredRssi)
				f.write(f"{APDict[addr[0]].mRcvdBeacon.rssi},{APDict[addr[0]].mRcvdBeacon.filteredRssi},{APDict[addr[0]].mRcvdBeacon.getDist()}\n")
		
		if addr[0] in debugRssiRaw:
			debugRssiRaw[addr[0]].append(APDict[addr[0]].mRcvdBeacon.rssi)
		else:
			debugRssiRaw[addr[0]]=[APDict[addr[0]].mRcvdBeacon.rssi]

		global stop_threads
		if stop_threads == True:
			break

		time.sleep(0.05)
def receiveThread():
	receive_thread = threading.Thread(target=receiveFromAPs, args=())
	receive_thread.start()
	return receive_thread

# this is the main entry point of this script
if __name__ == "__main__":
	setattr(Axes3D, 'arrow3D', _arrow3D)
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

	# AP_COUNT=para.APCount[0]
	expectAPCount = para.APCount[0]
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
		# thrObject.join()
		stop_threads = True
		sys.exit()

	pe=[]

	# 1 generate 20*10 room layout
	scene = None 

	# global SCENE_SIZE
	if expectAPCount > 2:
		scene = Scene([SCENE_X, SCENE_Y])
		SCENE_SIZE = scene.getSceneXY()
	elif expectAPCount == 2:
		scene = Scene([6.3, 0.0])
		SCENE_SIZE = scene.getSceneXY()
	# scene = Scene([6.30, 0])

	# pltmap = plt.figure(1)
	# plt.grid(True)

	# initialize APs
	# APDict = {}
	stop_threads = False
	receiveThread()

	# for i, j in zip(range(4), scene.get4Corners()):
	# 	plt.scatter(j[0], j[1], s=40, c='y', marker='s')

	# for key, val in APDict.items():
	# 	print("APs Coord:", val.mCoor[0], val.mCoor[1])
	# 	plt.scatter(val.mCoor[0], val.mCoor[1], s=40, c='y', marker='s')

	# sys.exit()
	# for i, j in zip(range(AP_COUNT), scene.get4Corners()):
	# 	apId = "ap" + str(i)
	# 	# PORT = PORT + 1
	# 	ap = AP(apId, j, PORT)	
	# 	APDict[apId] = ap
	# 	plt.scatter(j[0], j[1], s=40, c='y', marker='s')
	# 	print(apId, j, ap.mIPAddr, ap.mLPort)
	# 	# start receive beacon data
	# 	APDict[apId].receiveThread()

	# print(APDict)
	

	# initialize tags
	TagDict = {}
	for i in range(TAG_COUNT):
		tagId = "tag" + str(i)
	# 	randCoor = [round(np.random.rand() * scene.getSceneX(), 2), 
	# 				round(np.random.rand() * scene.getSceneY(), 2)]

		randCoor = TAG_COORD
		tag = Tag(tagId, randCoor)
		TagDict[tagId] = tag

	# plt.scatter(2.6, 2.4, s=100, c='r', marker='^')
		# print(tagId, randCoor)

	while True:
    		if 	AP_COUNT == TOTAL_AP:
    				break
				
	if len(APDict) < 2:
		logging.error(f'AP count is not enough: {len(APDict)}')
		# thrObject.join()
		stop_threads = True
		sys.exit()

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

	debugRssiFil={}
	

	manPoint = Particle("pman", scene, AP_COUNT)


	cnt = 1
	while True:
	#while simulatedTimestamp <= 10.0:
		logging.info('\n')
		logging.info(f"#######  timestep: {simulatedTimestamp} #######")
		simulatedTimestamp += 0.1
		round(simulatedTimestamp, 2)


		plt.close()
		# if simulatedTimestamp > 0.2:
		# 	sys.exit("DEBUG!!!")

		# plt.axis([-0.5, 10.5, -0.5, 5.5])
		# plt.grid(True)
		# ax1 = fig1.add_subplot(111, projection='3d')
		# fig1= plt.figure(1)
		if AP_COUNT > 2:
			plt.axis([-0.5, scene.getSceneX()+0.5, -0.5, scene.getSceneY()+0.5])
		else:
			plt.axis([-0.5, scene.getSceneX()+0.5, -5, 5])
		plt.grid(True)
		fig1 = plt.figure(1, dpi=300, figsize=(10, 7))
		# ax1=fig.add_axes(projection='3d')
		ax1 = fig1.add_subplot(1, 1, 1, projection='3d')


		randomWalkCnt += 1
	
		# debugParticles = []
		# for i in parFilter.particles:
			# debugParticles.append(i.mCoor)
			# print(i.mId, i.mCoor, parFilter.getWeightMap(i.mCoor))
		# x, y = zip(*debugParticles)
		# plt.scatter(x, y)
		# trilateration
		sysMat=[]

		combVec = [0.0, 0.0]
		# 2.1 preprocess rssi data
		# rawRSSIList=[]
		# filRSSIList=[]
		for i in APDict.values():
			ax1.scatter(i.getX(), i.getY(), [0], s=40, c='y', marker='s')
			ax1.text( i.getX(), i.getY(), 0, i.mId )
			apLoc = [i.getX(), i.getY()]
			if i.mRcvdBeacon != None:
				# rawRSSIList.append(i.mRcvdBeacon.rssi)
				if para.KFoff == True:
					i.mRcvdBeacon.applyAvgRssi()
					i.mRcvdBeacon.rssiHisFil.append(i.mRcvdBeacon.filteredRssi)
					# logging.info(f'ap:{i.mId}, filtered rssi: {i.mRcvdBeacon.filteredRssi}')
					if i.mId in debugRssiFil:
						debugRssiFil[i.mId].append(i.mRcvdBeacon.filteredRssi)
					else:
						debugRssiFil[i.mId]=[i.mRcvdBeacon.filteredRssi]
				else:
					i.mRcvdBeacon.applyKF4Rssi()
					#i.mRcvdBeacon.applyMA()
					i.mRcvdBeacon.rssiHisFil.append(i.mRcvdBeacon.filteredRssi)
					# logging.info(f'ap:{i.mId}, filtered rssi: {i.mRcvdBeacon.filteredRssi}')
					if i.mId in debugRssiFil:
						debugRssiFil[i.mId].append(i.mRcvdBeacon.filteredRssi)
					else:
						debugRssiFil[i.mId]=[i.mRcvdBeacon.filteredRssi]
				# filRSSIList.append(i.mRcvdBeacon.filteredRssi)
			else:
				# thrObject.join()
				stop_threads = True
				sys.exit("AP's beacon is None")

			# i.mRcvdBeacon.setSize(scene.getSceneXY())
			apLoc.append(i.mRcvdBeacon.getRawDist())
			sysMat.append(apLoc)

		if schemeName == 'tril':

			if expectAPCount > 2:
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

			elif expectAPCount == 2:
				# trilateration			
				# using 3rd element of ele in sysMat to calculate location in 1d
				loc1d = []
				if sysMat[0][0] > sysMat[1][0]:
					EstX1d = math.fabs(sysMat[0][0] - sysMat[0][2])
					EstLoc1d = (EstX1d + sysMat[1][0])/2
					loc1d.append(EstLoc1d)
					# logging.info(f'{EstX1d}, {EstLoc1d}')
				else:
					EstX1d = math.fabs(sysMat[1][0] - sysMat[1][2])
					EstLoc1d = (EstX1d + sysMat[0][0])/2
					loc1d.append(EstLoc1d)
					# logging.info(f'{EstX1d}, {EstLoc1d}')

				loc1d.append(0)
				# print(sysMat, loc1d)
				manPoint.setXY(round(float(loc1d[0]),2), round(float(loc1d[1]),2))


			# logging.info(f'tril: {schemeName}, {sysMat}, {triEstPos}, {manPoint.getX()}, {manPoint.getY()}')
			## angle and magnitude calculation
			# instMag = i.mRcvdBeacon.getCurrMag()
			# angle = i.angle2Me(tCoor=manPoint.mCoor) # manPoint.mCoor

			# xyProj = projectXY(angle, instMag)
			# combVec = combine2XYVec(combVec, xyProj)

			# degee = math.degrees(angle)
			# logging.info(f"{i.mId}, magnitude: {instMag}, angle: {angle}, ({round(degee,2)})")
			# logging.info(" ")

		# fileName = f'pe/rssiData.csv'
		# with open(fileName, 'a') as f:
		# 	f.write(f'{",".join(str(x) for x in rawRSSIList)}, , {",".join(str(x) for x in filRSSIList)}\n')

		#if para.MovePathOn: #ja
		#	parFilter.updateMotion(DEVICE_ANGLE, DEVICE_ACC)

		if schemeName == 'oips':
			# 2.2 particle filter
			if randomWalkCnt == RANDOM_WALK_CNT:
				# manPoint = parFilter.getAvgParticle()
				if expectAPCount > 2:
					parFilter.move(1.0, 1.0)
				elif expectAPCount == 2:
					parFilter.move(1.0, 0.0)

				randomWalkCnt = 0
				# plot estimated location
				# plt.scatter(manPoint.getX(), manPoint.getY(), s=100, c='g', marker='v')
				# print(manPoint.getX(), manPoint.getY())
				# print("Localization error: %f", TagDict.)
				# 2.3 particle filter resampling process
				parFilter.resample(list(APDict.values()), ax1)
			manPoint = parFilter.getAvgParticle()

		elif schemeName == 'ips':
			'''update particles' weights'''
			parFilter.updateWeight(list(APDict.values()))

			# 2.3 particle filter resampling process
			effeSZ = parFilter.effeSampleSize()
			logging.info(f"effecSampleSize: {effeSZ}")
			#if effeSZ < PARTICLE_COUNT*EFFPARATIO:
			if cnt % 5 == 0:
				if resamplingWay == 'MN':
					parFilter.resampleMultinomial(list(APDict.values()), ax1)
				elif resamplingWay == 'SUS':
					parFilter.resampleSUS(list(APDict.values()), ax1)  #[j] resampling 끄고 켜기
					if para.MovePathOn: #ja
						parFilter.updateMotion(DEVICE_ANGLE, DEVICE_ACC)
					None
				else:
					logging.error(f' unrecognized resampling approach: {resamplingWay}')
					# thrObject.join()
					stop_threads = True
					sys.exit()
		
		# estimated location
		manPoint = parFilter.getAvgParticle()
		# plot estimated location
		ax1.scatter(manPoint.getX(), manPoint.getY(), s=100, c='g', marker='v', label='Estimated location')
		ax1.text( manPoint.getX(), manPoint.getY(), 0, f'Est.: ({manPoint.getX()}, {manPoint.getY()})' )
		print("angle is {}".format(DEVICE_ANGLE))

		print(manPoint.getX(), manPoint.getY(), " ==> " , manPoint.getX()  +np.sin(DEVICE_ANGLE), manPoint.getY() +np.cos(DEVICE_ANGLE))
		print(math.sin(math.pi * (DEVICE_ANGLE / 180))  , math.cos(math.pi * (DEVICE_ANGLE / 180)))
		ax1.arrow3D(
			manPoint.getX(), manPoint.getY(), 0,
			math.sin(math.pi * (DEVICE_ANGLE / 180))  * 1.5, math.cos(math.pi * (DEVICE_ANGLE / 180)) *1.5, 0,
			mutation_scale=25,
			arrowstyle="-|>",
			ec ='black',
			fc='red'
		)
		
		logging.info(f"Tag Estimated Location: {manPoint.getX()}, {manPoint.getY()}" )

		'''for visualization'''
		pCoorX = [parFilter.particles[x].mCoor[0] for x in range(parFilter.numParticles)]
		pCoorY = [parFilter.particles[x].mCoor[1] for x in range(parFilter.numParticles)]
		pWeigh = [parFilter.particles[x].probability for x in range(parFilter.numParticles)]
		logging.debug( pWeigh )
		ax1.scatter(pCoorX, pCoorY, pWeigh)

		ax1.set_xlabel('Room Length (m)')
		ax1.set_ylabel('Room Width (m)')
		ax1.set_zlabel('Weight')
		
		# evaluate average errors of particles
		tagList = list(TagDict.values())
		error = 0.0
		# error = round(evaluate(tagList[0], parFilter.particles, scene), 2)
		if manPoint:
			accur = round(evaluateAccu(tagList[0], manPoint), 2)
		logging.info(f'RMSE: {error}, Accur: {accur}')
		pe.append([error, accur, str(manPoint.getX())+' '+str(manPoint.getY())])

		# plt.draw()
		# plt.pause(0.0001)
		time.sleep(0.08)
		# plt.clf()
		# fig1.tight_layout()

		# ======================== Send to PDR =========================== #

		HOST = DEVICE_IP #smartphone ip addr
		PORT = 5050
		ADDR = (HOST,PORT)
	
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		manPoint.mCoor[1] = scene.getSceneY() -  manPoint.getY()
		msg = str(manPoint.getX()) + ',' + str(manPoint.getY()) + '\n'
		encodedMsg = msg.encode(encoding="utf-8")
		client_socket.sendto(encodedMsg, (ADDR))

		# ================================================================ #

		if visualize:
			#ax1.tricontour(pCoorX, pCoorY, pWeigh, zdir='z', levels=14, linewidths=1, cmap=plt.cm.hot)	
			if cnt % 5 != 0:
				plt.show(block=False)
				plt.pause(0.3)
				plt.close()	
				#plt.show()
			else:
				plt.show()
		cnt += 1
		#parFilter.downgradeWeight()

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

	# fig1.tight_layout()
	# if visualize:
		# ax1.tricontour(pCoorX, pCoorY, pWeigh, zdir='z', levels=14, linewidths=1, cmap=plt.cm.hot)	
		# plt.show()	

	# thrObject.join()
	stop_threads = True

	# print(debugRssiFil)

	if para.KFoff:
		schemeName = 'sp'
	'''
	fileName = f'pe-exp/peData-exp-{schemeName}-ap-{AP_COUNT}-sigma-{para.sigma[0]}-coor-{TAG_COORD[0]}-{TAG_COORD[1]}-s-{para.seed[0]}.csv'
	with open(fileName, 'w') as f:
		f.write(f'scheme,{schemeName}\n')
		f.write(f'effPaRatio:{EFFPARATIO}\n')
		f.write(f'paMeasNoise:{PAMEASNOISE}\n')
		f.write(f'seed,{para.seed[0]}\n')
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
	'''
	# fileName = f'pe-exp/peData-exp-data-coor-{TAG_COORD[0]}-{TAG_COORD[1]}-s-{para.seed[0]}.csv'
	# with open(fileName, 'w') as f:
	# 	for i in debugRssiFil:
	# 		f.write(f'{i},')

# def init():


# def animate(i):
