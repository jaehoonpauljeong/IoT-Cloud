package cpslab.iotcloud.runnable.iotclient;

import cpslab.iotcloud.manager.iotclient.ClientController;
import cpslab.iotcloud.manager.iotclient.PositionUpdater;
import cpslab.iotcloud.utils.*;

import java.io.IOException;

public class Main{
    /**
     * Main of starting IoT Client
     * @param args 실행 시 인자
     */
    private static final String LOCATION = "/home/pi/DNSNA_Client_1";
    private static final String MY_IP = NetworkHelper.getIPv6("wlan0");

    private static final int COAP_CONTROL_PORT = 5000;
    private static final int COAP_UPDATE_PORT = 6000;

    public static void main(String[] args) throws IOException {
        FileHelper fileHelper = new FileHelper();
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "============= myClient_IOT_INFO ===============");
        String myDNS =  fileHelper.readFileinRasp(LOCATION, "dns_name.txt");
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG,  myDNS);
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, MY_IP);
        String[] myInfo = myDNS.split("\\.");
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "===============================================");
        /*
        B827EB340164.UID.rapsPi.LED.x.y.COORD.400609.ROOM.semicond.BUILDING.skku.LOC.cpslab.skku.edu
                myInfo[0] = B8EB615431(mac)
                myInfo[1] = UID
                myInfo[2] = rapsPi(DEVICE_CATEGORY)
                myInfo[3] = LED(DEVICE_TYPE)
                myInfo[4] = x(COORD_X)
                myInfo[5] = y(COORD_Y)
                myInfo[6] = COORD
                myInfo[7] = 400609(room_num)
                myInfo[8] = ROOM
                myInfo[9] = semicond(building)
                myInfo[10]= BUILDING
                myInfo[11]= skku
                myinfo[12]= LOC
                myInfo[13]= cpslab
                myInfo[14]= skku
                myInfo[15]= edu
         */
        ClientController controller = new ClientController(myInfo, COAP_CONTROL_PORT, LOCATION);
        PositionUpdater positionUpdater = new PositionUpdater(myInfo, COAP_UPDATE_PORT, LOCATION);
    }
}