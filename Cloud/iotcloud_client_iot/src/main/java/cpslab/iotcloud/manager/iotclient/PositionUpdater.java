package cpslab.iotcloud.manager.iotclient;

import cpslab.iotcloud.network.core.CoAPServer;
import cpslab.iotcloud.network.core.CoAPServerHandler;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;
import cpslab.iotcloud.utils.FileHelper;

import java.io.IOException;


/**
 * Get IoT Client location from SALA Server
 */
public class PositionUpdater extends Thread {
    private final int DNS_OFFSET_X = 4;
    private final int DNS_OFFSET_Y = 5;
    private final int DNS_OFFSET_MAC = 0;

    String[] myInfo;
    int port;
    String location;
    public PositionUpdater(String[] myInfo, int port, String location) {
        this.myInfo = myInfo;
        this.port = port;
        this.location = location;
        this.start();
    }
    public synchronized void update(String[] coordinates) {
        this.myInfo[DNS_OFFSET_X] = coordinates[0];
        this.myInfo[DNS_OFFSET_Y] = coordinates[1];
    }
    public void run() {
        FileHelper fileHelper = new FileHelper();
        try {
            CoAPServer server = new CoAPServer(myInfo[DNS_OFFSET_MAC], port,
                    new CoAPServerHandler() {
                        @Override
                        public boolean onRequire(String command) throws IOException {
                            DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "received: " + command);
                            update(command.split(","));
                            fileHelper.saveFile(location, "coordinate.file",
                                    myInfo[DNS_OFFSET_X] + " " + myInfo[DNS_OFFSET_Y]);
                            return true;
                        }
                    }, location);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
