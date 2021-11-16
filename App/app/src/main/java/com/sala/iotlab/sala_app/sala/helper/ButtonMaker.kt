package com.sala.iotlab.sala_app.sala.helper

import android.util.Log
import androidx.constraintlayout.widget.ConstraintLayout
import androidx.constraintlayout.widget.ConstraintSet
import com.google.android.material.button.MaterialButton
import com.sala.iotlab.sala_app.R
import com.sala.iotlab.sala_app.activity.IoTInfoActivity
import com.sala.iotlab.sala_app.data.IoTData
import com.sala.iotlab.sala_app.sala.SALAManager
import org.jetbrains.anko.startActivity

class ButtonMaker(val salaManager: SALAManager) {

    fun generateButton(
        ioTData: IoTData,
        width: Int = 50, height: Int = 50,
        xDrawMax: Int = -1, yDrawMax: Int = -1,
        roomInfo: String
    ): MaterialButton {

        val myButton = MaterialButton(
            salaManager.mContext,
            null,
            R.style.Widget_MaterialComponents_Button_OutlinedButton
        )

        with(myButton) {
            setBackgroundResource(R.color.colorTransparent)
            setCompoundDrawablesWithIntrinsicBounds(findImageId(ioTData), 0, 0, 0)
            iconGravity = MaterialButton.ICON_GRAVITY_TEXT_START
            iconPadding = 0
            setPadding(0, 0, 0, 0)

            val buttonSizeWidth =
                (width.toFloat() * salaManager.mContext.resources.displayMetrics.density).toInt()
            val buttonSizeHeight =
                (height.toFloat() * salaManager.mContext.resources.displayMetrics.density).toInt()
            with(
                ConstraintLayout.LayoutParams(
                    buttonSizeWidth,
                    buttonSizeHeight
                )
            ) {
                if (salaManager == null) {
                    leftMargin = ioTData.x
                    topMargin = ioTData.y
                } else {
                    leftMargin = SizeConverter.targetConversion(
                        tarDrawMax = salaManager.targetImageView.measuredWidth,
                        tarActual = ioTData.x,
                        tarActualMax = salaManager.ROOM_INFO.width,
                        tarDrawOffset = salaManager.targetImageView.x.toInt()
                    ) - buttonSizeWidth / 2
                    topMargin = SizeConverter.targetConversion(
                        tarDrawMax = salaManager.targetImageView.measuredHeight,
                        tarActual = ioTData.y,
                        tarActualMax = salaManager.ROOM_INFO.height,
                        tarDrawOffset = salaManager.targetImageView.y.toInt()
                    ) - buttonSizeHeight / 2
                    // button left top corner appears at IoT coordinate
                }

                topToTop = ConstraintSet.PARENT_ID
                leftToLeft = ConstraintSet.PARENT_ID

                layoutParams = this
            } // Set size and position

            tag = ioTData // Tagging

            setOnClickListener {
                salaManager.mContext.startActivity<IoTInfoActivity>(
                    "data" to ioTData,
                    "ROOM_INFO" to roomInfo
                )
            } // Set IoTInfoActivity to turn on when touched
            return this
        }
    }

    private fun findImageId(ioTData: IoTData): Int {
        return when (ioTData.deviceType.toUpperCase()) {
            "TV" -> R.mipmap.tv
            "AIRCONDITIONER" -> R.mipmap.airconditioner
            "LIGHT" -> R.mipmap.light
            "TEMPERATURE" -> R.mipmap.temperature
            "GASSTOVE" -> R.mipmap.gasstove
            "CCTV" -> R.mipmap.cctv
            "SPEAKER" -> R.mipmap.speaker
            "HUMAN" -> R.mipmap.human
            else -> R.mipmap.iot
        }
    }
}