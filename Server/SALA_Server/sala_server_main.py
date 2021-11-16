#-*- coding:utf-8 -*-
import salabase as sl
import sala_algorithm as salaal
import socket
from select import *
import sys
import os
import threading
from time import time 


# function 설명: 
# input: (1) sala_info: sala연산에 필요한 데이터를 담고있는 딕셔너리
#        (2) data: *.sala 파일을 읽어들인 텍스트 데이터
# return: 없음
# output: data를 분석한 결과를 sala_info에 추가함
#         또한, 그 결과를 *.sala 파일에 반영함

PATH = '/home/pi/DNSNA_Server_1/SALA_Server/'
data_file_name = 'SALA_DATA' # 만들어 줄 파일 이름

def client_data_processing_new(sala_info, data):
        
        text = data.decode('UTF-8')

        lines = text.split('\n')
        ln = 0
        while ln < len(lines)-1:

                SSID = lines[ln+0]
                MAC = lines[ln+1]
                IP = lines[ln+2]
                try:
                        num_of_recode = int(lines[ln+3])
                except ValueError as e:
                        print("[Data Process] Wrong data")
                        return
                except Exception as e:
                        print(e)

                print("[Data Process]", MAC, 'recode:', num_of_recode, SSID)
                SSID = SSID.replace(" ", "_")

                # sala_information update
                if MAC not in sala_info:
                        sala_info[MAC] = dict()
                        sala_info[MAC]["device"] = sl.DeviceInfo(SSID, MAC, IP)
                        sala_info[MAC]["reports"] = list()

                sala_info[MAC]["updated"] = False
                target_reports = sala_info[MAC]["reports"]

                for nr in range(num_of_recode):
                        v = list( lines[ln+4+nr].split(' ') )
                        try:
                                target_reports.append( sl.Report(int(v[0]), float(v[1]), float(v[2]), int(v[3])) )
                        except IndexError as e:
                                continue
                        except Exception as e:
                                print(e)
                        finally:
                                pass
                        

                ln += num_of_recode + 4
                print("\n[%s] Updating Information")
                # file update
                target_file = open( SSID+".sala", "w", encoding="UTF-8" )
                target_file.write( SSID+"\n" )
                target_file.write( MAC+"\n" )
                target_file.write( IP+"\n" )
                for re in target_reports:
                        target_file.write(str(re.timestamp)+" "+str(re.position.x)+" "+str(re.position.y)+" "+str(re.rssi)+"\n")
                target_file.close()

def client_data_processing_exist(sala_info, data):

        lines = data.split('\n')
        SSID = lines[0]
        MAC = lines[1]
        IP = lines[2]

        num_of_recode = len(lines)-3

        # sala_information update
        if MAC not in sala_info:
                sala_info[MAC] = dict()
                sala_info[MAC]["device"] = sl.DeviceInfo(SSID, MAC, IP)
                sala_info[MAC]["reports"] = list()
                sala_info[MAC]["updated"] = False

        target_reports = sala_info[MAC]["reports"]

        for nr in range(num_of_recode):
                v = list( lines[3+nr].split(' ') )
                target_reports.append( sl.Report(int(v[0]), float(v[1]), float(v[2]), int(v[3])) )

def salaServerRun():
        os.system("sudo java -jar salaServer.jar")

if __name__ == "__main__":

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
                        client_data_processing_exist(sala_information, read_data)
                except:
                        pass

        print("[Init] Initialization DONE")

        # Server loop
        HOST = ''
        PORT_PHONE = 50007
        PORT_IOT = 50009
        BUFSIZE = 2**12
        ADDR_PHONE = (HOST,PORT_PHONE)
        ADDR_IOT = (HOST,PORT_IOT)
        TIMEOUT = 10

        server_socket_phone = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket_phone.bind(ADDR_PHONE)
        server_socket_phone.listen(0)

        server_socket_iot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket_iot.bind(ADDR_IOT)
        server_socket_iot.listen(0)

        connection_list = [ server_socket_phone, server_socket_iot ]
        address_map = dict()

        print("[Server] SALA Server start!")

        updated_time = int(time())
        UPDATE_PERIOD = 10
        cnt = 0

        serverThread = threading.Thread(target=salaServerRun, args=())
        serverThread.start()

        while connection_list:
                try:
                        print("[Server] Listening... ")
                        read_socket, write_socket, error_socket = select(connection_list, [], [], TIMEOUT)

                        for sock in read_socket:
                                # new connection
                                if sock == server_socket_phone:
                                        client_socket, addr = server_socket_phone.accept()
                                        connection_list.append(client_socket)
                                        print("[Server] Client connection accepted.")
                                        address_map[client_socket] = addr[0]

                                # iot connection
                                elif sock == server_socket_iot:

                                        client_socket, addr = server_socket_iot.accept()
                                        request_iot_name = client_socket.recv(BUFSIZE)
                                        request_iot_name = request_iot_name.decode('UTF-8')
                                        print("[Request] IoT", request_iot_name, "request accepted.")
                                        

                                        # translate ssid to mac_address
                                        request_iot_mac = ''
                                        for macAddr, inform in sala_information.items():
                                                if inform["device"].ssid == request_iot_name:
                                                        request_iot_mac = macAddr
                                                        break

                                        if request_iot_mac in sala_information:
                                                if "location" in sala_information[request_iot_mac]:
                                                        px, py = sala_information[request_iot_mac]["location"][0]
                                                        client_socket.send(bytes(str(px)+" "+str(py), 'UTF-8'))
                                                        print("[Reply] pos", str(px), ",", str(py))
                                                else:
                                                        client_socket.send(bytes("0 0", 'UTF-8'))
                                        else:
                                                client_socket.send(bytes("0 0", 'UTF-8'))
                                        client_socket.close()
                                        

                                # data from client
                                else:
                                        data = b''
                                        while True:
                                                inputdata = sock.recv(BUFSIZE) # TODO

                                                if inputdata:
                                                        cnt += 1
                                                        print("[Server] Data from "+address_map[sock]+": receive (now "
                                                                +str(len(inputdata))+", total "+str(len(data))+")")
                                                        print("Data count: {}".format(cnt))
                                                        data += inputdata
                                                else:
                                                        print("[CLOSE] connection close")
                                                        client_data_processing_new(sala_information, data)
                                                        connection_list.remove(sock)
                                                        address_map[sock] = ""
                                                        sock.close()
                                                        break

                        if cnt % 10 == 0:
                                updated_time = int(time())
                                print("[SALA] SALA-DATA Update start! ")
                                available = salaal.run_sala_algorithm(sala_information)
                                if available:
                                        with open(PATH+data_file_name,'w') as SD:
                                                for macAddr, inform in sala_information.items():
                                                        if 'location' in inform:
                                                            SD.write(inform['device'].ipaddr +'/'+ macAddr + '/' + str(inform['location'][0][0]) + '/' + str(inform['location'][0][1]) + '\n')
                                                            print("writing SALA-DATA")
                                                        if inform["updated"] == True:
                                                            print("[SALA]", inform["device"].ssid, inform["location"])
                                                SD.close()
                                        print("[SALA] done")


                except KeyboardInterrupt:
                        print("\n[KEYBOARD_INTERRUPT] exit()")
                        server_socket_phone.close()
                        print("[Server] close phone server socket")
                        server_socket_iot.close()
                        print("[Server] close iot server socket")
                        sys.exit()

                print("[Server] Timeout")

