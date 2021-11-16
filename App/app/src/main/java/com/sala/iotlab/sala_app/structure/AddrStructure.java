package com.sala.iotlab.sala_app.structure;

public class AddrStructure {
    public String CLOUD_IP;
    public int MAIN_PORT;
    public int IMAGE_PORT;

    public AddrStructure(String CLOUD_IP, int MAIN_PORT, int IMAGE_PORT) {
        this.CLOUD_IP = CLOUD_IP;
        this.MAIN_PORT = MAIN_PORT;
        this.IMAGE_PORT = IMAGE_PORT;
    }
}
