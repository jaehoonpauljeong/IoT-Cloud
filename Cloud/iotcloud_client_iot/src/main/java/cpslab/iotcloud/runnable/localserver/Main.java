package cpslab.iotcloud.runnable.localserver;

import com.google.gson.Gson;
import cpslab.iotcloud.manager.localserver.HTTP2CoAPTranslater;
import cpslab.iotcloud.manager.localserver.IoTSendingServer;
import cpslab.iotcloud.network.core.CompactHttpClient;
import cpslab.iotcloud.structure.JsonObjectConverter;
import cpslab.iotcloud.structure.data.RoomStructure;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;
import cpslab.iotcloud.utils.PrettyPrint;
import org.eclipse.californium.elements.exception.ConnectorException;

import java.io.IOException;

/**
 * Start part of IoT Server
 *  - HTTP2CoAP Translating server
 *  - IoT Server
 */
public class Main {
    private static final String CLOUD_IP = "192.168.1.29";
    private static final int CLOUD_PORT = 9000;

    private static final String myInfoPath = "/skku/distributiveResearch/85461";
    private static final String baseLocation = "/home/pi/DNSNA_Server_1/";
    private static final String dnsnaListFileLocation = baseLocation + "IoT_DNS_Server/dnsna_list.txt";

    public static void main(String[] args) throws IOException, ConnectorException {
        Gson gson = new Gson();
        JsonObjectConverter<RoomStructure> conv = new JsonObjectConverter<>(RoomStructure.class);
        RoomStructure myInfo = gson.fromJson(CompactHttpClient.httpGet(CompactHttpClient.getBaseHeader(), "http://" + CLOUD_IP + ":" + CLOUD_PORT + myInfoPath), RoomStructure.class);

        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "=========== MEC Server INFO ==========");
        PrettyPrint.print(conv.convertToJsonObject(myInfo));

        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, Integer.toString(myInfo.port));

        IoTSendingServer ioTSendingServer = new IoTSendingServer(myInfo.port, dnsnaListFileLocation);
        HTTP2CoAPTranslater localRelayCommandManager = new HTTP2CoAPTranslater();
    }
}
