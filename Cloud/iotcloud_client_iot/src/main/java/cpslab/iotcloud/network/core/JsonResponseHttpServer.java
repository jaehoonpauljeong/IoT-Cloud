package cpslab.iotcloud.network.core;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.sun.net.httpserver.HttpServer;

import java.io.*;
import java.net.InetSocketAddress;

import java.util.*;
import java.util.concurrent.Executors;
import java.net.URI;

import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import cpslab.iotcloud.structure.JsonObjectConverter;
import cpslab.iotcloud.structure.data.DeviceStructure;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;
import cpslab.iotcloud.utils.FileHelper;
import cpslab.iotcloud.utils.PrettyPrint;


/**
 * 특정 조건에 따라 JSONObject를 텍스트화하여 반환하는 서버 코드 작성
 * path를 JSONObject로 변환하는 함수는 생성자에서 전달받음
 *
 * @author HTTP Server Team / 김민제
 */
public class JsonResponseHttpServer {

    private JsonResponseHandler handler;
    private int port;

    public JsonResponseHttpServer(int port, JsonResponseHandler myHandler) throws IOException {
        this.port = port;
        this.handler = myHandler;

        initServer();
    }
    /*
        Usage:
            JsonResponseHttpServer myServer = new JsonResponseHttpServer(
                new JsonResponseHandler(){
                    @Override
                    JsonObject onRequire(String path, Map<String, String> headers{
                        return JsonObject;
                    }});
     */

    /**
     * init Server + throw  error(서버 열기)
     */
    private void initServer() throws IOException {
        InetSocketAddress addr = new InetSocketAddress(port);
        HttpServer server = HttpServer.create(addr, 0);

        server.createContext("/", new handleRequest(handler));
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();
    }

    // for test which reads json file and send it to client and example of usage
    // show 192.168.0.1:8090/DeviceStructure/myIoT.json 이라 입력하면 myIoT.json content

    public static void main(String[] args) throws IOException {
        JsonResponseHttpServer myServer = new JsonResponseHttpServer(8090,
                new JsonResponseHandler() {
                    @Override
                    public JsonObject onRequire(String path, Map<String, List<String>> headers) throws NullPointerException, IOException {
                        System.out.println("path: " + path);
                        JsonObjectConverter<DeviceStructure> conv = new JsonObjectConverter<>(DeviceStructure.class);
                        FileHelper fileReader = new FileHelper();
                        String[] pathArray = path.split("/");

                        if(!(pathArray[pathArray.length-1].substring(pathArray[pathArray.length-1].length()-5)).equals(".json")) {
                            ClassLoader loader = getClass().getClassLoader();
                            String jsonpath = loader.getResource(path.substring(1)).getPath();
                            String[] listJsonFiles = new File(jsonpath).list();

                            StringBuilder allContent = new StringBuilder();
                            allContent.append("{result:[");
                            boolean isFirst = true;

                            for (String i : listJsonFiles) {
                                String content = fileReader.readJsonFile(path, i);
                                System.out.println("content:" + content);
                                if (!isFirst) allContent.append(",\n");
                                isFirst = false;
                                allContent.append(content);
                            }
                            allContent.append("]}");

                            return JsonObjectConverter.convertToJsonObject(allContent.toString());
                        }

                        else {
                            StringBuilder paths= new StringBuilder();
                            for(int i =0;i < pathArray.length-1; i++) {
                                paths.append(pathArray[i]);
                                if(i != pathArray.length-2) paths.append("/");
                            }
                            String content = fileReader.readJsonFile(paths.toString(), pathArray[pathArray.length-1]);
                            return conv.convertToJsonObject(content);
                        }
                    }
                });
    }

    class handleRequest implements HttpHandler {
        private JsonResponseHandler handler;

        handleRequest(JsonResponseHandler handler) {
            this.handler = handler;
        }

        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String requestMethod = exchange.getRequestMethod();
            /* Handle GET */
            if (requestMethod.equalsIgnoreCase("GET")) {
                Headers responseHeaders = exchange.getResponseHeaders();
                responseHeaders.set("Content-Type", "text/json");
                URI uri = exchange.getRequestURI();
                if (!uri.getPath().equals("/favicon.ico")) {
                    DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "*** Required Path: " + uri.getPath());
                }
                OutputStream responseBody = exchange.getResponseBody();
                Set<Map.Entry<String, List<String>>> headers = exchange.getRequestHeaders().entrySet();
                HashMap<String, List<String>> retHeaders = new HashMap<>();
                for (Map.Entry<String, List<String>> entry : headers) {
                    retHeaders.put(entry.getKey(), entry.getValue());
                }
                JsonObject target = handler.onRequire(uri.getPath(), retHeaders);
                exchange.sendResponseHeaders(200, 0);
                responseBody.write(target.toString().getBytes("UTF-8"));
                responseBody.close();
            }
            /* Handle POST */
            else if (requestMethod.equalsIgnoreCase("POST")) {
                DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "POST METHOD");
                BufferedReader reader = new BufferedReader(new InputStreamReader(exchange.getRequestBody()));

                URI uri = exchange.getRequestURI();

                OutputStream responseBody = exchange.getResponseBody();
                Gson gson = new Gson();
                JsonObject object = gson.fromJson(reader.readLine(), JsonObject.class);
                PrettyPrint.print(object);

                exchange.sendResponseHeaders(200, 0);
                responseBody.write("success".toString().getBytes("UTF-8"));
            }
        }
    }
}
