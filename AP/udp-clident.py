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

SERVER_IP = "192.168.1.29"

#Set bluetooth device. Default 0.
beacons4Server = {}

seq_n = 0

# byteData = B""
deviceMap = {}
def rcvdBeacon():
    dev_id = 0
    global seq_n

    try:
        sock = bluez.hci_open_dev(dev_id)
        print ("\n *** Looking for BLE Beacons ***\n")
        print ("\n *** CTRL-C to Cancel ***\n")
    except:
        print ("Error accessing bluetooth")

    ScanUtility.hci_enable_le_scan(sock)
    #Scans for iBeacons
    try:
        seq_n = 0
        while True:
            returnedList = ScanUtility.parse_events(sock,deviceMap, 100)

            if returnedList:
                for item in returnedList:
                    beacons4Server[item['uuid']] = [item['rssi'], seq_n, item['device_ip'], item['device_angle'], item['device_acc']]
                    seq_n += 1
                    print(" ")
            
                returnedList.clear()

                if seq_n > 12:
                    seq_n = 0
    except KeyboardInterrupt:
        pass

def sendUDP():
    global seq_n
    # IPv4
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(0.2)

    prevSeq = 0
    while True:
        message = ""
        for key, val in beacons4Server.items():
            message = str(key) + "," + str(val[0]) + "," + str(val[1]) + "," + str(val[2]) + "," + str(val[3]) + "," + str(val[4]) + ","
            
        if seq_n != prevSeq:
            #(message)
            prevSeq = seq_n
            encodedMsg = message.encode(encoding="utf-8")

            client.sendto(encodedMsg, (SERVER_IP, 6000))
            client.sendto(encodedMsg, ("192.168.1.35", 6000))
            print("message sent!")
        
        time.sleep(0.5)

if __name__ == "__main__":
    # rcvdBeacon()

    rcvdBeaconTh = threading.Thread(target=rcvdBeacon, args=())
    rcvdBeaconTh.start()

    udpSendBeaconTh = threading.Thread(target=sendUDP, args=())
    udpSendBeaconTh.start()
