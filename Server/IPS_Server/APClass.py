from scipy.spatial import distance
import numpy as np
import socket
import argparse
import threading
import logging, time

from TagClass import Tag
from Beacon import Beacon

class AP:
	"""docstring for AP"""
	
	def __init__(self, mId, mCoor, mLPort):
		super(AP, self).__init__()
		self.mId = mId
		self.mCoor = mCoor
		self.mIPAddr = socket.gethostbyname(socket.gethostname())
		self.mLPort = mLPort
		self.mRcvdBeacon = None
		self.user_list = {}

	def getX(self):
		return self.mCoor[0]

	def getY(self):
		return self.mCoor[1]

	def angle2Me(self, tCoor):
		para=(self.mCoor[0]-tCoor[0])/ distance.euclidean(self.mCoor, tCoor)
		angle = np.arccos(para)
		return angle

	def generateExactRSSI(self, tagCoor):
		dist = distance.euclidean(self.mCoor, tagCoor)
		beacon = Beacon(size=[1,1], _from = self.mIPAddr) # dummy size
		return beacon.dist2rssi(dist)

	def generateErrorRSSI_Normal(self, tagCoor, sigma=1):
		# rssi_e = sigma * np.random.randn() + self.generateExactRSSI(tagCoor)
		rssi_e = np.random.normal(self.generateExactRSSI(tagCoor), sigma)
		# logging.info(f"Exact RSSI: {self.generateExactRSSI(tagCoor)} at ({tagCoor})")
		return rssi_e

	def getMyIPAddr(self):
		localIPAddr = socket.gethostbyname(socket.gethostname())
		return localIPAddr

	def receiveThread(self):
		receive_thread = threading.Thread(target=self.accept_func, args=())
		receive_thread.start()		

	def accept_func(self):
		server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind(("", self.mLPort))

		while True:
			# data, addr = server.recv(1024).decode('utf-8')
			data, addr = server.recvfrom(1024)
			print(f"received message: {data}")
			# self.user_list[user] = client_socket

	# def msg_func(self, msg):
	# 	print(msg)
	# 	for con in self.user_list.values():
	# 		try:
	# 			con.send(msg.encode('utf-8'))
	# 		except:
	# 			print("연결이 비 정상적으로 종료된 소켓 발견")

	# def handle_receive(self, client_socket, addr, user):
	# 	msg = "---- %s connection ----" % user
	# 	self.msg_func(msg)
	# 	while 1:
	# 		data = client_socket.recv(1024)
	# 		string = data.decode('utf-8')

	# 		if "/exit" in string:
	# 			msg = "---- %s closed . ----" % user
	# 			#유저 목록에서 방금 종료한 유저의 정보를 삭제
	# 			del self.user_list[user]
	# 			self.msg_func(msg)
	# 			break

	# 		string = "%s : %s" % (user, string)
	# 		self.msg_func(string)

	# 	client_socket.close()
