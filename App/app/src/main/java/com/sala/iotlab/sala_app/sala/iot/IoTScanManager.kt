package com.sala.iotlab.sala_app.sala.iot

import android.content.Context
import android.content.IntentFilter
import android.net.wifi.WifiManager
import android.os.Build
import androidx.annotation.RequiresApi
import com.sala.iotlab.sala_app.bluetooth.BLEManager
import com.sala.iotlab.sala_app.data.IoTData
import com.sala.iotlab.sala_app.sala.device.DevicePositionManager
import com.sala.iotlab.sala_app.utils.urlHelper
import org.jetbrains.anko.AnkoLogger
import org.jetbrains.anko.info

class IoTScanManager(
    val mContext: Context,
    val devicePos: DevicePositionManager,
    val ip: String = "0.0.0.0",
    val IoTDataLists: HashMap<String, IoTData>
) : AnkoLogger {
    val myIpv4: String = urlHelper.getmyIPv4()
    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    val mBLEManager: BLEManager = BLEManager(myIpv4, devicePos)
    val scanThread = ScanThread()
    var threadAlive = false

    init {
        val intentFilter = IntentFilter()
        intentFilter.addAction(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION)
        info("BLE 초기화 완료")
    }

    /**
     * BLE 시작
     */
    fun startScan() {
        threadAlive = true
        if (!scanThread.isAlive) scanThread.start()
    }

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    fun stopScan() {
        scanThread.interrupt()
        threadAlive = false
        mBLEManager.stopBLE()
    }


    inner class ScanThread : Thread() {
        override fun run() {
            mBLEManager.start()
        }
    }
}
