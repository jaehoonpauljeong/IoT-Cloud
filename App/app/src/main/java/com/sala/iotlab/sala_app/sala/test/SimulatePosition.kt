package com.sala.iotlab.sala_app.sala.test

import com.sala.iotlab.sala_app.R
import com.sala.iotlab.sala_app.sala.device.DevicePositionManager
import java.util.*

class SimulatePosition(
    val mDevicePositionManager: DevicePositionManager,
    val fileID: Int,
    val refreshFreq: Long = 10L,
    val onDoneSimulationListener: () -> Unit = {}
) {
    var xPos: Int = 0
    var yPos: Int = 0
    val myFile =
        mDevicePositionManager.mContext.resources.openRawResource(fileID)
    val rawDataLoader = RawDataLoader(myFile)
    var nowPos: Int = 0
    var maxVal: Int = 0
    private var mTimer = Timer();

    companion object {
        val SIM_SALA_0 = R.raw.iot_sim_0
    }

    public fun run() {
        this.maxVal = this.rawDataLoader.scanData.scans.size
        this.nowPos = 0
        mTimer.schedule(SimulationTimer(this), refreshFreq, refreshFreq)
    }

    inner class SimulationTimer(val mParent: SimulatePosition) : TimerTask() {
        override fun run() {
            if (mParent.nowPos < mParent.maxVal) {
                mParent.xPos = mParent.rawDataLoader.scanData.scans.get(
                    mParent.nowPos
                ).x
                mParent.yPos = mParent.rawDataLoader.scanData.scans.get(
                    mParent.nowPos
                ).y
                mParent.mDevicePositionManager.refresh(DevicePositionManager.SIMULATE_POSITION)
                mParent.nowPos += 1
            } else {
                onDoneSimulationListener()
                this.cancel()
            }
        }
    }

}