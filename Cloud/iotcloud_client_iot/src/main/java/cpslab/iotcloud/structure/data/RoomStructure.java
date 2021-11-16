package cpslab.iotcloud.structure.data;

/**
 * 방 하나의 구조 정보
 */
public class RoomStructure {
    public String id; // room's id (400609)
    public String name; // room's name(iot 스튜디오)
    public String fullDns; // section ~ room id (skku.semiconductor.400609)
    public String IoTDns;
    public CustomImage img;
    public int height;
    public int width;
    public String ip;
    public int port;
    public int proxyPort;
}
