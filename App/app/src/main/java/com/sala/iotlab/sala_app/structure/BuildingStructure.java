package com.sala.iotlab.sala_app.structure;

import java.util.HashMap;

public class BuildingStructure {
    public String name; // name  (Semiconductor)
    public String k_name; // kor name(반도체관)
    public String id; // id (semiconductor)
    public String fullDns; // dns section ~ building  dns (skku.semiconductor)
    public int floors = 0;
    public HashMap<Integer, String> sections; // Map of floors
}
