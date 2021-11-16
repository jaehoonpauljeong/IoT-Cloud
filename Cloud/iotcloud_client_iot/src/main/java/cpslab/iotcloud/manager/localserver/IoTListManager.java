package cpslab.iotcloud.manager.localserver;

import cpslab.iotcloud.structure.data.DeviceStructure;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;
import org.apache.http.util.TextUtils;
import org.xbill.DNS.*;

import java.io.File;
import java.io.FileNotFoundException;
import java.net.Inet6Address;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.*;

/**
 * Manage IoT List.
 * Get IoT datas from bind9 zone by nslookup
 * Store IoT data at iotlist(Treemap)
 */
public class IoTListManager {
    private static String dnsnaListFileLocation;
    public IoTListManager(String dnsnaListFileLocation) throws FileNotFoundException {
        IoTListManager.dnsnaListFileLocation = dnsnaListFileLocation;
    }

    private static TreeMap<String, DeviceStructure> changeArrayList2TreeMap(ArrayList<DeviceStructure> target) {
        TreeMap<String, DeviceStructure> result = new TreeMap<>();

        for (DeviceStructure item : target) { // D8A21CB9 : Device Structure
            result.put(item.mac, item);
        }
        return result;
    }

    public IoTDataLists search(String dnsName) {
        IoTDataLists result = new IoTDataLists();
        ArrayList<DeviceStructure>  deviceStructures = new ArrayList<>();

        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, dnsnaListFileLocation);

        String data;//dnsna_list파일의 각 각 한줄을 담을 스트링
        String splitData[];//dnsna_list파일의 mac과 rawdns를 나눠서 저장할 스트링. 0:mac , 1: rawdns
        try{
            File dnsnaListFile = new File(dnsnaListFileLocation);
            Scanner dnsnaListReader = new Scanner(dnsnaListFile);
            while(dnsnaListReader.hasNextLine()){
                data = dnsnaListReader.nextLine();
                if (data.contains(dnsName)) {
                    splitData=data.split(" ");//0: mac 1: rawdns
                    //DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "data: " + data);
                    DeviceStructure tmp=new DeviceStructure();
                    tmp.mac=splitData[0];//mac
                    tmp.posDns = splitData[1];
                    tmp.rawDns= tmp.setRawDns();//rawdns
                    tmp.setCoord();
                    tmp.ipv6=readZone(splitData[1]);//zone 파일 읽는 함수.
                    tmp.isDnsExists=true;//dns가 존재하므로 true 로 변환.

                    deviceStructures.add(tmp);
                }
            }
            dnsnaListReader.close();
        } catch(FileNotFoundException e){
            e.printStackTrace();
        }

        result.update(changeArrayList2TreeMap(deviceStructures));

        return result;
    }

    private static String readZone(String posDns){
        String tempIp="0.0.0.0";//디폴트 ip 0.0.0.0 으로 설정. 해당 dns값에 맞는 ip주소가 zone에 없을 경우 0.0.0.0을 출력
        try {
            Lookup lookup = new Lookup(posDns, Type.AAAA);
            SimpleResolver resolver = new SimpleResolver();
            resolver.setAddress(Inet6Address.getByName(resolve("localhost", true)));
            lookup.setResolver(resolver);
            Record[] recs = lookup.run();
            if(recs != null) {
                for (Record rec : recs) {
                    AAAARecord aaaa = (AAAARecord)rec;
                    tempIp = aaaa.rdataToString();
                    DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, tempIp);

                }
            }
        }catch(UnknownHostException | TextParseException e){
            e.printStackTrace();
        }
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "[Nslookup] dns 서버에서 " + posDns + "을 검색 결과 : " + tempIp);
        return tempIp;
    }

    private static String resolve(String host, boolean enableIPv6) {
        String address = null;
        if(enableIPv6) {
            address = resolve(host, Type.AAAA);
            return address;

        }
        address = resolve(host, Type.A);
        if (!TextUtils.isEmpty(address)) {
            return address;
        }
        if (!TextUtils.isEmpty(address)) {
            return address;
        }
        address = resolve(host);
        if (!TextUtils.isEmpty(address)) {
            return address;
        }

        return null;
    }
    private static String resolve(String host, int addrType) {
        try {
            Lookup lookup = new Lookup(host, addrType);
            SimpleResolver resolver = new SimpleResolver("localhost");
            resolver.setTimeout(5);
            lookup.setResolver(resolver);
            Record[] result = lookup.run();
            if (result == null || result.length == 0) {
                return null;
            }

            List<Record> records = new ArrayList<>(Arrays.asList(result));
            Collections.shuffle(records);
            for (Record r : records) {
                switch (addrType) {
                    case Type.A:
                        return ((ARecord) r).getAddress().getHostAddress();
                    case Type.AAAA:
                        return ((AAAARecord) r).getAddress().getHostAddress();
                    default:
                        break;
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
    private static String resolve(String host) {
        try {
            InetAddress addr = InetAddress.getByName(host);
            return addr.getHostAddress();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
}
