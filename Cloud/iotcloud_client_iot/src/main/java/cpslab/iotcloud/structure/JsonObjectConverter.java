package cpslab.iotcloud.structure;

import com.google.gson.*;

import java.io.*;

public class JsonObjectConverter<I> {
    private final Class<I> classParameter;
    public static final String RESULT_NAME = "result";

    public JsonObjectConverter(Class<I> classParameter) {
        this.classParameter = classParameter;
    }


    public String convertToJsonString(I target) {
        Gson gson = new Gson();
        return gson.toJson(target);
    }
    public static JsonObject convertToJsonObject(String s) {
        Gson gson = new Gson();
        return JsonParser.parseString(s).getAsJsonObject();
    }
    public JsonObject convertToJsonObject(I target){
        Gson gson = new Gson();
        return gson.toJsonTree(target).getAsJsonObject();
    }

    public static String convertGeneralToJsonString(Object target){
        return new Gson().toJson(target);
    }
    public static JsonArray convertToJsonArray(String s){
        return JsonParser.parseString(s).getAsJsonArray();
    }
    public static JsonObject getResultObjectWithArrayGeneral(Object target){
        JsonObject ret = new JsonObject();
        ret.add(RESULT_NAME, convertToJsonArray(convertGeneralToJsonString(target)));
        return ret;
    }
    public static JsonObject getResultObjectWithJsonArrayString(String target){
        JsonObject ret = new JsonObject();
        ret.add(RESULT_NAME, convertToJsonArray(target));
        return ret;
    }
    public static JsonObject getResultObjectWithJsonArray(JsonArray target){
        JsonObject ret = new JsonObject();
        ret.add(RESULT_NAME, target);
        return ret;
    }

    /**
     *파일 저장하는 함수
     * @param folderName 폴더 이름 입력
     * @param fileName 파일 이름 입력
     * @param target JsonObject 입력
     * @author 김민제
     */
    public void convertToJsonFile(String folderName, String fileName, I target) throws IOException {
        ClassLoader loader = getClass().getClassLoader();
        if(folderName.charAt(0) == '/') folderName = folderName.substring(1);
        String jsonpath = loader.getResource(folderName).getPath();
        System.out.println(jsonpath);
        File folder = new File(jsonpath);
        File yourFile = new File(fileName);
        folder.mkdir();
        if(!yourFile.exists()) {
            yourFile.createNewFile();
        }
        BufferedWriter br = new BufferedWriter(new FileWriter(jsonpath+ fileName));
        br.write(convertToJsonString(target));
        br.flush();
        br.close();
    }

    public JsonElement  convertToJsonElement(I target) {
        Gson gson = new Gson();
        return JsonParser.parseString(convertToJsonString(target));
    }


    public I convertToObject(String target) {
        Gson gson = new Gson();
        return gson.fromJson(target, classParameter);
    }

    public I convertToObject(JsonElement target) {
        Gson gson = new Gson();
        return gson.fromJson(target, classParameter);
    }

    public I convertToObject(JsonObject target) {
        Gson gson = new Gson();
        return gson.fromJson(target.toString(), classParameter);
    }
}

