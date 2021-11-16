from scipy.spatial import distance

from Beacon import Beacon


class Tag:
	"""docstring for Tag"""

	# my coordinates [x,y]
	# mId = ""
	# mCoor = [0.0, 0.0]

	def __init__(self, mId, mCoor):
		super(Tag, self).__init__()
		self.mId = mId
		self.mCoor = mCoor
		self.speed = 0.0
		self.acc = 0.0
		self.dir = 0.0

	def generateExactRSSI(self):
		# beacon = Beacon()
		# return beacon.dist2rssi()
		pass

	def generateErrorRSSI(self):
		pass

	def getX(self):
		return self.mCoor[0]
	
	def getY(self):
		return self.mCoor[1]

	def getExactLocation(self):
		return self.mCoor

	def getDist2AP(self, apCoor):
		return distance.euclidean(self.mCoor, apCoor)
		