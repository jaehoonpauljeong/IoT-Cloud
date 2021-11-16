package com.sala.iotlab.sala_app.structure;

import java.util.HashMap;

public class StatusStructure {
    public String deviceType; // device type(led, airconditioner, ...)
    public String mac; // IoT ID
    public String rawDns; // IoT DNS(x,y)
    public String roomDns; // room DNS
    // response <response id, value> ex) {{"led":"on"}, {"mode": "turbo"}, {"temperature": "14"}}
    public HashMap<String, String> status;

}
