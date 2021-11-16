package com.sala.iotlab.sala_app.structure;

public class DeviceStructure {
    /**
     * hello hyuntae
     */
    public String name; // IoT name: 거실 LED
    public String id; // IoT id: LED1
    public String type;
    public String mac; // IoT mac: aa:bb:cc:dd:...
    public String ipv4; // IoT ipv4, 0.0.0.0
    public String ipv6; // IoT ipv6, 0000:0000:0000:0000:0000:0000:0000:0000
    public int port;
    public String rawDns; // IoT DNS with x,y
    public String posDns; // IoT DNS with x,y coor data
    public int x; // IoT x coor (sala)
    public int y; // IoT y coor (sala)
    public String roomDns; // IoT affiliated room's dns
    public boolean isAlive = false; // IoT on/off

    public boolean isDnsExists = false; // for verification of data effectiveness
    public boolean isSalaExists = false; // for verification of data effectiveness
    public boolean isNameExists = false; // for verification of data effectiveness

    public String toString(){ // TODO 마저 채울 것
        return "name: " + name + ", id: " + id + ", mac: " + mac;
    }
}
