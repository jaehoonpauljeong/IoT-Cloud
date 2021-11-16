package com.sala.iotlab.sala_app.data

/**
 * A bundle of scan information about a device with a specific address
 */
data class ScanData(
    var iotName: String,
    var macAddress: String,
    var ipAddress: String,
    var scans: ArrayList<SingleData> = ArrayList()
)