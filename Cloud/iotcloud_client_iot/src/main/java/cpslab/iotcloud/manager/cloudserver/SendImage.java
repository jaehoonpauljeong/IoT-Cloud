package cpslab.iotcloud.manager.cloudserver;

import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;
import cpslab.iotcloud.utils.FileHelper;

import java.io.*;
import java.net.InetSocketAddress;
import java.net.URI;
import java.nio.file.Files;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;

/**
 * Sending image map
 * @throws IOException
 */
public class SendImage {
    public SendImage(int PORT) throws IOException {
        InetSocketAddress addr = new InetSocketAddress(PORT);
        HttpServer server = HttpServer.create(addr, 0);
        server.createContext("/", new handleRequest());
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();
    }

    class handleRequest implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String requestMethod = exchange.getRequestMethod();
            /* Handle GET */
            if (requestMethod.equalsIgnoreCase("GET")) {
                FileHelper reader = new FileHelper();
                DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "*** Required IMAGE");
                Headers responseHeaders = exchange.getResponseHeaders();
                responseHeaders.set("Content-Type", "text/json");
                URI uri = exchange.getRequestURI();
                OutputStream responseBody = exchange.getResponseBody();
                Set<Map.Entry<String, List<String>>> headers = exchange.getRequestHeaders().entrySet();
                HashMap<String, List<String>> retHeaders = new HashMap<>();
                for (Map.Entry<String, List<String>> entry : headers) {
                    retHeaders.put(entry.getKey(), entry.getValue());
                }

                String[] pathArray = uri.getPath().split("/");
                StringBuilder paths = new StringBuilder();
                for (int i = 0; i < pathArray.length - 1; i++) {
                    paths.append(pathArray[i]);
                    if (i != pathArray.length - 2) paths.append("/");
                }
                File image = reader.readImageFile(paths.toString(), pathArray[pathArray.length - 1]);
                exchange.sendResponseHeaders(200, image.length());
                DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "sending IMAGE: " + image.toPath());
                Files.copy(image.toPath(), responseBody);
                responseBody.close();
            }
        }
    }
}
