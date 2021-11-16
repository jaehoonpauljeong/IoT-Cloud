package cpslab.iotcloud.network.core;

import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.SocketException;

import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;
import cpslab.iotcloud.utils.FileHelper;
import org.eclipse.californium.core.CoapResource;
import org.eclipse.californium.core.CoapServer;
import org.eclipse.californium.core.coap.CoAP;
import org.eclipse.californium.core.network.CoapEndpoint;
import org.eclipse.californium.core.network.config.NetworkConfig;
import org.eclipse.californium.core.server.resources.CoapExchange;
import org.eclipse.californium.elements.util.NetworkInterfacesUtil;

public class CoAPServer extends CoapServer{
    private int COAP_PORT;
    private CoAPServerHandler handler;
    private final String location;

    public CoAPServer(String ResourceName, int COAP_PORT, CoAPServerHandler myHandler, String location) throws SocketException, IOException {
        add(new CoAPServer.CoAPServerResource(ResourceName, myHandler));
        this.COAP_PORT = COAP_PORT;
        this.handler = myHandler;
        this.location = location;
        addEndpoint();
        start();
        DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "CoAPServer PORT: " + COAP_PORT);
    }

    public void addEndpoint() {
        NetworkConfig config =NetworkConfig.getStandard();
        for(InetAddress addr : NetworkInterfacesUtil.getNetworkInterfaces()) {
            InetSocketAddress bindToaddress =new InetSocketAddress(addr, COAP_PORT);
            CoapEndpoint.Builder builder = new CoapEndpoint.Builder();
            builder.setInetSocketAddress(bindToaddress);
            builder.setNetworkConfig(config);
            addEndpoint(builder.build());
        }
    }
    class CoAPServerResource extends CoapResource {
        private CoAPServerHandler handler;
        public CoAPServerResource(String ResourceName, CoAPServerHandler handler) {
            super(ResourceName);
            this.handler = handler;
        }
        /* Send myStatus to Local Server */
        public void handleGET(CoapExchange exchange) {
            DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG,"GET: Sending my status...");
            try {
                exchange.respond(
                    new FileHelper().readFileinRasp(location, "myStatus.json")
            );
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        /* Received command */
        public void handlePOST(CoapExchange exchange) {
            DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG,"==============POST REQUEST================");
            exchange.accept();
            String received = exchange.getRequestText();
            try {
                boolean isDone = handler.onRequire(received);
            } catch (IOException e) {
                e.printStackTrace();
            }

            DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG,"sending " + CoAP.ResponseCode.CREATED);
            String status = null;
            try {
                status = new FileHelper().readFileinRasp(location, "myStatus.json");
            } catch (IOException e) {
                e.printStackTrace();
            }
            DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG,"sending changed status: " + status);
            exchange.respond(
                    CoAP.ResponseCode.CREATED,
                    status
            );
            DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "==========================================");
        }
    }
}
