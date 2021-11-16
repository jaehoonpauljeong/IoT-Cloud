package com.sala.iotlab.sala_app.utils;

import android.util.Log;

import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.util.Enumeration;

public class urlHelper {
    /**
     * url 변환 도구
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
     * 자신의 ip주소 반환(ipv4)
     * @return
     */
    public static String getmyIPv4() {
        try {
            Enumeration<NetworkInterface> interfaces = NetworkInterface.getNetworkInterfaces();
            while (interfaces.hasMoreElements()) {
                NetworkInterface iface = interfaces.nextElement();
                if (iface.isLoopback() || !iface.isUp() || iface.isVirtual() || iface.isPointToPoint())
                    continue;

                Enumeration<InetAddress> addresses = iface.getInetAddresses();
                while(addresses.hasMoreElements()) {
                    InetAddress addr = addresses.nextElement();

                    final String ip = addr.getHostAddress();
                    if(Inet4Address.class == addr.getClass()) return ip ;
                }
            }
        } catch (SocketException e) {
            throw new RuntimeException(e);
        }
        return null;
    }
}
