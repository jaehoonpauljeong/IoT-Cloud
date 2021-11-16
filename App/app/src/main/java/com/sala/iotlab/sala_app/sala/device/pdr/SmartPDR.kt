package com.sala.iotlab.sala_app.sala.device.pdr
//package com.sala.iotlab.sala_app.activity

import android.app.Activity
import android.content.Context
import androidx.appcompat.app.AppCompatActivity
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Bundle
import android.os.PersistableBundle
import android.util.Log
import android.widget.TextView
import com.sala.iotlab.sala_app.R
import com.sala.iotlab.sala_app.activity.IoTSelectionActivity
import com.sala.iotlab.sala_app.utils.GyroscopeSensorFilter
import kotlinx.android.synthetic.main.activity_iotselection.*
import org.jetbrains.anko.AnkoLogger
import org.jetbrains.anko.debug
import kotlin.math.*
import java.lang.Math.sqrt as mathSqrt

/**
 * Sensor processing recognizes the occurrence of a walk and attempts to convert.
 * @author 이동욱, 강성민
 * @property sensorManager
 */
class SmartPDR(
    mContext: Context,
    private val sensorManager: SensorManager,
    private var xPos: Float = 0.0f,
    private var yPos: Float = 0.0f,
    private val lengthCoefficient: Float = 1.0f,
    private val onStepDetectedListener: (
        xPos: Float, yPos: Float, length: Double, degree: Double, timeStamp: Long
    ) -> Unit,
    private val onIPSDetectedListener: (xPos: Float, yPos: Float) -> Unit,
    private val onPeakRefreshListener: (peak: Float) -> Unit = {},
    private val onValleyRefreshListener: (valley: Float) -> Unit = {}
) : SensorEventListener, AppCompatActivity() {
    private val accelerometerReading = FloatArray(3)
    private val magnetometerReading = FloatArray(3)

    private val rotationMatrix = FloatArray(9)
    private val orientationAngles = FloatArray(3)

    private val mag = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD)
    private val acc = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
    private val lacc = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION)

    private var linearAcc: Float = 0.0f
    private var initTime: Long = 0
    private var preAcc = 0.0f
    public var nowAcc = 0.0f

    private var peak: Float = 0.0f
    private var valley: Float = 0.0f
    private var length: Double = 0.0

    private var azimuthView: TextView = (mContext as IoTSelectionActivity).getAzimuthTextView()
    private var calAzimuthView: TextView =
        (mContext as IoTSelectionActivity).getCalAzimuthTextView()
    private val roomNpole: Double = (mContext as IoTSelectionActivity).getMapNPole()
    private var deg: Double = 0.0

    private val gyroscopeSensorFilter = GyroscopeSensorFilter()

    var activate = true
    var deviceAngleInRoom = 0
    var y_acc = 0.0

    init {
        initTime = System.currentTimeMillis()
    }


    // This function is used to find peak and valley values.
    private val p2pThreshold = 1.0f
    private val peakRefreshThreshold = -0.2f
    fun calcPeakValley(previous: Float, now: Float) {
        //magDir.text = mag.toString()

        // 이전의 값이 현재의 값보다 크다면 peak 값에 저장합니다.
        // 이 때, 1.0 은 peak to peak의 threshold 로 논문에서 사용되었습니다.
        // If the previous value is greater than the current value, it is stored in the peak value.
        // At this time, 1.0 is used as the peak-to-peak threshold in the paper.

        if (previous > now) {
            if (previous > p2pThreshold) {
                peak = previous
                onPeakRefreshListener(peak)
            }
        }

        // 이전의 값이 현재의 값보다 작다면 valley 값에 저장합니다.
        // 이 떄, -0.2 는 임의로 정한 threshold 로
        // 원치 않는 작은 흔들림이 값에 반영되는 것을 피하기 위해 정한 값입니다.
        // If the previous value is less than the current value, it is stored in the valley value.
        // At this time, -0.2 is an arbitrarily set threshold.
        // This value is set to avoid unwanted small shakes from being reflected in the value.
        if (previous < now) {
            if (previous < peakRefreshThreshold) {
                valley = previous
                onValleyRefreshListener(valley)
            }
        }

        // peak 와 valley 값이 모두 0 이 아니라면 다음의 조건문이 실행됩니다.
        // If both peak and valley values are non-zero, the following conditional statement is executed.
        if (peak != 0.0f && valley != 0.0f) {
            Log.d("PEAK&VALLEY", "PEAK : $peak VALLEY : $valley")
            estimateStepLength()    // length 구하는 부분
            notifyStepDetected()   // 걸음 연산 및 걸음 감지 리스너 호출
            peak = 0.0f
            valley = 0.0f   // 다시 peak 와 valley 값을 0 으로 초기화
        }

    }

    fun updatePos(newXpos: Float, newYpos: Float) {
        xPos = newXpos
        yPos = newYpos
        if (!activate) activate = true // Activate false until initially updated to IPS
        onIPSDetectedListener(xPos, yPos)
    }

    fun notifyStepDetected() {
        deg = orientationAngles[0].toDouble() + (roomNpole * PI / 180)
        val timeStamp = System.currentTimeMillis() - initTime
        xPos += length.toFloat() * sin(deg).toFloat()
        yPos -= length.toFloat() * cos(deg).toFloat()

        if (activate) onStepDetectedListener(xPos, yPos, length, deg, timeStamp)
    }


    // 걸음 길이를 추정합니다. 상수값은 SmartPDR 논문의 수치 그대로 사용합니다.
    // Estimate the step length. The constant value is used as it is in the SmartPDR paper.
    fun estimateStepLength() {
        var p2vDiff = peak - valley
        Log.d("debug", "p2v diff: $p2vDiff")
        if (peak != 0.0f && valley != 0.0f) {
            length = if (p2vDiff < Companion.quadSquareThreshold) {
                Companion.quadSquareMultiplyingConstant * mathSqrt(mathSqrt(p2vDiff.toDouble())) +
                        Companion.quadSquareAddingConstant
            } else {
                Companion.logMultiplyingConstant * log10(p2vDiff.toDouble()) + Companion.logAddingConstant
            }
        }
        // 좌표계 변환을 위한 상수 곱셈
        // constant multiplication for coordinate system transformation
        length *= lengthCoefficient
    }


    // getOrientation 함수 부분입니다.
    // This is part of the getOrientation function.
    fun updateOrientationAngles(): Boolean {
        if (accelerometerReading.isEmpty() || magnetometerReading.isEmpty()) return false;
        SensorManager.getRotationMatrix(
            rotationMatrix,
            null,
            accelerometerReading,
            magnetometerReading
        )

        SensorManager.getOrientation(rotationMatrix, orientationAngles)
        var angle = Math.toDegrees(orientationAngles[0].toDouble())
        angle = gyroscopeSensorFilter.applyGyroscopeSensorFilter(angle, 90.0)
        deviceAngleInRoom = (angle + roomNpole).roundToInt()
        val azimuthTextBuilder = (angle.roundToInt()).toString() + "°"
        val calAzimuthTextBuilder = deviceAngleInRoom.toString() + "°"
        azimuthView.text = azimuthTextBuilder
        calAzimuthView.text = calAzimuthTextBuilder

        return true;
    }


    // sensor listener
    fun registerListener() {
        mag.also { mag ->
            sensorManager.registerListener(this, mag, SensorManager.SENSOR_DELAY_NORMAL)
        }
        acc.also { acc ->
            sensorManager.registerListener(this, acc, SensorManager.SENSOR_DELAY_NORMAL)
        }
        lacc.also { lacc ->
            sensorManager.registerListener(this, lacc, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    // unregister sensor listener
    fun unregisterListener() {
        sensorManager.unregisterListener(this)
    }

    // sensor 값이 변할 떄마다 반영되는 함수
    // A function that is reflected whenever the sensor value changes
    override fun onSensorChanged(sensorEvent: SensorEvent?) {
        when (sensorEvent!!.sensor.type) {
            Sensor.TYPE_ACCELEROMETER -> {
                System.arraycopy(
                    sensorEvent.values,
                    0,
                    accelerometerReading,

                    0,
                    accelerometerReading.size
                )
            }
            Sensor.TYPE_MAGNETIC_FIELD -> {
                System.arraycopy(
                    sensorEvent.values,
                    0,
                    magnetometerReading,
                    0,
                    magnetometerReading.size
                )
            }
            Sensor.TYPE_LINEAR_ACCELERATION -> {
                if (updateOrientationAngles()) {                    // Orientation 을 구합니다.
                    linearAcc = sensorEvent.values[0] * rotationMatrix[6] +
                            sensorEvent.values[1] * rotationMatrix[7] +
                            sensorEvent.values[2] * rotationMatrix[8]
                    nowAcc = linearAcc
                    calcPeakValley(preAcc, nowAcc)         // 먼저 peak, valley 값을 구합니다.
                    preAcc = nowAcc                       // 시간이 지남을 반영해준니다.
                }
            }
        }
    }

    override fun onAccuracyChanged(p0: Sensor?, p1: Int) {
        // Nothing to do
    }

    companion object {
        // 논문에 나온 stepLength 공식을 그대로 사용했습니다.
        // We have used stepLength formula in SmartPDR essay
        private const val quadSquareMultiplyingConstant = 1.479f
        private const val quadSquareAddingConstant = -1.259f
        private const val logMultiplyingConstant = 1.131f
        private const val quadSquareThreshold = 3.230f
        private const val logAddingConstant = 0.159f
    }

}