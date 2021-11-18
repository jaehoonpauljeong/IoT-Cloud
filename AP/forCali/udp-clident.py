#!/usr/bin/env python3
# by Yiwen Shen (SKKU)
# Email: chrisshen@skku.edu

import socket
import time
import bluetooth
import sys
import threading

import ScanUtility
import bluetooth._bluetooth as bluez

SERVER_IP = "192.168.1.30"

#Set bluetooth device. Default 0.
beacons4Server = {}

seq = 0
# byteData = B""
deviceMap = {}
def rcvdBeacon():
    dev_id = 0
    global seq
    try:
        sock = bluez.hci_open_dev(dev_id)
        print ("\n *** Looking for BLE Beacons ***\n")
        print ("\n *** CTRL-C to Cancel ***\n")
    except:
        print ("Error accessing bluetooth")

    ScanUtility.hci_enable_le_scan(sock)
    #Scans for iBeacons
    try:
        while True:
            returnedList = ScanUtility.parse_events(sock,deviceMap, 100)

            
            if returnedList:
                for item in returnedList:
                    if seq >= 12:
                        seq = 0
                    else:
                        seq += 1
                    beacons4Server[item['uuid']] = [item['rssi'], item['device_ip'], seq]
                    
                    print(" ")
            
                returnedList.clear()
    except KeyboardInterrupt:
        pass

def sendUDP():
    # IPv4
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(0.2)

    currSeq = 0
    prevSeq = 0
    while True:
        message = ""
        for key, val in beacons4Server.items():
            #message = str(key) + "," + str(val) + "," + str(seq) + ","

            message = str(key) + "," + str(val[0]) + "," +str(val[1]) +"," + str(val[2]) +","
            currSeq = val[2]
            
        if currSeq != -1 and currSeq != prevSeq:
            #(message)
            prevSeq = currSeq
            encodedMsg = message.encode(encoding="utf-8")
            timestamp = time.time()
            s = str(timestamp)
            message1 = s+  "," + str(key) + "," + str(val[0]) + ","  + str(val[2]) 
            print(message1)
            # print(byteData)
            client.sendto(encodedMsg, (SERVER_IP, 6000)) # 2001:db8:100:15a::3
            client.sendto(encodedMsg, ("192.168.1.50", 6000))
            #print("message sent!")
        else:
            pass
        time.sleep(0.02)

if __name__ == "__main__":
    # rcvdBeacon()

    rcvdBeaconTh = threading.Thread(target=rcvdBeacon, args=())
    rcvdBeaconTh.start()

    udpSendBeaconTh = threading.Thread(target=sendUDP, args=())
    udpSendBeaconTh.start()
