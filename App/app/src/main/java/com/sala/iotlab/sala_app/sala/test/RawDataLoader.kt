package com.sala.iotlab.sala_app.sala.test

import android.util.Log
import com.sala.iotlab.sala_app.data.ScanData
import com.sala.iotlab.sala_app.data.SingleData
import com.sala.iotlab.sala_app.sala.connect.HttpConnection
import java.io.File
import java.io.InputStream

class RawDataLoader {
    val rawDataFile: File?
    val scanData: ScanData = ScanData("test", "test", "test", ArrayList<SingleData>());

    companion object {
        const val IOT_NAME_POS = 0;
        const val MAC_ADDRESS_POS = 1;
        const val IP_ADDRESS_POS = 2;
        const val DATA_STARTING_POS = 3;

        const val DATA_TIMESTAMP_POS = 0;
        const val DATA_X_POS = 1;
        const val DATA_Y_POS = 2;
        const val DATA_RSSI_POS = 3;

        const val DATA_SIZE = 3;
    }

    constructor(inputStream: InputStream) {
        rawDataFile = null;
        val textVal =
            inputStream.bufferedReader(Charsets.UTF_8).use {
                it.readText()
            }
        parseFromString(textVal);
    }

    constructor(fileDir: String) {
        rawDataFile = File(fileDir);

        val textVal = rawDataFile.readText(Charsets.UTF_8);
        parseFromString(textVal);
    }

    constructor(dataFile: File) {
        this.rawDataFile = dataFile;

        val textVal = rawDataFile.readText(Charsets.UTF_8);
        parseFromString(textVal);
    }

    private fun parseFromString(targetStr: String) {
        val parsed = targetStr.split("\n");
        this.scanData.iotName = parsed[IOT_NAME_POS];
        this.scanData.macAddress = parsed[MAC_ADDRESS_POS];
        this.scanData.ipAddress = parsed[IP_ADDRESS_POS];

        val parsedLine = parsed.size - 1;
        for (i in DATA_STARTING_POS..parsedLine) {
            val spited = parsed[i].split(" ");
            if(spited.size < DATA_SIZE) continue;
            this.scanData.scans.add(
                SingleData(
                    x = spited[DATA_X_POS].toDouble().toInt(),
                    y = spited[DATA_Y_POS].toDouble().toInt(),
                    timeStamp = spited[DATA_TIMESTAMP_POS].toInt().toLong(),
                    rssi = spited[DATA_RSSI_POS].trimEnd().toInt()
                )
            )

        }
    }

}