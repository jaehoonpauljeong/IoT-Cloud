import salabase as sl
import sala_func 
import csala
import traceback

# IoT Device List
MAC_table = [

        "b8:27:eb:12:07:3b", # dev2
        "b8:27:eb:2f:bd:a6"  # dev1
        # "e8:4e:06:18:7e:70", # dev2
        # "e8:4e:06:18:8f:8b"  # dev1
]

wallInfo_list = sala_func.Wall()
wallInfo_list.add_wall(0,0,0,800)
wallInfo_list.add_wall(0,0,800,0)
wallInfo_list.add_wall(0,800,800,800)
wallInfo_list.add_wall(800,0,800,800)

def run_sala_algorithm(sala_information):
        available = True

        for macAddr, inform in list(sala_information.items()):

                #if macAddr not in MAC_table:
                #       continue

                if inform["updated"] == True:
                        continue
                
                try:
                        device_info = inform["device"]
                        reports = inform["reports"][-20:]
                        

                        if len(reports) < 10:
                                print( "device " + str(device_info) + " insufficient reports count " + str(len(reports)) + ", skipped!")
                                #del sala_information[macAddr]
                                available = False
                                continue
                        print( "device " + str(device_info) + " sufficient reports count " + str(len(reports)) + ", running!")

                       # print(csala.sala_algorithms(device_info, reports))
                        pos_star_x, pos_star_y, iot_location_x, iot_location_y = csala.sala_algorithms(device_info, reports)
                        print( "device " + str(device_info) + " done calc, " + str(pos_star_x) + " " + str(pos_star_y) + " / " + str(iot_location_x) + " " + str(iot_location_y))

                        pos_star = sl.Pos(pos_star_x, pos_star_y)
                        iot_location = [ [iot_location_x, iot_location_y] ]

                        sala_information[macAddr]["centroid"] = pos_star
                        sala_information[macAddr]["location"] = iot_location
                        inform["updated"] = True
                        print( "device " + str(device_info) + " done calc, " + str(iot_location))

                except KeyboardInterrupt as e:
                        raise KeyboardInterrupt
                except Exception as e:
                        print('Error:', e)
                        traceback.print_exc()
        # print("Done run_sala_algorithm, result is \n" + str(sala_information) + "\n\n")

        # duplicate position error
        addrList = list()
        for macAddr, inform in sala_information.items():
                if "location" in sala_information[macAddr]:
                        addrList.append(macAddr)

        dupcount = 1
        for n in range(0, len(addrList)):
                for m in range(n+1, len(addrList)):
                        nx, ny = sala_information[addrList[n]]["location"][0]
                        mx, my = sala_information[addrList[m]]["location"][0]
                        if nx == mx :
                                sala_information[addrList[n]]["location"][0][0] += dupcount
                                dupcount += 1
                        if ny == my :
                                sala_information[addrList[n]]["location"][0][1] += dupcount
                                dupcount += 1
        return available
