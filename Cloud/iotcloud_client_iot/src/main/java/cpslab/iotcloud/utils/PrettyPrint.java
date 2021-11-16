package cpslab.iotcloud.utils;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;

public class PrettyPrint {
    public static void  print(JsonObject object) {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        String output = gson.toJson(object);
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, output);
    }
}
