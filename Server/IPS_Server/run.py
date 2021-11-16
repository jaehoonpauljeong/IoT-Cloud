#!/home/chris/anaconda3/bin/python
import importlib 
import subprocess, logging, sys
import numpy as np
# bips = importlib.import_module("BeaconIPS-main", __name__)

def genPath(start, end):
	path=[]
	if start[0] == end[0]:
		# n = np.abs(end[1]-start[1])/1.0
		# path=[[start[0],y] for y in np.linspace(start[1], end[1], num=int(n))]
		if end[1] < start[1]:
			path = [[start[0], y] for y in range(int(start[1]), int(end[1]), -1)]
		else:
			path = [[start[0], y] for y in range(int(start[1]), int(end[1]))]
		return path
	elif start[1] == end[1]:
		# n=np.abs(end[0]-start[0])/1.0
		# path=[[x,start[1]] for x in np.linspace(start[0], end[0], num=int(n))]
		if end[0] < start[0]:
			path = [[x, start[1]] for x in range(int(start[0]), int(end[0]), -1)]
		else:
			path = [[x, start[1]] for x in range(int(start[0]), int(end[0]))]
		return path
	else:
		logging.error('start and end must have one same point, either x or y.')
		sys.exit()

def genPathRect(scene, start):
	path = []
	path += genPath(start, [start[0], scene[1]-2])
	path += genPath([start[0], scene[1]-2], [scene[0]-2, scene[1]-2])
	path += genPath([scene[0]-2, scene[1]-2], [scene[0]-2, start[1]])
	path += genPath([scene[0]-2, start[1]], start)
	return path

if __name__ == "__main__":

	logging.basicConfig(level=logging.INFO)

	path = genPathRect([20, 10], [2,2])

	path =genPath([2, 0], [18, 0])
	logging.info(f'path info: {path}')
	# sys.exit()
	for ele in path:
		for seed in range(2):
			logging.info(f"ele:{ele}, seed: {seed}")
			# 2 ap case
			subprocess.run(['/home/chris/usr/BeaconIPS-python/BeaconIPS-main.py', '--sigma', '1', '--tagCoord', str(ele[0]), str(ele[1]), '--seed', str(seed), '--APCount', '2', '--effPaRatio', '0.8', '--paMeasNoise', '0.8', '--scheme', 'ips'] )
			
			# subprocess.run(['/home/chris/usr/BeaconIPS-python/BeaconIPS-main.py', '--sigma', '3', '--tagCoord', str(ele[0]), str(ele[1]), '--seed', str(seed)], )

			# subprocess.Popen(['/home/chris/usr/BeaconIPS-python/BeaconIPS-main.py', '--sigma', '1', '--tagCoord', str(ele[0]), str(ele[1]), '--seed', str(seed)],  )

			# sp
			# subprocess.run(['/home/chris/usr/BeaconIPS-python/BeaconIPS-main.py', '--sigma', '1', '--tagCoord', str(ele[0]), str(ele[1]), '--seed', str(seed), '--APCount', '6', '--effPaRatio', '0.8', '--paMeasNoise', '0.8', '--scheme', 'ips', '--KFoff'], )

			# tril
			# subprocess.run(['/home/chris/usr/BeaconIPS-python/BeaconIPS-main.py', '--sigma', '1', '--tagCoord', str(ele[0]), str(ele[1]), '--seed', str(seed), '--APCount', '6', '--scheme', 'tril'], )		

			# oips
			# subprocess.run(['/home/chris/usr/BeaconIPS-python/BeaconIPS-main.py', '--sigma', '1', '--tagCoord', str(ele[0]), str(ele[1]), '--seed', str(seed), '--APCount', '6', '--scheme', 'oips'], )		