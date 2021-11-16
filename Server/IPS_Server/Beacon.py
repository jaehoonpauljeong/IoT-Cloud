from MovingAverage import MovingAverage
import logging,math
import numpy as np
from collections import deque
from scipy import signal
from scipy.spatial import distance

from KalmanFilter import KalmanFilter

class Beacon:
	"""docstring for Beacon"""
	
	coeffA = 0.00002803
	coeffB = -0.1409

	n = 1.14671509 
	a = -72.6929423

	#n = 0.83901063 
	#a = -65.11187992

	# n = 0.75344983 
	# a = -67.44388786

	def __init__(self, size=[0,0], _from=""):
		super(Beacon, self).__init__()
		self.lastSeq = 0
		self.kFilter = KalmanFilter(processNoise=0.01,measurementNoise=20)
		self.MAFilter = MovingAverage(alpha = 0.5) #ja
		self.rssi = 0.0
		self.filteredRssi = 0.0
		self.rssiHis = deque([],60)
		self.rssiHisFil = deque([],60)
		self.size=size
		self.maxDist=distance.euclidean([0,0], self.size)
		
		if _from == "192.168.1.74":
			n = 1.10282199
			a = -66.70638174		
		elif _from == "192.168.1.38":
			n = 1.20433379
			a = -66.86683432

		elif _from == "192.168.1.44":
			n = 1.17592762
			a  = -62.41854648
      
		elif _from == "192.168.1.103":
			n = 2.31223909
			a = -57.57862279
		elif _from == "192.168.1.79":
			n = 1.68997563
			a  = -62.46355815
	def setSize(self, size):
		self.size = size

	def dist2rssi(self, x):
		# original
		# rssi = (math.log(dist) - math.log(self.coeffA)) / self.coeffB

		# for RPI
		rssi = -10*self.n*np.log10(x)+self.a
		return rssi

	def rssi2dist(self, rssi):
		# original:
		# dist = self.coeffA * math.exp(self.coeffB * rssi)

		# for RPI
		power =  (self.a-rssi)/(10.0*self.n)
		dist = pow(10,power)
		return dist

	def applyMA(self):  #ja
		self.filteredRssi = self.MAFilter.applyFilter(self.rssiHis)
		return self.filteredRssi

	def applyKF4Rssi(self):
		self.filteredRssi = self.kFilter.applyFilter(rssi=self.rssi)
		return self.filteredRssi

	def applyKFAvgRssi(self):
		self.filteredRssi = np.average(self.rssiHisFil)
		return self.filteredRssi

	def applyAvgRssi(self):
		self.filteredRssi = np.average(self.rssiHis)
		return self.filteredRssi

	def getDist(self):
		# dist = self.coeffA * math.exp(self.coeffB * self.filteredRssi)
		power =  (self.a-self.filteredRssi)/(10.0*self.n)
		# power =  (self.a-self.rssi)/(10.0*self.n)

		dist = pow(10,power)

		# maxDist=distance.euclidean([0,0], self.size)
		if dist > self.maxDist:
			return self.maxDist
		else:
			return dist

	def getRawDist(self):
		# dist = self.coeffA * math.exp(self.coeffB * self.filteredRssi)
		power =  (self.a-self.rssi)/(10.0*self.n)
		dist = pow(10,power)
		
		# maxDist=distance.euclidean([0,0], self.size)
		if dist > self.maxDist:
			return self.maxDist
		else:
			return dist

	def getGradAcc(self):
		"""get acceleration of rssi, i.e., the changing rate of speed (gradient)

		Returns:
			list: differential values of recent gradient data points
		"""
		res=self.getGrad()
		if len(res)>0:
			res = [0.0] + res
			resf2 = [res[a + 1] - res[a] for a in range(len(res)-1)]
			return resf2
		else:
			resf2=[0.0]
			return resf2

	def getGrad(self):
		"""get gradient of rssi list, i.e., the changing rate of rssi for this beacon

		Returns:
			list: differential values of recent 60 filtered rssi data points
		"""
		rssiHF=self.rssiHisFil
		resf = [rssiHF[a + 1] - rssiHF[a]for a in range(len(rssiHF)-1)]
		return resf

	def getGradFromNP(self):
		"""get gradient of rssi list from numpy built-in gradient function.

		Returns:
			list: gradient of rssi
		"""
		rssiHF=list(self.rssiHisFil)
		gRssi = []
		if len(rssiHF)<2:
			rssiHF=[0.0]+rssiHF
			rssi = np.array(rssiHF, dtype=float)
			# logging.info(f"rssi in getGradFromNP: {rssi}")
			gRssi = np.gradient(rssi)
		else:
			rssi = np.array(rssiHF, dtype=float)
			# logging.info(f"rssi in getGradFromNP: {rssi}")
			gRssi = np.gradient(rssi)
		return gRssi

	def gradButterFilter(self, order=3, freq=0.05):
		"""using the Butterworth filter to get low frequency part of gradients

		Args:
			order (int, optional): the order of the filter. Defaults to 3.
			freq (float, optional): the frequency to keep, e.g., 0.1 means keeping signals below 100Hz. Defaults to 0.05.

		Returns:
			list: filtered gradient data points
		"""
		xn = self.getGrad()
		# xn = self.getGradFromNP()
		if len(xn)>0:
			xn = [0.0] + xn
			# for ele in xn:
				# t = np.linspace(1.0, len(ele), len(ele))
			# b, a = signal.butter(order, freq)
			sos = signal.butter(order, freq, output='sos')

			# zi = signal.lfilter_zi(b, a)
			# z, _ = signal.lfilter(b, a, xn, zi=zi*xn[0])
			# z2, _ = signal.lfilter(b, a, z, zi=zi*xn[0])
			# y = signal.filtfilt(b, a, xn)
			y = signal.sosfiltfilt(sos, np.array(xn), padlen=0)
			return y
		else:
			y = [0.0]
			return 	y
	
	def getCurrMag(self):
		"""get current magnitude of velocity after filtering

		Returns:
			float: magnitude of this moment of gradient
		"""
		filteredGrad=self.gradButterFilter()
		return filteredGrad[len(filteredGrad)-1]