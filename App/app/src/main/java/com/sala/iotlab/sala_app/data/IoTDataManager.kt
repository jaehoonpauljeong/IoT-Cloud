package com.sala.iotlab.sala_app.data

import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.sala.iotlab.sala_app.structure.DeviceStructure
import kotlinx.coroutines.*
import org.jetbrains.anko.AnkoLogger
import org.jetbrains.anko.info
import org.xbill.DNS.Lookup
import org.xbill.DNS.Record
import org.xbill.DNS.SimpleResolver
import org.xbill.DNS.TextParseException
import java.net.InetAddress
import java.net.UnknownHostException
import java.util.concurrent.Future

/**
 * Singleton to manage IoTData class
 * @author 유영석
 */
object IoTDataManager : AnkoLogger {

    const val NOT_DNS: Int = 0xA001
    const val DNS_BUT_NO_POS: Int = 0xA002
    const val DNS_WITH_POS: Int = 0xA003

    private const val DNS_OFFSET_MAC: Int = 0
    private const val DNS_OFFSET_X: Int = 4
    private const val DNS_OFFSET_Y: Int = 5
    private const val DNS_OFFSET_TYPE: Int = 3

    /*
     타입.mac(:생략).x.y.호수.건물.대분류.3차도메인.2차도메인.1차도메인
     ex) FFH12CD3.UID.raspPi.LED.x.y.COORD.400625.ROOM.semiconductor.BUILDING.skku.LOC.cpslab.skku.edu
     수신용은 x, y 대신 좌표값
     */

    fun makeMacWithColon(raw: String): String{
        if(raw.length != 12) return raw
        return "${raw[0]}${raw[1]}:${raw[2]}${raw[3]}:${raw[4]}${raw[5]}:${raw[6]}${raw[7]}:${raw[8]}${raw[9]}:${raw[10]}${raw[11]}"
    }

    fun makeMacWithoutColon(raw: String): String{
        if(raw.length != 17) return raw
        return "${raw[0]}${raw[1]}${raw[3]}${raw[4]}${raw[6]}${raw[7]}${raw[9]}${raw[10]}${raw[12]}${raw[13]}${raw[15]}${raw[16]}"
    }


    /**
     * Returns [DNS_WITH_POS] if [dnsName] is a valid DNS name
     */
    fun checkDNSName(dnsName: String): Int {
        val tokens = dnsName.split("""\.""".toRegex()).toMutableList()
        val size = tokens.size

        if (size < DNS_OFFSET_Y) {
            return NOT_DNS
        }

        try {
            Integer.parseInt(tokens[DNS_OFFSET_X])
            Integer.parseInt(tokens[DNS_OFFSET_Y])
        } catch (e: Exception) {
            return DNS_BUT_NO_POS
        }

        return DNS_WITH_POS
    }


    /**
     * Converts [dnsName] to a pure DNS Name and returns it
     * If conversion is not possible, [dnsName] is returned as is.
     */
    fun getPureDNSName(dnsName: String): String {
        if (checkDNSName(dnsName) != DNS_WITH_POS) return dnsName

        val tokens = dnsName.split("""\.""".toRegex()).toMutableList()
        //val size = tokens.size

        tokens[DNS_OFFSET_X] = "x"
        tokens[DNS_OFFSET_Y] = "y"
        return tokens.joinToString(separator = ".")
    }

    /**
     * Returns a new [IoTData] object with DNS name [dnsName] and IP address [ip]
     */
    fun generateIoTData(dnsName: String, ip: String, port: Int): IoTData {
        val regex = "\\.".toRegex()
        val tokens: List<String> = regex.split(dnsName).toMutableList()
        //val size = tokens.size
        val pos_x = try{
            Integer.parseInt(tokens[DNS_OFFSET_X])
        } catch (e: Exception){
            -1
        }
        val pos_y = try{
            Integer.parseInt(tokens[DNS_OFFSET_Y])
        } catch (e: Exception){
            -1
        }
        val macAddr = makeMacWithColon(tokens[DNS_OFFSET_MAC])

        val type = formatType(tokens[DNS_OFFSET_TYPE].toUpperCase())

        info { "IoTData가 생성됨 -> 타입 : ${type} , DNS 이름 : ${dnsName} , IP 주소 : ${ip} , MAC 주소: ${macAddr} X좌표 : ${pos_x} , Y좌표 : ${pos_y}" }

        return IoTData(type, getPureDNSName(dnsName), ip, port, macAddr, pos_x, pos_y)
    }

    /**
     * Converts a raw [tarStr] representing the type into a standardized format and returns it
     */
    private fun formatType(tarStr: String): String {
        with(tarStr) {
            return when {
                contains("TV") -> TYPE_TV
                contains("AIR") -> TYPE_AIRCONDITIONER
                contains("LED") || contains("LIGHT") -> TYPE_LIGHT
                contains("TEMPERATURE") -> TYPE_TEMPERATURE
                contains("STOVE") || contains("GASRANGE") -> TYPE_GASSTOVE
                contains("CCTV") -> TYPE_CCTV
                contains("SPEAKER") || contains("SOUND") -> TYPE_SPEAKER
                else -> tarStr
            }
        }
    }

    private const val TYPE_TV: String = "TV"
    private const val TYPE_AIRCONDITIONER: String = "AIRCONDITIONER"
    const val TYPE_LIGHT: String = "LIGHT"
    private const val TYPE_TEMPERATURE: String = "TEMPERATURE"
    private const val TYPE_GASSTOVE: String = "GASSTOVE"
    private const val TYPE_CCTV: String = "CCTV"
    private const val TYPE_SPEAKER: String = "SPEAKER"

}