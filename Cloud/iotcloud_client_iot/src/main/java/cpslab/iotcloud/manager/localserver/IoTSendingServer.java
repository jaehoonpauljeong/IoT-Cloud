package cpslab.iotcloud.manager.localserver;

import com.google.gson.JsonObject;
import cpslab.iotcloud.network.core.JsonResponseHandler;
import cpslab.iotcloud.network.core.JsonResponseHttpServer;
import cpslab.iotcloud.structure.JsonObjectConverter;
import cpslab.iotcloud.structure.data.DeviceStructure;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;
import cpslab.iotcloud.utils.FileHelper;

import java.io.IOException;
import java.util.List;
import java.util.Map;

/**
 * Send IoT List as json on command
 */
public class IoTSendingServer {
    public IoTSendingServer(int port, String dnsnaListFileLocation) throws IOException {
        IoTListManager iotListManager = new IoTListManager(dnsnaListFileLocation);
        FileHelper reader = new FileHelper();

        JsonResponseHttpServer server = new JsonResponseHttpServer(port, new JsonResponseHandler() {
            @Override
            public JsonObject onRequire(String path, Map<String, List<String>> headers) throws IOException {
                String[] pathArray = path.split("/");

                JsonObject dataJsonObject = new JsonObject();
                if (pathArray[pathArray.length-1].equals("IoTLists")) {
                    JsonObjectConverter<DeviceStructure> conv4 = new JsonObjectConverter<>(DeviceStructure.class);
                    DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "searching IoTData Lists..." + pathArray[1]);

                    IoTDataLists IoTDataList = iotListManager.search(pathArray[1]);

                    StringBuilder allContent = new StringBuilder();
                    allContent.append("{result:[");

                    boolean isFirst = true;
                    for (Map.Entry<String, DeviceStructure> i : IoTDataList.iotList.entrySet()) {
                        if (!isFirst) allContent.append(",\n");
                        isFirst = false;
                        allContent.append(conv4.convertToJsonString(i.getValue()));
                    }
                    allContent.append("]}");

                    DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, allContent.toString());
                    dataJsonObject = conv4.convertToJsonObject(allContent.toString());

                    return dataJsonObject;
                }
                return null;
            }
        });
    }
}
