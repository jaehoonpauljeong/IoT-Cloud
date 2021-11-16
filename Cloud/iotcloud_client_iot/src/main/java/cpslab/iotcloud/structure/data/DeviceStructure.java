package cpslab.iotcloud.structure.data;


public class DeviceStructure {
    public String name; // IoT 이름: 거실 LED
    public String id; // IoT id: LED1
    public String type;
    public String mac; // IoT mac: aa:bb:cc:dd:...
    public String ipv4; // IoT ipv4, 0.0.0.0
    public String ipv6; // IoT ipv6, 0000:0000:0000:0000:0000:0000:0000:0000
    public int port = 5000;
    public String rawDns; // IoT DNS with x,y
    public String posDns; // IoT DNS with x,y coor data
    public int x; // IoT x coor (sala)
    public int y; // IoT y coor (sala)
    public String roomDns; // IoT affiliated room's dns
    public boolean isAlive = false; // IoT on/off

    public boolean isDnsExists = false; // for verification of data effectiveness
    public boolean isSalaExists = false; // for verification of data effectiveness
    public boolean isNameExists = false; // for verification of data effectiveness

    public String toString() {

        return "[mac: " + mac + ", " +
                "ipv4: " + ipv4 + ", " +
                "rawDns: " + rawDns  + ", " +
                "posDns: " + posDns + ", " +
                "x: " + x + ", " +
                "y: " + y + ", " +
                "isDnsExist: " + isDnsExists + ", " +
                "isSalaExist: " + isSalaExists +
                "]";
    }
    public String setRawDns() {
        String[] tokens = posDns.split("\\.");
        tokens[4] = "x";
        tokens[5] = "y";
        StringBuilder res = new StringBuilder();
        for(int i =0; i< tokens.length; i++) {
            res.append(String.format("%s%s", tokens[i], (i<tokens.length-1) ? "." : ""));
        }
        return res.toString();
    }
    public void setCoord() {
        x = Integer.parseInt(posDns.split("\\.")[4]);
        y = Integer.parseInt(posDns.split("\\.")[5]);
    }
}
