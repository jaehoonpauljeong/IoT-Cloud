class Point():
	"""docstring for Point"""
	
	# mCoor = [0.0, 0.0]
	# x = 0.0
	# y = 0.0

	def __init__(self, coor=[0.0, 0.0]):
		super(Point, self).__init__()
		self.mCoor = coor
		self.x = coor[0]
		self.y = coor[1]

	def getX(self):
		return self.x

	def getY(self):
		return self.y
		