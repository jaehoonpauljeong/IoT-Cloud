package cpslab.iotcloud.network.core;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;
import cpslab.iotcloud.utils.FileHelper;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.BasicResponseHandler;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.util.EntityUtils;


import java.io.IOException;
import java.util.HashMap;

/**
 * Simple HTTP Server
 *
 */
public class CompactHttpClient {

    /**
     * Setting basic header function
     * TODO Imply Client key register
     * @return defined basic HashMap<String, String> containing header
     */
    public static HashMap<String, String> getBaseHeader() {
        HashMap<String, String> ret = new HashMap<>();
        ret.put("Content-Type", "application/json");
        ret.put("Accept-Charset", "UTF-8");
        return ret;
    }
    public static String httpGet(HashMap<String, String> headers, String url){
        HttpClient client = HttpClientBuilder.create().build();
        try {
            HttpGet getRequest = new HttpGet(url);
            headers.forEach(getRequest::addHeader); // headers의 값을 getRequest의 header로 실제로 추가

            HttpResponse response = client.execute(getRequest);

            ResponseHandler<String> handler = new BasicResponseHandler();
            String body = handler.handleResponse(response);

            return body;
        }
        catch(Exception e){
            e.printStackTrace();
        }
        return null;
    }

    public static String httpPost(String url, String content) {
        HttpClient client = HttpClientBuilder.create().build();
        try {
            HttpPost postRequest = new HttpPost(url);
            postRequest.setHeader("Accept", "application/json");
            postRequest.setHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
            postRequest.setEntity(new StringEntity(content)); //json 메시지 입력

            HttpResponse response = client.execute(postRequest);

            DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "code: " + response.getStatusLine().getStatusCode());
            if (response.getStatusLine().getStatusCode() == 200) {
                HttpEntity entity = response.getEntity();
                String responseString = EntityUtils.toString(entity, "UTF-8");
                System.out.println("body: " + responseString);
                return responseString;
            }
            else if (response.getStatusLine().getStatusCode() == 201) {
                ResponseHandler<String> handler = new BasicResponseHandler();
                String body = handler.handleResponse(response);
                System.out.println("body: " + body);
                return body;
            } else {
                System.out.println("response is error : " + response.getStatusLine().getStatusCode());
            }
        } catch (Exception e) {
            System.err.println(e.toString());
        }
        return null;
    }


    /* test */
    public static void main(String[] args) throws IOException {
        //String ret = httpGet(getBaseHeader(), "http://127.0.0.1:7890/proxy/coap://localhost:9999/coap-target");
        //System.out.println(ret);
        FileHelper fileReader = new FileHelper();
        //String fileContent = fileReader.readJsonFile("/Commands/", "command1.json");
        httpPost("http://192.168.1.74:8001/B827EB340164", "D8D8.coorod.x.y.cpslab.skku.edu D8D8.coorod.88.99.cpslab.skku.edu");
    }
}
