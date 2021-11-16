package com.sala.iotlab.sala_app.sala

import android.content.Context
import android.net.wifi.WifiManager
import android.os.Build
import android.util.Log
import android.widget.ImageView
import androidx.annotation.RequiresApi
import com.sala.iotlab.sala_app.activity.IoTSelectionActivity
import com.sala.iotlab.sala_app.data.IoTData
import com.sala.iotlab.sala_app.sala.device.DevicePositionManager
import com.sala.iotlab.sala_app.sala.helper.ButtonMaker
import com.sala.iotlab.sala_app.sala.helper.SizeConverter
import com.sala.iotlab.sala_app.sala.iot.IoTScanManager
import com.sala.iotlab.sala_app.structure.RoomStructure
import org.jetbrains.anko.AnkoLogger

class SALAManager(
    val mContext: Context,
    val targetImageView: ImageView,
    val mDevicePositionManager: DevicePositionManager = DevicePositionManager(mContext),
    val ROOM_INFO: RoomStructure,
    val IoTDataLists: HashMap<String, IoTData>
) : AnkoLogger {
    val mSizeConverter = SizeConverter
    val mButtonMaker = ButtonMaker(this)
    var iotScanManager: IoTScanManager

    private var xDrawMax = 0
    private var yDrawMax = 0

    /*
    init {
        iotScanManager = IoTScanManager(
            mContext,
            mDevicePositionManager,
            ip = ROOM_INFO.ip,
            IoTDataLists = IoTDataLists
        )
    }

     */
    init {
        iotScanManager = IoTScanManager(
            mContext,
            mDevicePositionManager,
            IoTDataLists = IoTDataLists
        )
    }

    fun calcActualImageViewSize() {
        xDrawMax = targetImageView.measuredWidth
        yDrawMax = targetImageView.measuredHeight
    }

    fun requestForButton() {
        return
    }

    fun startAll() {
        positionRegisterAll()
        iotScanManager.startScan()
    }

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    fun stopAll() {
        positionUnregisterAll()
        iotScanManager.stopScan()
    }

    fun positionRegisterAll() {
        mDevicePositionManager.registerAll()
    }

    fun positionUnregisterAll() {
        mDevicePositionManager.unregisterAll()
    }

    fun positionRegisterSpecific(targetCode: Int) {
        mDevicePositionManager.registerSpecific(targetCode)
    }

    fun positionUnregisterSpecific(targetCode: Int) {
        mDevicePositionManager.unregisterSpecific(targetCode)
    }

    fun getDevicePositionManager(): DevicePositionManager {
        return mDevicePositionManager
    }


}