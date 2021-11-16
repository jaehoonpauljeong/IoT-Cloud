package cpslab.iotcloud.manager.iotclient;

import cpslab.iotcloud.control.ControllerBasis;
import com.google.gson.Gson;
import cpslab.iotcloud.network.core.CoAPServer;
import cpslab.iotcloud.network.core.CoAPServerHandler;
import cpslab.iotcloud.structure.data.CommandStructure;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;

import java.io.IOException;

public class ClientController {
    private final int DNS_OFFSET_MAC = 0;
    private final int DNS_OFFSET_TYPE= 3;

    /**
     * Getting command from translating server and
     * @param myInfo
     * @param PORT
     * @param location
     * @throws IOException
     */
    public ClientController(String[] myInfo, int PORT, String location) throws IOException {
        /* Execute Coap Server */
        CoAPServer server = new CoAPServer(myInfo[DNS_OFFSET_MAC], PORT,
                new CoAPServerHandler() {
                    @Override
                    public boolean onRequire(String command) throws IOException {
                        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "[SALA] coordinate: " + command);
                        Gson gson = new Gson();
                        CommandStructure commandJson = gson.fromJson(command, CommandStructure.class);
                        ControllerBasis controllerBasis = new ControllerBasis(myInfo[DNS_OFFSET_TYPE], location);
                        controllerBasis.executeControl(commandJson);
                        return true;
                    }
                }, location);
    }
}
