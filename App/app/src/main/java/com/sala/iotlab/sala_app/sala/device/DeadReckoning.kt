package com.sala.iotlab.sala_app.sala.device

import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import java.util.*
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

/**
 * DeadReckoning 담당하여 디바이스 위치 결정
 * @author 강성민
 * @deprecated pdr 패키지 내의 클래스들로 대체
 */
class DeadReckoning(
    private val parentPositionManager: DevicePositionManager,
    private var sensorManager: SensorManager,
    private val xMax: Int, private val yMax: Int,
    var xPos: Int, var yPos: Int
) {

    companion object {
        private const val NS2S = 1.0f / 1000000000.0f // nanosecond to second
        private const val ACCEL_NUM = 20

        const val ONCE_MAGNET = 0x01
        const val ONCE_GRAVITY = 0x02
        const val ONCE_ALL = 0x03
    }

    // Sensor values
    private var orientation = ArrayList<Float>(3)
    private var orientationInit: ArrayList<Float>? = null
    private var orientationCali = ArrayList<Float>()
    private var acceleration = ArrayList<Float>(3)
    private var gyroscope = ArrayList<Float>(3)
    private var gravity = ArrayList<Float>(3)
    private var magnet = ArrayList<Float>(3)
    private var angleChange = ArrayList<Float>(3)
    private var direction: Float = 0.0f
    private var timeStamp: Long = 0
    private var accelerationTime0: Long = 0

    // Orientation
    private var cCount: Int = 0

    // Step counting..
    private var stepCount = 0
    private val accMax = 6.5f
    private val accMin = 2.05f
    private val accOverMax = 4
    private val accLenMin = 4
    private var accOvered = 0

    // Min value
    private val xMin = 0
    private val yMin = 0

    private var mySensorEventListener = MySensorEventListener()


    /**
     * [accelerationTime1] 을 바탕으로 유효성 검증 후 수정
     */
    private fun validation(accelerationTime1: Long) {
        //return // TODO 수정

        val lacc = acceleration[0]

        // 가속도 범위 체크 및 횟수 계산
        if (lacc > accMax || lacc < accMin) {
            accOvered += 1
            if (accOvered >= accOverMax) {
                accOvered = 0
                acceleration.clear()
            }
        }
        if (acceleration.size < accLenMin) {
            return
        }

        val dt = (accelerationTime1 - accelerationTime0) * NS2S
        if (dt >= 0.7f) {
            stepCount++
            acceleration.clear()
            accelerationTime0 = accelerationTime1

            // 위치 계산
            val theta = orientationCali[0] + Math.PI / 1.0
            xPos += (60 * cos(theta)).toInt()
            yPos += (60 * sin(theta)).toInt()

            // boundary 검증
            if (xPos < xMin) xPos = xMin
            if (yPos < yMin) yPos = yMin
            if (xPos > xMax) xPos = xMax
            if (yPos > yMax) xPos = yMax
        }

        parentPositionManager.refresh(DevicePositionManager.DEAD_RECKONING)
    }


    /**
     * 방향 계산 및 보정
     */
    private fun calculateDirection() {
        // TODO 보정 식
        if (angleChange.isEmpty() || orientationCali.isEmpty()) return

        cCount++
        if (cCount >= 10) {
            angleChange[2] = -orientationCali[0]
            cCount = 0
        }
        if (angleChange.isNotEmpty()) direction = angleChange[2]
    }


    /**
     * [accelerationItems]를 바탕으로 가속도 갱신
     */
    private fun updateAcceleration(accelerationItems: ArrayList<Float>) {
        if (acceleration.size == ACCEL_NUM) {
            acceleration.removeAt(ACCEL_NUM - 1)
        }
        val sqrtValue =
            sqrt(accelerationItems.fold(0.0f) { acc, e -> acc + e * e })
        acceleration.add(0, sqrtValue)
    }

    /**
     * [magneticItems]를 바탕으로 자력계 갱신
     */
    private fun updateMagnetic(magneticItems: ArrayList<Float>) {
        magnet = ArrayList(magneticItems)
    }


    /**
     * [gyroscopeItems]와 [times]를 바탕으로 자이로스코프 갱신
     */
    private fun updateGyroscope(gyroscopeItems: ArrayList<Float>, times: Long) {
        if (timeStamp != 0L) {
            val dt = (times - timeStamp) * NS2S
            angleChange.forEachIndexed { i, _ ->
                angleChange[i] += dt * (gyroscopeItems[i] + gyroscope[i]) / 2.0f
            }
        }
        gyroscope = ArrayList(gyroscopeItems)
        timeStamp = times
    }


    /**
     * [gravityItems]를 바탕으로 중력계 갱신
     */
    private fun updateGravity(gravityItems: ArrayList<Float>) {
        gravity = ArrayList(gravityItems)
    }


    /**
     * [R]을 바탕으로 Orientation 갱신
     */
    private fun updateOrientation(R: ArrayList<Float>) {
        val rArray = R.toFloatArray()
        if (rArray.isEmpty()) return
        val orientationArray = orientation.toFloatArray()
        if (orientationArray.isEmpty()) return

        SensorManager.getOrientation(rArray, orientationArray)
        orientation = orientationArray.toCollection(ArrayList())

        if (orientationInit == null) {
            orientationInit = ArrayList(orientation)
        }
        orientationCali[0] = orientation[0] - orientationInit!![0]
        orientationCali[1] = orientationCali[2]
        orientationCali[2] = 0f
    }


    /**
     * Sensor Event 리스너
     */
    inner class MySensorEventListener : SensorEventListener {
        private var onceChecked: Int = 0

        init {
            onceChecked = 0
        }

        override fun onSensorChanged(event: SensorEvent) {
            when (event.sensor.type) {
                Sensor.TYPE_LINEAR_ACCELERATION -> {
                    updateAcceleration(event.values.toCollection(ArrayList()))
                    validation(event.timestamp)
                }
                Sensor.TYPE_MAGNETIC_FIELD -> {
                    onceChecked = onceChecked or ONCE_MAGNET
                    updateMagnetic(event.values.toCollection(ArrayList()))
                }
                Sensor.TYPE_GRAVITY -> {
                    onceChecked = onceChecked or ONCE_GRAVITY
                    updateGravity(event.values.toCollection(ArrayList()))
                }
                Sensor.TYPE_GYROSCOPE -> {
                    updateGyroscope(
                        event.values.toCollection(ArrayList()),
                        event.timestamp
                    )
                    calculateDirection()
                }
            }

            if (onceChecked == ONCE_ALL) {
                val rArray = FloatArray(9)
                val gravityArray = gravity.toFloatArray()
                val magnetArray = magnet.toFloatArray()

                SensorManager.getRotationMatrix(
                    rArray,
                    null, gravityArray, magnetArray
                )

                gravity = gravityArray.toCollection(ArrayList())
                magnet = magnetArray.toCollection(ArrayList())
                updateOrientation(rArray.toCollection(ArrayList()))
            }
        }

        override fun onAccuracyChanged(sensor: Sensor, accuracy: Int) {}

    } // listener end


    /**
     * 리스너 등록
     */
    fun registerListener() {
        val delay = SensorManager.SENSOR_DELAY_NORMAL
        val sensors = intArrayOf(
            Sensor.TYPE_LINEAR_ACCELERATION,
            Sensor.TYPE_ACCELEROMETER,
            Sensor.TYPE_GYROSCOPE,
            Sensor.TYPE_MAGNETIC_FIELD,
            Sensor.TYPE_GRAVITY
        )

        for (type in sensors) {
            sensorManager.registerListener(
                mySensorEventListener,
                sensorManager.getDefaultSensor(type), delay
            )
        }
    }


    /**
     * 리스너 해제
     */
    fun unregisterListener() {
        sensorManager.unregisterListener(mySensorEventListener)
    }
}