#-*- coding:utf-8 -*-
from math import sqrt

class DeviceInfo:
	ssid = ""
	macaddr = ""
	ipaddr = ""
	
	def __init__(self, ssid, macaddr, ipaddr):
		self.ssid = ssid
		self.macaddr = macaddr
		self.ipaddr = ipaddr

	def __repr__(self):
		return str( {"ssid":self.ssid, "mac":self.macaddr, "ip":self.ipaddr} )

class Pos:
	x = 0
	y = 0

	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __repr__(self):
		return str( {"x":self.x, "y":self.y} )

class Report:
	timestamp = -1
	position = None
	rssi = 0

	def __init__(self, timestamp, px, py, rssi):
		self.timestamp = timestamp
		self.position = Pos(px, py)
		self.rssi  = rssi 

	def __repr__(self):
		return str( {"time":self.timestamp, "position":str(self.position), "RSSI":self.rssi} )



class PowerDistanceTable(list):

	def add(self, point, power, distance, avg_dist, std_dist):
		entry = dict()
		entry["point"] = point
		entry["power"] = power
		entry["distance"] = distance
		entry["avg_dist"] = avg_dist
		entry["std_dist"] = std_dist
		self.append(entry)

# 거리공식 (power distance table용) -> round가 있으서 밑에것과 추후 통합 예정
def find_distance(position1, position2):   # distance를 구하는 함수
    return round(sqrt((position1.x-position2.x)*(position1.x-position2.x)
                      + (position1.y - position2.y) * (position1.y - position2.y)), 1)


# 거리공식 (grid weight map용)
def distance2(x1, x2, y1, y2):
    x = x1-x2
    y = y1-y2
    d = sqrt(x*x + y*y)
    return d


# Common variables
m = 10      # number of test points (base: 2m)
prodistance = 200   # distance between wall and centroid which is condition of wallcorner handling
