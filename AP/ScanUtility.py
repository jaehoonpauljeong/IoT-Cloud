import sys
import struct
import time
import bluetooth._bluetooth as bluez

class BeaconMSG:
    def __init__(self, recvData):
        self.recvData = recvData
        self.ip_address = ""
        self.x_cor = 0
        self.y_cor = 0
        self.device_angle = 0
        self.device_acc = 0
        self.rssi = 0
        self.count = 2
        self.pre_data = ""
    def reset(self):
        self.recvData = ""
        self.ip_address = ""
        self.x_cor = 0
        self.y_cor = 0
        self.device_angle = 0
        self.device_acc = 0
        self.rssi = 0
        self.count = 2
        self.pre_data = ""

OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_ENABLE=0x000C

def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)

def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)

def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)

def packetToString(packet):
    """
    Returns the string representation of a raw HCI packet.
    """
    if sys.version_info > (3, 0):
        return ''.join('%02x' % struct.unpack("B", bytes([x]))[0] for x in packet)
    else:
        return ''.join('%02x' % struct.unpack("B", x)[0] for x in packet)

def reverseUuid(target):
    result = ""
    for i in range(15, -1, -1):
        result += target[i*2] + target[i*2 + 1]
    return result

def parse_events(sock, deviceMap, loop_count=100):
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
    results = []
    
    startTime = time.time()

    for i in range(0, loop_count):
        packet = sock.recv(255)
        dataString = packetToString(packet)
        rssi, = struct.unpack("b", packet[len(packet)-1:])
     
        if len(dataString) > 64: 
            reversedUuid = reverseUuid(dataString[32:64])
            if reversedUuid in deviceMap:
                recvData = dataString[64:len(dataString)-2]
                if deviceMap[reversedUuid].pre_data != recvData:
                    deviceMap[reversedUuid].recvData = deviceMap[reversedUuid].recvData + recvData
                    print( deviceMap[reversedUuid].recvData )
                    deviceMap[reversedUuid].rssi += int(rssi * 0.7)
                    deviceMap[reversedUuid].count = deviceMap[reversedUuid].count - 1

                    if deviceMap[reversedUuid].count == 0:  #Received all Msg
                        if checkMsg(deviceMap, reversedUuid):
                            print("[received all beaconMsg] - Working time: ", time.time() - startTime)
                            printData(reversedUuid, deviceMap)
                            return [{"uuid": reversedUuid, 
                                "device_ip" : deviceMap[reversedUuid].ip_address, 
                                "device_angle" : deviceMap[reversedUuid].device_angle,
                                "device_acc": deviceMap[reversedUuid].device_acc,
                                "rssi" : deviceMap[reversedUuid].rssi
                                    }]
                deviceMap[reversedUuid].pre_data = recvData

            elif dataString[32:40] == '4d000215':  
                uuid = dataString[40:72]
                if uuid not in deviceMap:
                    startTime = time.time()
                    recvData = dataString[72:len(dataString)-2]
                    deviceMap[uuid] = BeaconMSG(recvData)
                    deviceMap[uuid].pre_data = recvData
                    deviceMap[uuid].rssi = int(rssi * 0.3)
                    deviceMap[uuid].count = deviceMap[uuid].count -1
                else: # Already registered device
                    deviceMap[uuid].reset()
                    deviceMap[uuid].rssi = int(rssi * 0.3)
                    deviceMap[uuid].count = deviceMap[uuid].count - 1
                    deviceMap[uuid].recvData = dataString[72:len(dataString)-2]
                    deviceMap[uuid].pre_data = deviceMap[uuid].recvData

def twosComplement_hex(hexval):
    bits = 16 # Number of bits in a hexadecimal number format
    val = int(hexval, bits)
    if val & (1 << (bits-1)):
        val -= 1 << bits
    return val            

def checkMsg(deviceMap, reversedUuid):
    print("checking Message...")
    print("msg: " , deviceMap[reversedUuid].recvData)
    if len(deviceMap[reversedUuid].recvData) != 44:
        return False
    
    byteArray = []
    for i in range(0, 22):
        byteArray.append(deviceMap[reversedUuid].recvData[i*2] + deviceMap[reversedUuid].recvData[i*2+1])

    if dataCheckerV4(byteArray):
        print("Valid Message!")
        saveInfov4(deviceMap, reversedUuid, byteArray)
        return True
    else:
        print("Invalid Message...")
        deviceMap[reversedUuid].reset()       
        return False

def saveInfov4(deviceMap, reversedUuid, msgByte):
    deviceMap[reversedUuid].ip_address
    for i in range(0, 4):
        deviceMap[reversedUuid].ip_address += str(int(msgByte[i], 16))
        if i != 3:
            deviceMap[reversedUuid].ip_address += '.'
    i = 5
    tmp = msgByte[i] + msgByte[i+1]
    deviceMap[reversedUuid].x_cor = twosComplement_hex(tmp)
    i = 8
    tmp = msgByte[i] + msgByte[i+1]
    deviceMap[reversedUuid].y_cor = twosComplement_hex(tmp)
    i = 11
    tmp = msgByte[i] + msgByte[i+1]
    deviceMap[reversedUuid].device_angle = twosComplement_hex(tmp)
    i = 14
    tmp = msgByte[i] + msgByte[i+1]
    deviceMap[reversedUuid].device_acc = twosComplement_hex(tmp)

def saveInfov6(deviceMap, reversedUuid, msgByte):
    deviceMap[reversedUuid].ip_address
    for i in range(0, 16):
        deviceMap[reversedUuid].ip_address += str(msgByte[i])
        if i != 15 and i % 2 == 1:
            deviceMap[reversedUuid].ip_address += ':'
    i = 17
    tmp = msgByte[i] + msgByte[i+1]
    deviceMap[reversedUuid].x_cor = int(tmp, 16)
    i = 20
    tmp = msgByte[i] + msgByte[i+1]
    deviceMap[reversedUuid].y_cor = int(tmp, 16)
    i = 23
    deviceMap[reversedUuid].seq_num = int(msgByte[i], 16)

    for i in range(25, 33):
        if i == 25:
            tmp = msgByte[i]
        else:
            tmp += msgByte[i]

def dataCheckerV4(msg):
    isRight = False
    if msg[4] == '2c' and msg[7] == '2c' and msg[10] == '2c' and msg[13] == '2c':
        isRight = True
    if isRight:
        for i in range(21, -1, -1):
            if msg[i] == '2f':
                return True
            elif msg[i] != '00':
                break
    return False

def dataCheckerV6(msg):
    isRight = False
    if msg[16] == '2c' and msg[19] == '2c' and msg[22] == '2c' and msg[24] == '2c':
        isRight = True
    if isRight:
        for i in range(34, -1, -1):
            if msg[i] == '2f':
                return True
            elif msg[i] != '00':
                break
    return False

def printData(reversedUuid, deviceMap):
    print()
    print("################## DATA ###################")
    print("# uuid:",        reversedUuid)
    print("# ip: ",         deviceMap[reversedUuid].ip_address)
    print("# x:",           deviceMap[reversedUuid].x_cor)
    print("# y:",           deviceMap[reversedUuid].y_cor)
    print("# angle:",       deviceMap[reversedUuid].device_angle)
    print("# acc:",        deviceMap[reversedUuid].device_acc)
    print("# rssi:",        deviceMap[reversedUuid].rssi)
    print("############################################")
    print()


        
