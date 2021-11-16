package cpslab.iotcloud.structure.data;

import java.util.HashMap;

public class SectionStructure {
    public String id; // ex) skku
    public String fullDns; // same as id
    public String name; // ex) 성균관대
    public String img; // section image path
    public HashMap<String, String> buildings; // List of <id, name> maps for each building
    public HashMap<String, String> buildings_id; // List of <id, name> maps for each building
}
