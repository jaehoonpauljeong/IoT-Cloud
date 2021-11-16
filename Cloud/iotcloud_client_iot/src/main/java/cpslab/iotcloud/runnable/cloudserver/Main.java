package cpslab.iotcloud.runnable.cloudserver;

import cpslab.iotcloud.manager.cloudserver.*;
import cpslab.iotcloud.structure.data.AddrStructure;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;
import cpslab.iotcloud.utils.NetworkHelper;

import java.io.IOException;

public class Main {
    /**
     * Main of starting Cloud server
     * @param args 실행 시 인자
     */

    public static void main(String[] args) throws IOException {
        AddrStructure addr_info = new AddrStructure();

        addr_info.CLOUD_IP = NetworkHelper.getIPv4("wlan0");
        //addr_info.CLOUD_IP = "192.168.1.2"; // You can either set IP by passively
        addr_info.MAIN_PORT = 9000;
        addr_info.IMAGE_PORT = 9001;
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "Cloud Server IP: " + addr_info.CLOUD_IP);

        SendImage sendImage = new SendImage(addr_info.IMAGE_PORT);
        DataCommunicationCenter dataCommunicator = new DataCommunicationCenter(addr_info.MAIN_PORT);
    }
}
