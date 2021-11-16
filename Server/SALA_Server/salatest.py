#-*- coding:utf-8 -*-
import salabase
import sala_algorithm
import sala_server_main
import sys
import os
import csala
import time

# iot Device Informations
sala_information = {}

# read exist IoT information
print("[Init] Initialization Start...")
file_list = os.listdir('./')

for filename in file_list:
	try:
		iotname, extend = filename.split('.')
		if extend != "sala":
			continue
		print("[Init] Read sala file:", filename)
		exist_file = open( filename, "r", encoding="UTF-8" )
		read_data = ''
		while True:
			line = exist_file.readline()
			if not line:
				break
			read_data += line

		exist_file.close()
		sala_server_main.client_data_processing_exist(sala_information, read_data)
	except:
		pass

print("[Init] Initialization DONE")


print("[SALA] SALA Update start!")
startTime = time.time()

sala_algorithm.run_sala_algorithm(sala_information)
print("[SALA] done")
endTime = time.time() - startTime
print("Cost : " + str(endTime))

for mac, info in sala_information.items():
	print("mac:", mac)
	print("device:", info["device"])
	print("location:", info["location"])
	print("centroid:", info["centroid"])
