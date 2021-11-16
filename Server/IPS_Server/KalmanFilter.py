class KalmanFilter():
	"""docstring for KalmanFilter"""

	# processNoise = 0.0 # Process noise
	# measurementNoise = 0.0 # Measurement noise
	# estimatedRSSI = 0.0 # calculated rssi
	# errorCovarianceRSSI = 0.0 # calculated covariance
	# isInitialized = False # initialization flag

	def __init__(self, processNoise, measurementNoise):
		super(KalmanFilter, self).__init__()
		self.processNoise = processNoise # Process noise
		self.measurementNoise = measurementNoise # Measurement noise
		self.estimatedRSSI = 0.0 # calculated rssi
		self.errorCovarianceRSSI = 0.0 # calculated covariance
		self.isInitialized = False # initialization flag

	def applyFilter(self, rssi):
		priorRSSI = 0.0
		kalmanGain = 0.0
		priorErrorCovarianceRSSI = 0.0

		if not self.isInitialized:
			priorRSSI = rssi
			priorErrorCovarianceRSSI = 1
			self.isInitialized = True
		else:
			priorRSSI = self.estimatedRSSI
			priorErrorCovarianceRSSI = self.errorCovarianceRSSI + self.processNoise

		kalmanGain = priorErrorCovarianceRSSI / (priorErrorCovarianceRSSI + self.measurementNoise)
		self.estimatedRSSI = priorRSSI + (kalmanGain * (rssi - priorRSSI))
		self.errorCovarianceRSSI = (1 - kalmanGain) * priorErrorCovarianceRSSI

		return self.estimatedRSSI	