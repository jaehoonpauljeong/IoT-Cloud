package com.sala.iotlab.sala_app.sala.device

import android.util.Log
import java.io.BufferedReader
import java.io.InputStreamReader
import java.lang.Exception
import java.net.ServerSocket

class IPSManager(
    val mDevicePositionManager: DevicePositionManager
) {
    private var isFirst = true

    fun run() {
        IPSPositionUpdater(this).start()
    }

    inner class IPSPositionUpdater(val mParent: IPSManager) : Thread() {
        override fun run() {

            val thread = NetworkThread()
            thread.start()

            sleep(5000) //IPS 초반에 기다리기

            while (true) {
                val str = thread.str
                // Original coordinate
                val ori_x = mParent.mDevicePositionManager.xPos
                val ori_y = mParent.mDevicePositionManager.yPos

                // IPS 서버 콜 함수로부터 x,y좌표 수집
                // Collect x,y coordinate IPS server
                if(str[0] == "-1" && str[1] == "-1") {
                    continue;
                }
                val IPS_x = str[0].toFloat() * 100
                val IPS_y = str[1].toFloat() * 100

                val newXPos: Float
                val newYPos: Float

                // 기존 좌표와 IPS_좌표와의 비율 조정 (처음에는 순수 IPS_좌표로 설정)
                // Adjust the ratio of existing coordinates to IPS_coordinates (set as pure IPS_coordinates initially)
                Log.d("debug", "IPS_x = $IPS_x)")
                if (isFirst) {
                    newXPos = IPS_x
                    newYPos = IPS_y
                }
                else {
                    newXPos = IPS_x * 0.7F + ori_x * 0.3F
                    newYPos = IPS_y * 0.7F + ori_y * 0.3F
                }

                // 좌표 업데이트
                // update coordinate
                mParent.mDevicePositionManager.refresh(
                    DevicePositionManager.IPS_MANAGER,
                    newXPos,
                    newYPos
                )


                Log.i("Origin", "$ori_x,$ori_y")
                Log.i("IPS", "$IPS_x,$IPS_y")
                Log.i("NEW", "$newXPos,$newYPos")

                mParent.mDevicePositionManager.mSmartPDR.updatePos(newXPos, newYPos)

                isFirst = false
                // 2초마다 업데이트
                // Update by 2 sec
                sleep(2000)
            }
        }
    }
}