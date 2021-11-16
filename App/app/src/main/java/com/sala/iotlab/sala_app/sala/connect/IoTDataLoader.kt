package com.sala.iotlab.sala_app.sala.connect

import android.content.Context
import android.net.wifi.WifiManager
import android.os.Handler
import android.os.Message
import android.provider.Telephony
import android.util.Log
import android.util.Log.d
import androidx.appcompat.app.AppCompatActivity
import com.google.gson.Gson
import com.sala.iotlab.sala_app.data.IoTData
import com.sala.iotlab.sala_app.data.IoTDataManager
import com.sala.iotlab.sala_app.sala.iot.control.LightControl
import com.sala.iotlab.sala_app.structure.AddrStructure
import com.sala.iotlab.sala_app.structure.DeviceStructure
import com.sala.iotlab.sala_app.structure.IoTListsStructure
import com.sala.iotlab.sala_app.structure.RoomStructure
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.jetbrains.anko.AnkoLogger
import org.jetbrains.anko.info
import java.io.IOException
import java.lang.Exception
import java.lang.Thread.sleep
import java.net.ConnectException
import java.net.InetSocketAddress
import java.net.Socket

class IoTDataLoader(
    val mContext: Context,
    val mDataLoadedListener: (iotDatum: ArrayList<IoTData>) -> Unit
) : AnkoLogger {

    /**
     * Return after parsing data
     */
    fun parse(raw: String): ArrayList<IoTData> {
        val gson = Gson()
        val eachInfo = gson.fromJson(raw, IoTListsStructure::class.java).result
        val ret = ArrayList<IoTData>()
        info { "IoT 데이터 줄 단위로 절삭: " + eachInfo.joinToString(separator = ", ") }

        for (line in eachInfo) {
            val dnsPart = gson.fromJson(line, DeviceStructure::class.java)
            Log.d("debug", line.toString())
            lateinit var iotData: IoTData
            if (dnsPart.posDns.length > 20) {
                iotData = IoTDataManager.generateIoTData(dnsPart.posDns, dnsPart.ipv6, dnsPart.port)
            } else continue
            ret.add(iotData)
        }
        info {
            "변환된 IoT 데이터들, " + ret.joinToString(
                transform = { it -> it.toString() },
                separator = ", "
            )
        }
        return ret
    }

    inner class NetworkResultHandler : Handler() {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                MSG_UPDATE_DNS_INFORM -> {
                    val dnsInform = msg.obj as ArrayList<IoTData>
                    info { "$dnsInform 전송함" }
                    mDataLoadedListener(dnsInform)
                }
            }
        }
    }

    val networkResultHandler = NetworkResultHandler()
    fun getData(PortInfo:AddrStructure, RoomInfo: RoomStructure) {
        lateinit var response: String
        val job = GlobalScope.launch(Dispatchers.Default) {
            for (i in 0..CONNECTION_RETRY_COUNT) {
                try {
                    // 맥 주소 가져오기
                    val url: String = "http://${RoomInfo.ip}:${RoomInfo.port}/${RoomInfo.IoTDns}/IoTLists"
                    Log.d("debug", url)
                    response = HttpConnection.getRequest(url)
                    if(response != "") {
                        val msg = networkResultHandler.obtainMessage()
                        msg.what = MSG_UPDATE_DNS_INFORM
                        msg.obj = parse(response)
                        networkResultHandler.sendMessage(msg)
                        break
                    }
                }catch(e: Exception) {
                    e.printStackTrace()
                }
                sleep(CONNECTION_RETRY_DELAY)
            }
        }
    }
    companion object {
        private const val MSG_UPDATE_DNS_INFORM = 0x1001
        private const val CONNECTION_RETRY_COUNT = 3
        private const val CONNECTION_RETRY_DELAY: Long = 5000
    }
}
