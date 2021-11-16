package cpslab.iotcloud.runnable.localserver;

import cpslab.iotcloud.utils.CompactDebug;
import cpslab.iotcloud.utils.DebugManager;
import org.eclipse.californium.core.CoapClient;
import org.eclipse.californium.core.coap.MediaTypeRegistry;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

/**
 * Start SALA Server
 * Send IoT coordinate to IoT by using coap protocol
 */

public class SALAServer {
    private static String salaDataLocation = "/home/pi/DNSNA_Server_1/SALA_Server/SALA_DATA";

    public static void main(String[] args) throws FileNotFoundException {
        CoapClient coapClient = new CoapClient();
        while(true) {
            try {
                Thread.sleep(30000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            File salaDataFile = new File(salaDataLocation);
            Scanner salaDataReader = new Scanner(salaDataFile);

            while(salaDataReader.hasNextLine()) {
                String data = salaDataReader.nextLine();
                String[] splitData = data.split("/");
                DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, "coap://[" + splitData[0] +"]:" + "6000/" + splitData[1].replace(":", "").toUpperCase());
                coapClient.setURI("coap://[" + splitData[0] +"]:" + "6000/" + splitData[1].replace(":", "").toUpperCase());
                try {
                    coapClient.post(splitData[2].split("\\.")[0] + "," + splitData[3].split("\\.")[0], MediaTypeRegistry.TEXT_PLAIN);
                } catch (Exception e) {
                    DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_ERR, "unable to connect IoT");
                }
            }

            salaDataReader.close();
        }
    }
}
