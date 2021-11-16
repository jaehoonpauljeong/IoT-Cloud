package com.sala.iotlab.sala_app.activity

import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.util.Log
import android.view.View
import android.widget.ImageView
import android.widget.TextView
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.constraintlayout.widget.ConstraintLayout
import com.google.android.material.button.MaterialButton
import com.google.gson.Gson
import com.sala.iotlab.sala_app.R
import com.sala.iotlab.sala_app.data.IoTData
import com.sala.iotlab.sala_app.data.IoTDataManager
import com.sala.iotlab.sala_app.sala.SALAManager
import com.sala.iotlab.sala_app.sala.connect.IoTDataLoader
import com.sala.iotlab.sala_app.sala.device.DevicePositionManager
import com.sala.iotlab.sala_app.sala.helper.ButtonMaker
import com.sala.iotlab.sala_app.structure.AddrStructure
import com.sala.iotlab.sala_app.structure.RoomStructure
import com.sala.iotlab.sala_app.utils.urlHelper
import com.squareup.picasso.Picasso
import kotlinx.android.synthetic.main.activity_iotselection.*
import org.jetbrains.anko.AnkoLogger


class IoTSelectionActivity() : AppCompatActivity(), AnkoLogger {
    private lateinit var mSALAManager: SALAManager
    private var iotDevices = HashMap<String, IoTData>()// mac -> data
    private var iotButtons = HashMap<String, MaterialButton>() // mac -> button
    private lateinit var buttonMaker: ButtonMaker
    private lateinit var roomInfo: String
    private lateinit var ROOM_INFO: RoomStructure
    private lateinit var PORT_INFO: AddrStructure
    private lateinit var humanButton: MaterialButton
    lateinit var azimuthText: TextView
    lateinit var calAzimuthText: TextView

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    override fun onDestroy() {
        super.onDestroy()
        mSALAManager.stopAll()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_iotselection)
        val intent = intent
        azimuthText = azimuth
        calAzimuthText = calAzimuth
        val portInfo = intent.getStringExtra("PORT_INFO")
        roomInfo = intent.getStringExtra("ROOM_INFO")
        val buildingName = intent.getStringExtra("BUILDING_NAME")

        PORT_INFO = Gson().fromJson(portInfo, AddrStructure::class.java)
        ROOM_INFO = Gson().fromJson(roomInfo, RoomStructure::class.java)

        val RoomImageUrl = "http://${PORT_INFO.CLOUD_IP}:${PORT_INFO.IMAGE_PORT}/${urlHelper.reverseURL(ROOM_INFO.fullDns).replace(
                ".", "/")}/${ROOM_INFO.img.path}"
        val map = findViewById<ImageView>(R.id.roomMap)
        Picasso.get().load(RoomImageUrl).into(map)

        buildingInfo.text = buildingName
        roomNum.text = ROOM_INFO.name + "(${ROOM_INFO.id})"


        mSALAManager = SALAManager(
            this,
            roomMap,
            DevicePositionManager(onPositionChangedListener = { humanXPos: Float, humanYPos: Float ->
                runOnUiThread {
                    this.refreshHumanButton(
                        mSALAManager.mButtonMaker.generateButton(
                            IoTData(
                                "HUMAN", "USER", "0.0.0.0", 0, "aa:bb:cc:dd:ee:ff",
                                humanXPos.toInt(), humanYPos.toInt()
                            ), roomInfo = roomInfo
                        )
                    )
                }
            }, mContext = this),
            ROOM_INFO = ROOM_INFO,
            IoTDataLists = iotDevices
        )
        mSALAManager.calcActualImageViewSize()
        buttonMaker = ButtonMaker(mSALAManager)

        buttonMaker = mSALAManager.mButtonMaker
        //generateSomething() // Simulation start
        mSALAManager.startAll() // start PDR
        TestIoTGenerationThread().start() // Generate test IoT Icon
    }

    inner class TestIoTGenerationThread : Thread() {
        override fun run() {
            /*val testIoT =
                IoTDataManager.generateIoTData(
                    "E84E06187E70.UID.raspPi.LED.0.0.COORD.400609.ROOM.semicond.BUILDING.skku.LOC.cpslab.skku.edu",
                    "192.168.0.0", 5050
                )
            runOnUiThread { refreshIoTWithData(testIoT) }*/

            //coapTest()
            //val airConditioner =
            //    IoTDataManager.generateIoTData( "AIR.E84E06187E71.300.400.400609.semiconductor.skku.cpslab.skku.edu")
            //runOnUiThread{ refreshIoTWithData(airConditioner) }
        }
    }

    private fun loadAllIoTData() {
        Log.d(
            "debug",
            "================================loadAllIoTData Action================================"
        )
        val mIoTDataLoader = IoTDataLoader(applicationContext) { iotDatum ->
            for (iotData in iotDatum) {
                Log.d("debug", "Making Button: " + iotData.dnsName)
                refreshIoTWithData(iotData)
            }
        }
        mIoTDataLoader.getData(PORT_INFO, ROOM_INFO)
    }

    private fun generateSimulatedIoTButton() {
        Handler().postDelayed({
            var myButton = buttonMaker.generateButton(
                IoTData("CCTV", "DNSNAME1", "1.2.3.4", 0, "aa:bb:cc:dd:ee:ff", 0, 50)
                , roomInfo = roomInfo
            )
            iotselectionLayout.addView(
                myButton,
                myButton.layoutParams as ConstraintLayout.LayoutParams
            )

            myButton = buttonMaker.generateButton(
                IoTData("GASSTOVE", "DNSNAME2", "2.3.4.5", 0, "aa:bb:cc:dd:ee:ff", 0, 390)
                , roomInfo = roomInfo
            )
            iotselectionLayout.addView(
                myButton,
                myButton.layoutParams as ConstraintLayout.LayoutParams
            )

            myButton = buttonMaker.generateButton(
                IoTData("LIGHT", "DNSNAME3", "3.4.5.6", 0, "aa:bb:cc:dd:ee:ff", 330, 370)
                , roomInfo = roomInfo
            )
            iotselectionLayout.addView(
                myButton,
                myButton.layoutParams as ConstraintLayout.LayoutParams
            )

            myButton = buttonMaker.generateButton(
                IoTData(
                    "TEMPERATURE",
                    "DNSNAME4",
                    "4.5.6.7",
                    0,
                    "aa:bb:cc:dd:ee:ff",
                    0,
                    600
                )
                , roomInfo = roomInfo
            )
            iotselectionLayout.addView(
                myButton,
                myButton.layoutParams as ConstraintLayout.LayoutParams
            )

            myButton = buttonMaker.generateButton(
                IoTData("SPEAKER", "DNSNAME5", "5.6.7.8", 0, "aa:bb:cc:dd:ee:ff", 420, 400)
                , roomInfo = roomInfo
            )
            iotselectionLayout.addView(
                myButton,
                myButton.layoutParams as ConstraintLayout.LayoutParams
            )

            myButton = buttonMaker.generateButton(
                IoTData(
                    "AIRCONDITIONER",
                    "DNSNAME6",
                    "6.7.8.9",
                    0,
                    "aa:bb:cc:dd:ee:ff",
                    500,
                    50
                )
                , roomInfo = roomInfo
            )
            iotselectionLayout.addView(
                myButton,
                myButton.layoutParams as ConstraintLayout.LayoutParams
            )

            myButton = buttonMaker.generateButton(
                IoTData("TV", "DNSNAME7", "7.8.9.10", 0, "aa:bb:cc:dd:ee:ff", 400, 730)
                , roomInfo = roomInfo
            )
            iotselectionLayout.addView(
                myButton,
                myButton.layoutParams as ConstraintLayout.LayoutParams
            )

            myButton = buttonMaker.generateButton(
                IoTData("VR", "DNSNAME8", "8.9.10.11", 0, "aa:bb:cc:dd:ee:ff", 600, 600)
                , roomInfo = roomInfo
            )
            iotselectionLayout.addView(
                myButton,
                myButton.layoutParams as ConstraintLayout.LayoutParams
            )

        }, 100)
    }

    fun refreshHumanButton(tarButton: MaterialButton) {
        if (::humanButton.isInitialized) {
            iotselectionLayout.removeView(humanButton)
            humanButton = tarButton
            iotselectionLayout.addView(humanButton)
        } else {
            humanButton = tarButton
            iotselectionLayout.addView(humanButton)
        }
    }

    fun refreshIoTWithData(iotData: IoTData) {
        synchronized(iotDevices) {
            if (iotDevices.containsKey(iotData.macAddress)) {
                iotselectionLayout.removeView(iotButtons[iotData.macAddress]) // 기존 버튼 제거
            }

            iotDevices[iotData.macAddress] = iotData
            iotButtons[iotData.macAddress] =
                buttonMaker.generateButton(iotData, roomInfo = roomInfo)
            iotselectionLayout.addView(
                iotButtons[iotData.macAddress],
                iotButtons[iotData.macAddress]!!.layoutParams as ConstraintLayout.LayoutParams
            ) // 새로운 데이터 생성 및 버튼 생성
        }
    }

    fun runSimulation(v: View) {
        mSALAManager.getDevicePositionManager()
            .registerSpecific(DevicePositionManager.SIMULATE_POSITION)
    }

    fun refreshButtonPressed(view: View) {
        loadAllIoTData()
    }

    fun getAzimuthTextView(): TextView {
        return azimuthText
    }

    fun getCalAzimuthTextView(): TextView {
        return calAzimuthText
    }

    fun getMapNPole(): Double {
        return ROOM_INFO.img.n_pole
    }
}
