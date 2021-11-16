package cpslab.iotcloud.utils;

import java.net.*;
import java.util.Arrays;
import java.util.Enumeration;

public class NetworkHelper {
    /**
     * url change util
     * @param url 400609.semiconductor.skku
     * @return skku.semiconductor.400609
     */
    public static String reverseURL(String url) {
        String[] urlArray =url.split("\\.");
        StringBuilder reversed = new StringBuilder();
        for(int i = urlArray.length-1; i >=0; i--) {
            reversed.append(urlArray[i]);
            if(i!=0) reversed.append(".");
        }
        return reversed.toString();
    }

    /**
     * retrun my ipv4 address
     * @param mode e.g "eth0" or "wlan0"
     *             ** when eth0, it seems to not work **
     * @return String ipv4
     */
    public static String getIPv4(String mode) throws UnknownHostException {
        try {
            NetworkInterface iface = NetworkInterface.getByName(mode);

            if (!(iface.isLoopback() || !iface.isUp() || iface.isVirtual() || iface.isPointToPoint())) {
                Enumeration<InetAddress> addresses = iface.getInetAddresses();
                while(addresses.hasMoreElements()) {
                    InetAddress addr = addresses.nextElement();
                    DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, addr.getHostName());
                    final String ip = addr.getHostAddress();
                    if(Inet4Address.class == addr.getClass()) return ip;
                }
            }
        } catch (SocketException socketException) {
            socketException.printStackTrace();
        }
        return null;

    }

    /**
     * return my IPv6 address
     * @param mode e.g "eth0" or "wlan0
     *             ** when eth0, it seems not work.
     * @return String ipv6
     */
    public static String getIPv6(String mode) {
        try {
            NetworkInterface iface = NetworkInterface.getByName(mode);
            if (!(iface.isLoopback() || !iface.isUp() || iface.isVirtual() || iface.isPointToPoint())) {
                Enumeration<InetAddress> addresses = iface.getInetAddresses();
                while(addresses.hasMoreElements()) {
                    Inet6Address addr = (Inet6Address) addresses.nextElement();
                    final String ip = addr.getHostAddress().split("%")[0];
                    if(Inet6Address.class == addr.getClass()) DebugManager.debugPrintln(CompactDebug.DEBUG_LEVEL_DEBUG, ip);
                    if(!ip.substring(0,4).equals("fe80")) {
                        return ip;
                    }
                }
            }
        } catch (SocketException socketException) {
            socketException.printStackTrace();
        }
        return null;
    }
    public static String getMAC() {
        String result = "";
        try {
            NetworkInterface network = NetworkInterface.getByInetAddress(InetAddress.getLocalHost());
            byte[] mac = network.getHardwareAddress();

            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < mac.length; i++) {
                sb.append(String.format("%02X", mac[i]));
            }
            result = sb.toString();
        } catch (UnknownHostException | SocketException e) {
            e.printStackTrace();
        }

        return result;
    }
    public static String dnsMac2MAC(String Mac) {
        StringBuffer result = new StringBuffer(Mac);
        for(int i = 2; i<15; i+=3) {
            result.insert(i, ":");
        }
        return result.toString();
    }
}
