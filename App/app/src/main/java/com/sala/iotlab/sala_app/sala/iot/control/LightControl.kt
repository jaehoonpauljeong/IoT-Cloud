package com.sala.iotlab.sala_app.sala.iot.control

import android.content.Context
import android.util.Log
import com.google.gson.Gson
import com.sala.iotlab.sala_app.data.IoTData
import com.sala.iotlab.sala_app.sala.connect.HttpConnection
import com.sala.iotlab.sala_app.structure.CommandStructure
import com.sala.iotlab.sala_app.structure.RoomStructure
import com.sala.iotlab.sala_app.structure.StatusStructure
import com.sala.iotlab.sala_app.utils.urlHelper
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import java.lang.Exception
import java.net.InetSocketAddress
import java.net.Socket

class LightControl(
    val iotData: IoTData,
    val ROOM_INFO: RoomStructure,
    val lightOnListener: () -> Unit,
    val lightOffListener: () -> Unit
) {
    val gson = Gson()
    /* IoT Coap address */
    private val url: String =
        "http://${ROOM_INFO.ip}:${ROOM_INFO.proxyPort}/proxy/coap://[${iotData.ipAddress.toUpperCase()}]:${iotData.port}/${iotData.macAddress.replace(
            ":",
            ""
        )}"

    private fun applyStatus(status: HashMap<String, String>) {
        for (key in status.keys) {
            if (status[key] == "on") lightOnListener()
            else lightOffListener()
        }
    }

    /**
     * send Command and return response
     */
    fun sendCommand(command: HashMap<String, String>): String {
        var commandBuild: CommandStructure = CommandStructure()
        commandBuild.id = iotData.macAddress
        commandBuild.deviceType = iotData.deviceType
        commandBuild.roomDns = ROOM_INFO.fullDns
        commandBuild.rawDns = iotData.dnsName
        commandBuild.originIp = urlHelper.getmyIPv4()
        commandBuild.commands = command

        return HttpConnection.putRequest(url, Gson().toJson(commandBuild))
    }

    fun lightOn() {
        lateinit var response: StatusStructure
        val commandMap: HashMap<String, String> = HashMap<String, String>()
        commandMap.put("led", "on")
        val currentTime = System.currentTimeMillis()
        val job = GlobalScope.launch(Dispatchers.Default) {
            response = gson.fromJson(sendCommand(commandMap), StatusStructure::class.java)
            Log.d("debug", "got response of iot client: " + gson.toJson(response))
        }
        runBlocking {
            job.join()
        }
        applyStatus(response.status)
        Log.d("workingTime", (System.currentTimeMillis() - currentTime).toString())
    }

    fun lightOff() {
        lateinit var response: StatusStructure
        val commandMap: HashMap<String, String> = HashMap<String, String>()
        commandMap.put("led", "off")
        val currentTime = System.currentTimeMillis()
        val job = GlobalScope.launch(Dispatchers.Default) {
            response = gson.fromJson(sendCommand(commandMap), StatusStructure::class.java)
            Log.d("debug", "got response of iot client: " + gson.toJson(response))
        }
        runBlocking {
            job.join()
        }
        applyStatus(response.status)
        Log.d("workingTime", (System.currentTimeMillis() - currentTime).toString())
    }

    fun getStatus(): Boolean {
        var isOn: Boolean = false
        lateinit var response: String
        val currentTime = System.currentTimeMillis()
        val job = GlobalScope.launch(Dispatchers.Default) {
            Log.d("debug", "required Status URL: $url")
            response = HttpConnection.getRequest(url)
            Log.d("debug", "getStatus $url: $response")
        }
        runBlocking {
            job.join()
        }
        Log.d("workingTime", (System.currentTimeMillis() - currentTime).toString())
        val STATUS: StatusStructure = Gson().fromJson(response, StatusStructure::class.java)
        for (key in STATUS.status.keys) {
            if (key == "led") {
                if (STATUS.status[key] == "on") {
                    lightOnListener()
                    isOn = true
                } else {
                    lightOffListener()
                }
            }
        }
        return isOn
    }
}