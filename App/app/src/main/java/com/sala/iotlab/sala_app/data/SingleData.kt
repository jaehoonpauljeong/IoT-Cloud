package com.sala.iotlab.sala_app.data

/**
 * 측정 Scan Data 하나에 관한 정보
 * One info of a measured Scan data
 */
data class SingleData(
    var x: Int,
    var y: Int,
    var rssi: Int,
    var timeStamp: Long
)