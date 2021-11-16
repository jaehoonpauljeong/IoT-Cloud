package cpslab.iotcloud.manager.iotclient;

import cpslab.iotcloud.structure.JsonObjectConverter;
import cpslab.iotcloud.structure.data.DeviceStructure;
import cpslab.iotcloud.structure.data.StatusStructure;

import java.io.IOException;
import java.util.HashMap;

public class ClientCoap {
    public static void addStatusInfo() throws IOException {
        JsonObjectConverter<StatusStructure> conv = new JsonObjectConverter<>(StatusStructure.class);
        StatusStructure tmp = new StatusStructure();
        tmp.deviceType = "LED";
        tmp.mac = "B827EB615431";
        tmp.rawDns = "LED.B827EB615431.x.y.400609.semiconductor.skku.edu";
        tmp.roomDns = "400609.semiconductor.skku.edu";
        tmp.status = new HashMap<String, String>() {{
            put("led", "off");
        }};
        conv.convertToJsonFile("IoTClients/", "myStatus.json", tmp);
    }
    public static void main(String[] args) throws IOException {
        addStatusInfo();
    }
}