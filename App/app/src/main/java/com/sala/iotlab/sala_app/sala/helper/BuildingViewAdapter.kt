package com.sala.iotlab.sala_app.sala.helper

import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.google.gson.Gson
import com.sala.iotlab.sala_app.R
import com.sala.iotlab.sala_app.activity.SectionActivity
import com.sala.iotlab.sala_app.sala.connect.HttpConnection
import com.sala.iotlab.sala_app.structure.AddrStructure
import com.sala.iotlab.sala_app.structure.BuildingInfoStructure
import com.sala.iotlab.sala_app.structure.BuildingStructure
import com.sala.iotlab.sala_app.structure.SectionStructure
import com.sala.iotlab.sala_app.utils.urlHelper
import kotlinx.android.synthetic.main.activity_main_section.*
import kotlinx.coroutines.*


class BuildingViewAdapter(
    private val SECTION_INFO: SectionStructure,
    private val PORT_INFO: AddrStructure
) :
    RecyclerView.Adapter<BuildingViewAdapter.BuildingViewHolder>() {
    lateinit var buildingEntryList: List<BuildingInfoStructure>

    inner class BuildingViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val buildingNum: TextView
        val buildingName: TextView

        init {
            hashMap2ArrayList()
            buildingNum = itemView.findViewById(R.id.buildingNum)
            buildingName = itemView.findViewById(R.id.buildingName)

            itemView.setOnClickListener {
                with(itemView.context as SectionActivity) {
                    val which = buildingEntryList[adapterPosition]
                    whichBuilding.text = which.buildingName
                    lateinit var response: String
                    var BUILDING_INFO = BuildingStructure()
                    val job = GlobalScope.launch {
                        val url: String =
                            "http://${PORT_INFO.CLOUD_IP}:${PORT_INFO.MAIN_PORT}/${urlHelper.reverseURL(SECTION_INFO.fullDns).replace(".", "/")}/${which.buildingID}"
                        Log.d("debug", url);
                        response = HttpConnection.getRequest(url)
                        if(response != "") {
                            Log.d("debug", response)
                            Log.d("debug", "===========================================================")
                            BUILDING_INFO = Gson().fromJson(response, BuildingStructure::class.java)
                        }
                    }
                    runBlocking {
                        job.join()
                    }
                    floors.adapter = FloorViewAdapter(BUILDING_INFO, PORT_INFO)
                }
            }
        }
    }

    fun hashMap2ArrayList() {
        val tmpList: ArrayList<BuildingInfoStructure> = arrayListOf()
        for ((key, value) in SECTION_INFO.buildings) {
            val tmp = BuildingInfoStructure(key, value, SECTION_INFO.buildings_id[key])
            tmpList.add(tmp)
        }
        buildingEntryList = tmpList.sortedBy { it.num }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): BuildingViewHolder {
        val view =
            LayoutInflater.from(parent.context).inflate(R.layout.building_item, parent, false)
        return BuildingViewHolder(view)
    }

    override fun getItemCount(): Int {
        return SECTION_INFO.buildings.size
    }

    override fun onBindViewHolder(holder: BuildingViewAdapter.BuildingViewHolder, position: Int) {
        with(holder) {
            buildingNum.apply {
                setText(buildingEntryList[position].num.toString())
            }
            buildingName.apply {
                setText(buildingEntryList[position].buildingName)
            }
        }
    }

}