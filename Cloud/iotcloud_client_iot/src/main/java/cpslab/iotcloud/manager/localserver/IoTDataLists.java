package cpslab.iotcloud.manager.localserver;

import cpslab.iotcloud.structure.data.DeviceStructure;

import java.util.ArrayList;
import java.util.TreeMap;

/**
 * Store tree map of iotlist
 * <MAC, DeviceStructure class>
 */
public class IoTDataLists {
    public TreeMap<String, DeviceStructure> iotList;

    public synchronized void update(TreeMap<String, DeviceStructure> iotList) {
        this.iotList = iotList;
    }
}
