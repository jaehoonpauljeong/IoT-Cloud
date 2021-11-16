package com.sala.iotlab.sala_app.sala.helper

import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.github.chrisbanes.photoview.PhotoView
import com.google.gson.Gson
import com.sala.iotlab.sala_app.R
import com.sala.iotlab.sala_app.activity.*
import com.sala.iotlab.sala_app.sala.connect.HttpConnection
import com.sala.iotlab.sala_app.structure.AddrStructure
import com.sala.iotlab.sala_app.structure.BuildingStructure
import com.sala.iotlab.sala_app.structure.FloorInfoStructure
import com.sala.iotlab.sala_app.utils.urlHelper
import com.squareup.picasso.Picasso
import kotlinx.android.synthetic.main.activity_main_section.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.jetbrains.anko.startActivity


class FloorViewAdapter(
    private val BUILDING_INFO: BuildingStructure,
    private val PORT_INFO: AddrStructure
) :
    RecyclerView.Adapter<FloorViewAdapter.FloorViewHolder>() {
    lateinit var floorEntryList: List<FloorInfoStructure>
    private val floorList = (1..BUILDING_INFO.floors).toList().toTypedArray()
    lateinit var ROOM_RESPONSE: String

    inner class FloorViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val floorNum: TextView = itemView.findViewById(R.id.floor_text)
        init {
            hashMap2ArrayList()
            itemView.setOnClickListener {
                with(itemView.context as SectionActivity) {
                    val which = floorEntryList[adapterPosition]
                    whichFloor.text = which.floor.toString() + "층"
                    lateinit var response: String
                    val reversedDnsName = urlHelper.reverseURL(BUILDING_INFO.fullDns)
                    Log.d("debug", reversedDnsName)
                    val imageURL: String =
                        "http://${PORT_INFO.CLOUD_IP}:${PORT_INFO.IMAGE_PORT}/${reversedDnsName.replace(
                            '.',
                            '/'
                        )}/${which.floorImage}"
                    val photoView = findViewById<PhotoView>(R.id.sectionmap)
                    Picasso.get().load(imageURL).into(photoView);
                    enter.isEnabled = true
                    enter.setOnClickListener {
                        onButtonClick(whichRoom)

                        startActivity<IoTSelectionActivity>(
                            "PORT_INFO" to Gson().toJson(PORT_INFO),
                            "ROOM_INFO" to ROOM_RESPONSE,
                            "BUILDING_NAME" to BUILDING_INFO.name
                        )
                    }
                }
            }
        }
    }

    fun onButtonClick(whichRoom: EditText) {
        val room_num = whichRoom.text.toString()
        if (!room_num.isEmpty()) {
            val job = GlobalScope.launch(Dispatchers.Default) {
                val reversedDnsName = urlHelper.reverseURL(BUILDING_INFO.fullDns)
                val url: String =
                    "http://${PORT_INFO.CLOUD_IP}:${PORT_INFO.MAIN_PORT}/${reversedDnsName.replace(
                        '.', '/')}/$room_num"
                Log.d("debug", url);
                ROOM_RESPONSE = HttpConnection.getRequest(url)
                if(ROOM_RESPONSE != "") {
                    Log.d("debug", ROOM_RESPONSE)
                    Log.d("debug", "========================================")
                }
            }
            runBlocking {
                job.join()
            }
        }
    }

    fun hashMap2ArrayList() {
        val tmpList: ArrayList<FloorInfoStructure> = arrayListOf()
        for ((key, value) in BUILDING_INFO.sections) {
            val tmp = FloorInfoStructure(key, value)
            tmpList.add(tmp)
        }
        floorEntryList = tmpList.sortedBy { it.floor }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FloorViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.floor_item, parent, false)
        return FloorViewHolder(view)
    }

    override fun onBindViewHolder(holder: FloorViewHolder, position: Int) {
        holder.floorNum.text = floorList[position].toString() + "F"
    }

    override fun getItemCount(): Int {
        return floorList.size
    }
}