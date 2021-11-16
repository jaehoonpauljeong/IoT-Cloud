package com.sala.iotlab.sala_app.sala.device

import android.content.Context
import android.hardware.SensorManager
import com.sala.iotlab.sala_app.sala.device.pdr.SmartPDR
import org.jetbrains.anko.AnkoLogger
import org.jetbrains.anko.info

/**
 * Final determination of device location based on various positioning classes
 * @author 강성민
 */
class DevicePositionManager(
    val mContext: Context,
    var xPos: Float = 0.0f, // Initial point
    var yPos: Float = 0.0f, // Initial point
    val onPositionChangedListener: (xPos: Float, yPos: Float) -> Unit = { fl: Float, fl1: Float -> }
) : AnkoLogger {

    companion object {
        const val DEAD_RECKONING: Int = 0x101
        const val SMART_PDR: Int = 0x102
        const val SIMULATE_POSITION: Int = 0xfff
        const val IPS_MANAGER: Int = 0x103

        const val PDR_LENGTH_COEFFICIENT: Float = 35.0f // 좌표계 변환 상수
    }

    val mSensorManager: SensorManager =
        mContext.getSystemService(Context.SENSOR_SERVICE) as SensorManager

    //private val mSimulatePosition = SimulatePosition(this, SimulatePosition.SIM_SALA_0);
    val mSmartPDR: SmartPDR =
        SmartPDR(
            mContext,
            mSensorManager,
            xPos,
            yPos,
            lengthCoefficient = PDR_LENGTH_COEFFICIENT,
            onStepDetectedListener = { newXPos: Float, newYPos: Float, _, _, _ ->
                refresh(SMART_PDR, newXPos, newYPos)
            },
            onIPSDetectedListener = { newXPos: Float, newYPos: Float ->
                refresh(SMART_PDR, newXPos, newYPos)
            }
        )
    val mIPSManager = IPSManager(this)

    /**
     * Turn on all location measurement functions managed by the manager
     */
    fun registerAll() {
        //mDeadReckoning.registerListener()
        mSmartPDR.registerListener()
        mIPSManager.run()
        info { "모든 위치측정 기능을 켬" }
    }

    /**
     * Turn off all location measurement functions managed by the manager
     */
    fun unregisterAll() {
        //mDeadReckoning.unregisterListener()
        mSmartPDR.unregisterListener()
        info { "모든 위치측정 기능을 끔" }
    }

    /**
     * turn on location management having [targetCode]
     */
    fun registerSpecific(targetCode: Int) {
        when (targetCode) {
            //DEAD_RECKONING -> mDeadReckoning.unregisterListener()
            //SIMULATE_POSITION -> mSimulatePosition.run()
            SMART_PDR -> mSmartPDR.registerListener()
            IPS_MANAGER -> mIPSManager.run()
        }
        info { "${targetCode}를 갖는 위치측정 기능을 켬" }
    }


    /**
     * turn off location management having [targetCode]
     */
    fun unregisterSpecific(targetCode: Int) {
        when (targetCode) {
            //DEAD_RECKONING -> mDeadReckoning.unregisterListener()
            SMART_PDR -> mSmartPDR.unregisterListener()
        }
        info { "${targetCode}를 갖는 위치측정 기능을 끔" }
    }

    /**
     * Called from subclass with [fromCode] to update the current value
     */
    fun refresh(fromCode: Int, newXPos: Float? = null, newYPos: Float? = null) {
        when (fromCode) {
            /*
            DEAD_RECKONING -> {
                this.xPos = mDeadReckoning.xPos
                this.yPos = mDeadReckoning.yPos
            }
             */

            SMART_PDR -> {
                this.xPos = newXPos!!
                this.yPos = newYPos!!
            }
            IPS_MANAGER -> {
                this.xPos = newXPos!!
                this.yPos = newYPos!!
            }
        }

        onPositionChangedListener(xPos, yPos)

        info { "${fromCode}로부터 현재 X 좌표 및 Y 좌표 갱신" }
    }
}