package com.sala.iotlab.sala_app.data

import android.os.Parcel
import android.os.Parcelable
import org.jetbrains.anko.AnkoLogger
import org.jetbrains.anko.debug

/**
 * Information about one received IoT device
 */
data class IoTData(
    var deviceType: String,
    var dnsName: String,
    var ipAddress: String,
    var port: Int,
    var macAddress: String,
    var x: Int,
    var y: Int
) : Parcelable {
    constructor(parcel: Parcel) : this(
        parcel.readString().toString(),
        parcel.readString().toString(),
        parcel.readString().toString(),
        parcel.readInt(),
        parcel.readString().toString(),
        parcel.readInt(),
        parcel.readInt()
    )

    override fun writeToParcel(parcel: Parcel, flags: Int) {
        parcel.writeString(deviceType)
        parcel.writeString(dnsName)
        parcel.writeString(ipAddress)
        parcel.writeInt(port)
        parcel.writeString(macAddress)
        parcel.writeInt(x)
        parcel.writeInt(y)
    }

    override fun describeContents(): Int {
        return 0
    }

    companion object CREATOR : Parcelable.Creator<IoTData> {
        override fun createFromParcel(parcel: Parcel): IoTData {
            return IoTData(parcel)
        }

        override fun newArray(size: Int): Array<IoTData?> {
            return arrayOfNulls(size)
        }
    }
}