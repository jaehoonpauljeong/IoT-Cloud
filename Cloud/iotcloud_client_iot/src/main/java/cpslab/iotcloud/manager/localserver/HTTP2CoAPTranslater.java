package cpslab.iotcloud.manager.localserver;


import cpslab.iotcloud.network.core.ProxyServer;
import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;

import java.io.IOException;

/**
 * open Translating proxy Server
 */
public class HTTP2CoAPTranslater {
    public HTTP2CoAPTranslater() throws IOException {
        ProxyServer proxyServer = new ProxyServer(false, true);
        while(true) {
            try {
                Thread.sleep(15000);
            } catch (InterruptedException e) {
                DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "interrupted exception");
                break;
            }
        }
    }
}
