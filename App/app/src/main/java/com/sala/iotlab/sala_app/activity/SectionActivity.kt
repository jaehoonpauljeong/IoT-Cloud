package com.sala.iotlab.sala_app.activity

import android.os.Bundle
import android.util.Log
import android.widget.Button
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.github.chrisbanes.photoview.PhotoView
import com.google.gson.Gson
import com.sala.iotlab.sala_app.R
import com.sala.iotlab.sala_app.sala.helper.BuildingViewAdapter
import com.sala.iotlab.sala_app.sala.helper.FloorViewAdapter
import com.sala.iotlab.sala_app.structure.AddrStructure
import com.sala.iotlab.sala_app.structure.BuildingStructure
import com.sala.iotlab.sala_app.structure.SectionStructure
import com.sala.iotlab.sala_app.utils.urlHelper
import com.squareup.picasso.Picasso
import kotlinx.android.synthetic.main.activity_iotselection.view.*

class SectionActivity : AppCompatActivity() {
    lateinit var PORT_INFO: AddrStructure
    lateinit var SECTION_INFO: SectionStructure

    fun getSectionImage(photoView: PhotoView) {
        val imageURL = "http://${PORT_INFO.CLOUD_IP}:${PORT_INFO.IMAGE_PORT}/${urlHelper.reverseURL(SECTION_INFO.fullDns).replace(".", "/")}/${SECTION_INFO.img}"
        Log.d("debug", imageURL)
        Picasso.get().load(imageURL).into(photoView);
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main_section)

        val enter: Button
        enter = findViewById<Button>(R.id.enter)
        enter.isEnabled = false
        val intent = intent
        PORT_INFO = Gson().fromJson(intent.getStringExtra("ADDR_CLASS"), AddrStructure::class.java)
        SECTION_INFO = Gson().fromJson(intent.getStringExtra("SECTION_INFO"), SectionStructure::class.java)

        val photoView = findViewById<PhotoView>(R.id.sectionmap)
        getSectionImage(photoView)

        findViewById<RecyclerView>(R.id.buildings).apply {
            setHasFixedSize(true)
            layoutManager = LinearLayoutManager(this@SectionActivity)
            adapter = BuildingViewAdapter(SECTION_INFO, PORT_INFO)
        }
        val bin_BuildingStructure = BuildingStructure()
        findViewById<RecyclerView>(R.id.floors).apply {
            setHasFixedSize(true)
            layoutManager = LinearLayoutManager(this@SectionActivity)
            adapter = FloorViewAdapter(bin_BuildingStructure, PORT_INFO)
        }
    }
}