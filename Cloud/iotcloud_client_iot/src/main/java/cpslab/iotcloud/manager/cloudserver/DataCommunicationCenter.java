package cpslab.iotcloud.manager.cloudserver;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import cpslab.iotcloud.manager.localserver.IoTListManager;
import cpslab.iotcloud.network.core.JsonResponseHandler;
import cpslab.iotcloud.network.core.JsonResponseHttpServer;
import cpslab.iotcloud.structure.JsonObjectConverter;
import cpslab.iotcloud.structure.data.*;
import cpslab.iotcloud.utils.*;

import java.io.FileNotFoundException;
import java.nio.file.Path;
import java.util.HashMap;
import java.io.IOException;
import java.util.List;
import java.util.Map;

/**
 * Sends datas of json in require
 * @returns json data object
 */
public class DataCommunicationCenter {
   public DataCommunicationCenter(int port) throws IOException {
        JsonResponseHttpServer server = new JsonResponseHttpServer(port, new JsonResponseHandler() {
            @Override
            public JsonObject onRequire(String path, Map<String, List<String>> headers) throws IOException {
                FileHelper reader = new FileHelper();
                String[] pathArray = path.split("/");
                JsonObject dataJsonObject = new JsonObject();

                String content = reader.readJsonFile(path, pathArray[pathArray.length - 1] + ".json");
                dataJsonObject = new Gson().fromJson(content, JsonObject.class); //String -> JsonObject

                return dataJsonObject;
            }
        });
    }

    /**
     * Making info of Section
     * @throws IOException
     */
    public static void addSectionInfo() throws IOException {
        JsonObjectConverter<SectionStructure> conv = new JsonObjectConverter<>(SectionStructure.class);
        FileHelper reader = new FileHelper();
        SectionStructure tmp = new SectionStructure();
        tmp.id = "skku";
        tmp.fullDns = tmp.id + ".edu";
        tmp.name = "성균관대";
        tmp.img = tmp.id + ".jpg";
        tmp.buildings = new HashMap<String, String>() {{
            put("01", "삼성학술정보관");
            put("03", "학생회관");
            put("04", "복지회관");
            put("05", "수성관");
            put("11", "체육관");
            put("13", "대강당");
            put("20", "공학실습동");
            put("21", "제1공학관");
            put("22", "제1공학관");
            put("23", "제1공학관");
            put("24", "공학실습동");
            put("25", "제2공학관");
            put("26", "제2공학관");
            put("27", "제2공학관");
            put("28", "공학실습동");
            put("30", "건축환경실습");
            put("40", "반도체관");
            put("31", "제1과학관");
            put("32", "제2과학관");
            put("33", "화학관");
            put("51", "기초학문관");
            put("53", "약학관");
            put("61", "생명공학관");
            put("62", "생명공학관");
            put("63", "생명공학실습동");
            put("64", "생명공학실습동");
            put("71", "의학관");
            put("81", "제1종합연구동");
            put("83", "제2종합연구동");
            put("84", "제약기술관");
            put("85", "산학협력센터");
            put("91", "인관");
            put("92", "의관");
            put("93", "예관");
            put("95", "지관");
            put("96", "게스트하우스");
            put("97", "신관");
            put("102", "환경플랜트");
            put("103", "건축관리실");
            put("104", "파워플랜트");
        }};
        tmp.buildings_id = new HashMap<String, String>(){{
            put("01", "samsungLibrary");
            put("03", "studentUnion");
            put("04", "welfareUnion");
            put("05", "susungCenter");
            put("11", "gymCenter");
            put("13", "auditorium");
            put("20", "engineeringLab");
            put("21", "engineering1");
            put("22", "engineering1");
            put("23", "engineering1");
            put("24", "engineeringLab");
            put("25", "engineering2");
            put("26", "engineering2");
            put("27", "engineering2");
            put("28", "engineeringLab");
            put("30", "constructionLab");
            put("40", "semiconductor");
            put("31", "science1");
            put("32", "science2");
            put("33", "chemistry");
            put("51", "basicStudy");
            put("53", "pharmacy");
            put("61", "BioEngineering");
            put("62", "BioEngineering");
            put("63", "BioEngineeringLab");
            put("64", "BioEngineeringLab");
            put("71", "medical");
            put("81", "totalResearch1");
            put("83", "totalResearch2");
            put("84", "pharmaceuticalTech");
            put("85", "distributiveResearch");
            put("91", "inCenter");
            put("92", "euCenter");
            put("93", "yeCenter");
            put("95", "jiCenter");
            put("96", "guestHouse");
            put("97", "sinCenter");
            put("102", "enviromentPlant");
            put("103", "constructionManagement");
            put("104", "powerPlant");
        }};
        String path = NetworkHelper.reverseURL(tmp.fullDns);
        conv.convertToJsonFile(path.replace(".", "/") + "/", tmp.id + ".json", tmp);
    }
    /**
     * Making info of Building
     * @throws IOException
     */
    public static void addBuildingInfo() throws IOException {
        JsonObjectConverter<BuildingStructure> conv = new JsonObjectConverter<>(BuildingStructure.class);
        FileHelper reader = new FileHelper();
        BuildingStructure tmp = new BuildingStructure();
        tmp.name = "산학협력센터";
        tmp.id = "distributiveResearch";
        tmp.fullDns = "distributiveResearch.skku";
        tmp.floors = 7;
        tmp.sections = new HashMap<Integer, String>() {{
            put(1, "1.jpg");
            put(2, "2.jpg");
            put(3, "3.jpg");
            put(4, "4.jpg");
            put(5, "5.jpg");
            put(6, "6.jpg");
            put(7, "7.jpg");
        }};
        String path = NetworkHelper.reverseURL(tmp.fullDns);
        conv.convertToJsonFile(path.replace(".", "/") + "/", tmp.id + ".json", tmp);
    }
    /**
     * Making info of Room
     * @throws IOException
     */
    public static void addRoomInfo() throws IOException {
        JsonObjectConverter<RoomStructure> conv = new JsonObjectConverter<>(RoomStructure.class);
        RoomStructure tmp = new RoomStructure();
        tmp.id = "85416";
        tmp.name = "IoT Lab";
        tmp.fullDns = "85416.distributiveResearch.skku";
        tmp.ip = "192.168.0.11";
        tmp.port = 8000;
        tmp.proxyPort = 7890;
        tmp.img = new CustomImage("85461.png", 132.96);
        tmp.width = 490;
        tmp.height = 540;
        String path = NetworkHelper.reverseURL(tmp.fullDns);
        conv.convertToJsonFile(path.replace(".", "/") + "/", tmp.id + ".json", tmp);
    }

    /**
     * test
     * @param args
     * @throws IOException
     */
    public static void main(String[] args) throws IOException {
        addSectionInfo();
        addBuildingInfo();
        addRoomInfo();
    }
}
