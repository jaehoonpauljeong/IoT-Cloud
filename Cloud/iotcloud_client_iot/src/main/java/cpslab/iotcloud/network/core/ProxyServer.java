package cpslab.iotcloud.network.core;

import org.eclipse.californium.core.CoapServer;
import org.eclipse.californium.core.CoapResource;
import org.eclipse.californium.core.coap.CoAP;
import org.eclipse.californium.core.coap.MediaTypeRegistry;
import org.eclipse.californium.core.network.CoapEndpoint;
import org.eclipse.californium.core.network.config.NetworkConfig;
import org.eclipse.californium.core.network.config.NetworkConfigDefaultHandler;
import org.eclipse.californium.core.server.MessageDeliverer;
import org.eclipse.californium.core.server.resources.CoapExchange;
import org.eclipse.californium.elements.util.DaemonThreadFactory;
import org.eclipse.californium.elements.util.ExecutorsUtil;
import org.eclipse.californium.proxy2.*;
import org.eclipse.californium.proxy2.resources.*;

import java.io.File;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Revised from Californum CoAP translating proxy server
 * https://github.com/eclipse/californium
 */
public class ProxyServer {
    private static final File CONFIG_FILE = new File("Californium.properties");
    private static final String CONFIG_HEADER = "Californium CoAP Properties file for Example Proxy";
    private static final int DEFAULT_MAX_RESOURCE_SIZE = 8192;
    private static final int DEFAULT_BLOCK_SIZE = 1024;
    private static final NetworkConfigDefaultHandler DEFAULTS = new NetworkConfigDefaultHandler() {
        @Override
        public void applyDefaults(NetworkConfig config) {
            config.setInt(NetworkConfig.Keys.MAX_ACTIVE_PEERS, 20000);
            config.setInt(NetworkConfig.Keys.MAX_RESOURCE_BODY_SIZE, DEFAULT_MAX_RESOURCE_SIZE);
            config.setInt(NetworkConfig.Keys.MAX_MESSAGE_SIZE, DEFAULT_BLOCK_SIZE);
            config.setInt(NetworkConfig.Keys.PREFERRED_BLOCK_SIZE, DEFAULT_BLOCK_SIZE);
            config.setString(NetworkConfig.Keys.DEDUPLICATOR, NetworkConfig.Keys.DEDUPLICATOR_PEERS_MARK_AND_SWEEP);
            config.setInt(NetworkConfig.Keys.MAX_PEER_INACTIVITY_PERIOD, 60 * 60 * 24); // 24h
            config.setInt(NetworkConfig.Keys.TCP_CONNECTION_IDLE_TIMEOUT, 10); // 10s
            config.setInt(NetworkConfig.Keys.TCP_CONNECT_TIMEOUT, 15 * 1000); // 15s
            config.setInt(NetworkConfig.Keys.TLS_HANDSHAKE_TIMEOUT, 30 * 1000); // 30s
            config.setInt(NetworkConfig.Keys.UDP_CONNECTOR_RECEIVE_BUFFER, 8192);
            config.setInt(NetworkConfig.Keys.UDP_CONNECTOR_SEND_BUFFER, 8192);
            config.setInt(NetworkConfig.Keys.HEALTH_STATUS_INTERVAL, 60);
        }
    };
    private static final String COAP2COAP = "coap2coap";
    private static final String COAP2HTTP = "coap2http";

    private static String start;

    private CoapServer coapProxyServer;
    private boolean useEndpointsPool;
    private ClientEndpoints endpoints;
    private ProxyHttpServer httpProxyServer;
    private int coapPort = 9999;
    private int httpPort = 7890;
    private CacheResource cache;

    public ProxyServer(boolean accept, boolean cache) throws IOException {
        NetworkConfig config = NetworkConfig.createWithFile(CONFIG_FILE, CONFIG_HEADER, DEFAULTS);
        HttpClientFactory.setNetworkConfig(config);

        int threads = config.getInt(NetworkConfig.Keys.PROTOCOL_STAGE_THREAD_COUNT);
        ScheduledExecutorService mainExecutor = ExecutorsUtil.newScheduledThreadPool(threads,
                new DaemonThreadFactory("Proxy#"));
        ScheduledExecutorService secondaryExecutor = ExecutorsUtil.newDefaultSecondaryScheduler("ProxyTimer#");
        Coap2CoapTranslator translater = new Coap2CoapTranslator();
        NetworkConfig outgoingConfig = new NetworkConfig(config);
        if (useEndpointsPool) {
            outgoingConfig.setInt(NetworkConfig.Keys.NETWORK_STAGE_RECEIVER_THREAD_COUNT, 1);
            outgoingConfig.setInt(NetworkConfig.Keys.NETWORK_STAGE_SENDER_THREAD_COUNT, 1);
            endpoints = new EndpointPool(1000, 250, outgoingConfig, mainExecutor, secondaryExecutor);
        } else {
            outgoingConfig.setString(NetworkConfig.Keys.MID_TRACKER, "NULL");
            CoapEndpoint.Builder builder = new CoapEndpoint.Builder();
            builder.setNetworkConfig(outgoingConfig);
            endpoints = new ClientSingleEndpoint(builder.build());
        }
        ProxyCacheResource cacheResource = null;
        StatsResource statsResource = null;
        if (cache) {
            cacheResource = new ProxyCacheResource(true);
            statsResource = new StatsResource(cacheResource);
        }
        ProxyCoapResource coap2coap = new ProxyCoapClientResource(COAP2COAP, false, accept, translater, endpoints);
        ProxyCoapResource coap2http = new ProxyHttpClientResource(COAP2HTTP, false, accept, new Coap2HttpTranslator());
        if (cache) {
            coap2coap.setCache(cacheResource);
            coap2coap.setStatsResource(statsResource);
            coap2http.setCache(cacheResource);
            coap2http.setStatsResource(statsResource);
        }
        // Forwards requests Coap to Coap or Coap to Http server
        coapProxyServer = new CoapServer(config, coapPort);
        MessageDeliverer local = coapProxyServer.getMessageDeliverer();
        ForwardProxyMessageDeliverer proxyMessageDeliverer = new ForwardProxyMessageDeliverer(coapProxyServer.getRoot(),
                translater);
        proxyMessageDeliverer.addProxyCoapResources(coap2coap, coap2http);
        proxyMessageDeliverer.addExposedServiceAddresses(new InetSocketAddress(coapPort));
        coapProxyServer.setMessageDeliverer(proxyMessageDeliverer);
        coapProxyServer.setExecutors(mainExecutor, secondaryExecutor, false);
        coapProxyServer.add(coap2http);
        coapProxyServer.add(coap2coap);
        if (cache) {
            coapProxyServer.add(statsResource);
        }
        coapProxyServer.add(new SimpleCoapResource("target",
                "Hi! I am the local coap server on port " + coapPort + ". Request %d."));

        CoapResource targets = new CoapResource("targets");
        coapProxyServer.add(targets);

        // HTTP Proxy which forwards http request to coap server and forwards
        // translated coap response back to http client
        httpProxyServer = new ProxyHttpServer(config, httpPort);
        httpProxyServer.setHttpTranslator(new Http2CoapTranslator());
        httpProxyServer.setLocalCoapDeliverer(local);
        httpProxyServer.setProxyCoapDeliverer(proxyMessageDeliverer);
        httpProxyServer.start();

        System.out.println("** HTTP Local at: http://localhost:" + httpPort + "/local/");
        System.out.println("** HTTP Proxy at: http://localhost:" + httpPort + "/proxy/");

        coapProxyServer.start();
        System.out.println("** CoAP Proxy at: coap://localhost:" + coapPort + "/coap2http");
        System.out.println("** CoAP Proxy at: coap://localhost:" + coapPort + "/coap2coap");
        this.cache = cacheResource;
    }

    private static class SimpleCoapResource extends CoapResource {
        private final String value;
        private final AtomicInteger counter = new AtomicInteger();

        public SimpleCoapResource(String name, String value) {
            // set the resource hidden
            super(name);
            getAttributes().setTitle("Simple local coap resource.");
            this.value = value;
        }
        public void handleGET(CoapExchange exchange) {
            exchange.setMaxAge(0);
            exchange.respond(CoAP.ResponseCode.CONTENT, String.format(value, counter.incrementAndGet()),
                    MediaTypeRegistry.TEXT_PLAIN);
        }
    }
    public static void main(String[] args) throws  IOException {
        ProxyServer translateServer = new ProxyServer(false,true);
        while(true) {
            try {
                Thread.sleep(15000);
            } catch (InterruptedException e) {
                System.err.println("interrupted exception");
                break;
            }
        }
    }
}