import socket
import time
import bluetooth
import sys
import threading

import ScanUtility
import bluetooth._bluetooth as bluez

dev_id = 0
global seq
try:
    sock = bluez.hci_open_dev(dev_id)
    print ("\n *** Looking for BLE Beacons ***\n")
    print ("\n *** CTRL-C to Cancel ***\n")
except:
    print ("Error accessing bluetooth")


deviceMap = {}
ScanUtility.hci_enable_le_scan(sock)

try:
    ScanUtility.parse_events(sock, deviceMap)
except KeyboardInterrupt:
    pass

    
