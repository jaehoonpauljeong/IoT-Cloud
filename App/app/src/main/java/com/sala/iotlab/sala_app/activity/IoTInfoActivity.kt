package com.sala.iotlab.sala_app.activity

import android.app.Activity
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.Window
import com.google.gson.Gson
import com.sala.iotlab.sala_app.R
import com.sala.iotlab.sala_app.data.IoTData
import com.sala.iotlab.sala_app.data.IoTDataManager
import com.sala.iotlab.sala_app.sala.iot.control.LightControl
import com.sala.iotlab.sala_app.structure.RoomStructure
import kotlinx.android.synthetic.main.activity_iotinfo.*
import org.jetbrains.anko.toast

class IoTInfoActivity : Activity() {
    private var isOn = false
    private lateinit var lightControl: LightControl

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestWindowFeature(Window.FEATURE_NO_TITLE)
        setContentView(R.layout.activity_iotinfo)

        val intent = intent
        val ROOM_INFO: RoomStructure =
            Gson().fromJson(intent.getStringExtra("ROOM_INFO"), RoomStructure::class.java)
        val iotData: IoTData = intent.getParcelableExtra<IoTData>("data")!!
        iotDeviceType.text = iotData.deviceType
        iotDevicePosition.text = "X 좌표 : ${iotData.x}  Y 좌표 : ${iotData.y}"
        iotDeviceDnsName.text = iotData.dnsName
        iotDeviceIpAddress.text = iotData.ipAddress

        when (iotData.deviceType) {
            IoTDataManager.TYPE_LIGHT -> {
                deviceLight.text = "전등 스위치"
                fun lightOn() {
                    light_control.visibility = View.VISIBLE
                    toast("LED 켬")
                    light_control.setImageResource(R.drawable.light_on)
                }

                fun lightOff() {
                    light_control.visibility = View.VISIBLE
                    toast("LED 끔")
                    light_control.setImageResource(R.drawable.light_off)

                }
                lightControl = LightControl(
                    iotData,
                    ROOM_INFO = ROOM_INFO,
                    lightOnListener = { lightOn() },
                    lightOffListener = { lightOff() })

                isOn = lightControl.getStatus()

                fun onclick(v: View) {
                    //v.isClickable = false
                    v.visibility = View.GONE
                    isOn = !isOn
                    Log.d("debug", "isOn: " + isOn)
                    if (isOn) {
                        Log.d("debug", "turning on")
                        lightControl.lightOn()
                    } else {
                        Log.d("debug", "turning off")
                        lightControl.lightOff()
                    }
                }
                light_control.setOnClickListener { onclick(it) }
            }
            else -> {
                light_control.visibility = View.GONE
                deviceLight.visibility = View.GONE
            }
        }

    }

}
