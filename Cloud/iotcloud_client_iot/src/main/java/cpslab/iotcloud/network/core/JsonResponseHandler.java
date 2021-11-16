package cpslab.iotcloud.network.core;

import com.google.gson.JsonObject;

import java.io.IOException;
import java.util.List;
import java.util.Map;

/**
 * JsonResponseHttpServer 구현에 있어
 * path를 JsonObject 값으로 변환해주는 Handler의 인자 전달을 위한 인터페이스
 */
public interface JsonResponseHandler {
    public JsonObject onRequire(String path, Map<String, List<String>> headers) throws IOException;
}
