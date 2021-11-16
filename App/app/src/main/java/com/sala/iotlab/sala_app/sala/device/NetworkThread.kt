package com.sala.iotlab.sala_app.sala.device

import android.util.Log
import java.io.BufferedReader
import java.io.InputStreamReader
import java.lang.Exception
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.ServerSocket


class NetworkThread : Thread() {
    var str: List<String> = listOf("-1", "-1")

    override fun run() {
        try {
            val socket = DatagramSocket(5050)
            var address = InetAddress.getByName("localhost")

            val buf = ByteArray(256)
            var packet = DatagramPacket(buf, buf.size)

            while (true) {
                socket.receive(packet)
                var data = String(packet.data, 0, packet.length)
                this.str = data.split(",")

                //Log.i("Data", str[0] + ',' + str[1])
            }

        } catch (e: Exception) {
            e.printStackTrace()
        }


    }
}