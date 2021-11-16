class Scene:
	"""docstring for Scene"""

	origin = [0,0]
	# scene size: m
	# sceneSize = [0,0]

	def __init__(self, sceneSize = [20.00,10.00]):
		super(Scene, self).__init__()
		self.sceneSize = sceneSize
	
	def getSceneX(self):
		return self.sceneSize[0]

	def getSceneY(self):
		return self.sceneSize[1]

	def getSceneOri(self):
		return self.origin

	def getSceneXY(self):
		return self.sceneSize

	def get4Corners(self):
		return [self.origin,
				self.sceneSize,
				[self.origin[0], self.sceneSize[1]], 
				[self.sceneSize[0], self.origin[1]]]

	def genAPPos(self, APcount):
		if APcount == 2:
			return [[self.origin[0], self.origin[0]],
					[self.sceneSize[0], self.origin[0]]]
		elif APcount ==4:
			return [self.origin,
					self.sceneSize,
					[self.origin[0], self.sceneSize[1]], 
					[self.sceneSize[0], self.origin[1]]]
		elif APcount == 6:
			return [self.origin,
					self.sceneSize,
					[self.origin[0], self.sceneSize[1]], 
					[self.sceneSize[0], self.origin[1]],
					[self.sceneSize[0]/2.0, self.origin[1]],
					[self.sceneSize[0]/2.0, self.sceneSize[1]]]
		elif APcount == 8:
			return [self.origin,
					self.sceneSize,
					[self.origin[0], self.sceneSize[1]], 
					[self.sceneSize[0], self.origin[1]],
					[self.sceneSize[0]/3, self.origin[1]],
					[self.sceneSize[0]*2/3, self.origin[1]],
					[self.sceneSize[0]/3, self.sceneSize[1]],
					[self.sceneSize[0]*2/3, self.sceneSize[1]]]