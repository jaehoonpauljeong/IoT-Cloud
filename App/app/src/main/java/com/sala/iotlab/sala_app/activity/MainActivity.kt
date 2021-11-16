package com.sala.iotlab.sala_app.activity

import kotlinx.android.synthetic.main.activity_main.*
import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.google.gson.Gson
import com.sala.iotlab.sala_app.R
import com.sala.iotlab.sala_app.sala.connect.HttpConnection
import com.sala.iotlab.sala_app.structure.AddrStructure
import kotlinx.coroutines.*
import org.jetbrains.anko.startActivity


class MainActivity : AppCompatActivity() {
    val CLOUD_IP = "192.168.1.29"
    val CLOUD_PORT = 9000
    val IMAGE_PORT = 9001
    var ADDR_CLASS = AddrStructure(CLOUD_IP, CLOUD_PORT, IMAGE_PORT)

    lateinit var sectionInfo: String
    suspend fun networkRequire(section: String) {
        val sectionURL = "http://$CLOUD_IP:${CLOUD_PORT}/${section}"
        Log.d("debug", sectionURL)
        val networkJob = GlobalScope.launch(Dispatchers.Default) {
            sectionInfo = HttpConnection.getRequest(sectionURL)
            Log.d("debug", sectionInfo)
        }
        networkJob.join()
        networkJob.cancel()
    }

    fun setOnButtonCreate() {
        house.setOnClickListener {
            GlobalScope.launch() {
                onButtonClick("GwangGyo_SummitPlace")
            }
        }
        skku.setOnClickListener {
            GlobalScope.launch() {
                onButtonClick("skku")
            }
        }
        office.setOnClickListener {
            GlobalScope.launch() {
                onButtonClick("office")
            }
        }
    }

    suspend fun onButtonClick(section: String) {
        networkRequire(section)
        Log.d("debug", "================================END===============================")
        startActivity<SectionActivity>(
            "ADDR_CLASS" to Gson().toJson(ADDR_CLASS),
            "SECTION_INFO" to sectionInfo,
            "CLOUD_ADDRESS" to "http://$CLOUD_IP:"
        )
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setOnButtonCreate()
    }
}

