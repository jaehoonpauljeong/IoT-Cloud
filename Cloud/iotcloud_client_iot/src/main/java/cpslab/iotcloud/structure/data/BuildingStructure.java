package cpslab.iotcloud.structure.data;

import java.util.HashMap;

public class BuildingStructure {
    public String name; // name (Semiconductor)
    public String k_name; // kor name (반도체관)
    public String id; // id (semiconductor)
    public String fullDns; // section ~ building dns (skku.semiconductor)
    public int floors;
    public HashMap<Integer, String> sections; // 증 - 단면도 맵
    /*
    public HashMap<Integer, HashMap<String, String>> rooms; // 층마다, 방에 대한 <id, 이름> 맵의 리스트
    private boolean equals(BuildingStructure another){
        return this.name.equals(another.name) && this.id.equals(another.id) &&
                this.fullDns.equals(another.fullDns) && this.sections.equals(another.sections) &&
                this.rooms.equals(another.rooms);
    }

     */

    public String toString(){
        return name + id + fullDns + sections;
    }

}
