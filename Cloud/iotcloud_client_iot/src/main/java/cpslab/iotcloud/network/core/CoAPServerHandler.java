package cpslab.iotcloud.network.core;

import java.io.IOException;

/**
 * CoapServer 구현에 있어
 * command를 Handler의 인자 전달을 위한 인터페이스
 */
public interface CoAPServerHandler {
    boolean onRequire(String path) throws IOException;
}
