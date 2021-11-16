package com.sala.iotlab.sala_app.structure;

public class BuildingInfoStructure {
    public int num;
    public String buildingName;
    public BuildingInfoStructure(String num, String buildingName, String buildingID) {
        this.num = Integer.parseInt(num);
        this.buildingName = buildingName;
        this.buildingID = buildingID;
    }
    public String buildingID;

}
