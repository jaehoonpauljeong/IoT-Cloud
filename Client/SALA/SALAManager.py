import ScanUtility
import socket
import time

from uuid import getnode as get_mac

mac = str(hex(get_mac()))[2:]
SALAServerIP = "192.168.1.74"
SALAServerPort = 50007

def sendMsg(beaconMsg):
    reportMsg = makeSALAformat(beaconMsg)
    print("\n===== changing to SALA data format =====")
    print(reportMsg)
    try:
        with socket.socket() as s:
            s.connect((SALAServerIP, SALAServerPort))
            s.sendall(reportMsg.encode())
            print("============ done sending ==============")
    except:
        print("=================================")
        print("!! Unable to connect SALA Server! Please check again...!!")
        print()
        
def makeSALAformat(beaconMsg):
    builder = mac + '\n'
    builder += changeMac() + '\n'
    builder += getIPv6byFile() + '\n'
    builder += str(1) + '\n'
    builder += str(int(time.time())) + ' ' + str(beaconMsg.x_cor) + ' ' + str(beaconMsg.y_cor) + ' ' + str(beaconMsg.rssi)
    
    return builder

def changeMac():
    tmp = mac
    tmp = tmp[:2] + ":" + tmp[2:4] + ":" + tmp[4:6] + ":" + tmp[6:8] + ":" + tmp[8:10] + ":" + tmp[10:12]
    return tmp

def getmyIPv4():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    result = s.getsockname()[0]
    s.close()
    return result

def getIPv6byFile():
    f = open("/home/pi/DNSNA_Client_1/Local_ipaddr.file")
    ipaddr = f.read()
    return ipaddr

def getmyIPv6():
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    s.connect(("2001:4860:4860::8844", 80))
    print(s.getsockname())
    result = s.getsockname()[0]
    s.close()
    return result
