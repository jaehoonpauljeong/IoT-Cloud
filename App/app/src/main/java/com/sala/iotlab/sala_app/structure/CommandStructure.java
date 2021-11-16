package com.sala.iotlab.sala_app.structure;

import java.util.HashMap;

public class CommandStructure {

    public String originIp; // 명령 사용자 IP
    public String deviceType; // 기기 종류(led, airconditioner, ...)
    public String id; // 해당 기기 ID
    public String rawDns; // 해당 기기 DNS(x.y 처리됨)
    public String roomDns; // 방 DNS
    public HashMap<String, String> commands; // 제어 명령 <제어id, 제어값> ex) {{"led":"on"}, {"mode": "turbo"}, {"temperature": "14"}}
}
