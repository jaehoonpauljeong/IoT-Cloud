package cpslab.iotcloud.control;

import com.google.gson.Gson;
import cpslab.iotcloud.structure.JsonObjectConverter;
import cpslab.iotcloud.structure.data.CommandStructure;
import cpslab.iotcloud.structure.data.StatusStructure;
import cpslab.iotcloud.utils.FileHelper;

import java.io.IOException;

/**
 * Basic IoT Control class
 * @author IoT Controller & Relay Team /
 */
public class ControllerBasis {
    private final String type;
    private final String location;
    public ControllerBasis(String type, String location) {
        this.type = type;
        this.location = location;
    }
    public void executeControl(CommandStructure command) throws IOException {
        JsonObjectConverter<StatusStructure> conv = new JsonObjectConverter<>(StatusStructure.class);
        StatusStructure myStatus = new Gson().fromJson(new FileHelper().readFileinRasp(location, "myStatus.json"), StatusStructure.class);
        if(type.equals("LED")) { myStatus =LedControllerBasis.LedControl(command, myStatus); }

        new FileHelper().saveFile(location, "myStatus.json", new Gson().toJson(myStatus));
    }
    /*
    public static void main(String[] args) throws IOException {
        String me = "/DeviceStructure/myIoT.json";
        JsonResponseHttpServer myServer = new JsonResponseHttpServer(8090,
                new JsonResponseHandler() {
                    @Override
                    public JsonObject onRequire(String ms, Map<String, List<String>> headers) {
                        JsonObjectConverter<DeviceStructure> conv = new JsonObjectConverter<>(DeviceStructure.class);
                        FileHelper fileReader = new FileHelper();
                        String command = ms;
                        String content = fileReader.readJsonFile("DeviceStructure",me);
                        JsonObject meObject = conv.convertToJsonObject(content);

                        if(command.equals("/LED_ON")) {
                            meObject.addProperty("isAlive", true);

                            LedControllerBasis led_control_center = new LedControllerBasis();
                            led_control_center.turnLed();
                        }
                        else if(command.equals("/LED_OFF")) {
                            meObject.addProperty("isAlive", false);
                            LedControllerBasis led_control_center = new LedControllerBasis();
                            led_control_center.turnOffLed();
                        }
                        // test start
                        if(command.equals("/list")){
                            System.out.println("hi");
                            ArrayList<DeviceStructure> tmp = new ArrayList<>();
                            DeviceStructure kkk = new DeviceStructure(); kkk.name="123";
                            DeviceStructure kkkk = new DeviceStructure(); kkkk.name="1233";
                            DeviceStructure kkkkk = new DeviceStructure(); kkkkk.name="12443";
                            tmp.add(kkk);
                            tmp.add(kkkk);
                            tmp.add(kkkkk);

                            Gson gson = new Gson();
                            String ret = gson.toJson(tmp);
                            System.out.println(ret);

                            JsonObject rret = new JsonObject();
                            rret.add("ret", JsonObjectConverter.convertToJsonArray(ret));
                            System.out.println(rret);
                            return rret;
                         }
                        //test end
                        return meObject;
                    }
                });

    }

    */
}
