package com.sala.iotlab.sala_app.sala.connect

import com.google.android.gms.common.ConnectionResult.TIMEOUT
import org.jetbrains.anko.AnkoLogger
import org.jetbrains.anko.debug
import java.io.*
import java.net.HttpURLConnection
import java.net.HttpURLConnection.HTTP_OK
import java.net.MalformedURLException
import java.net.URL
import java.net.URLConnection
import kotlin.Exception as Exception1

/**
 * Communication with SALA server and DNSNA server
 * @author 강성민
 */
object HttpConnection : AnkoLogger {
    private const val UTF_8 = "UTF-8"
    private val CHARSET_UTF_8 = Charsets.UTF_8
    private const val METHOD_GET = "GET"
    private const val METHOD_POST = "POST"


    /**
     * Return the result value by performing HTTP GET communication with [url] (Nullable)
     */
    fun getRequest(url: String): String {
        try {
            with(URL(url).openConnection() as HttpURLConnection) {
                setProperties(this, METHOD_GET)
                if (responseCode == 201) {
                    return inputStream.bufferedReader(CHARSET_UTF_8).use {
                        it.readText()
                    }
                }
                if (responseCode == HTTP_OK) {
                    return inputStream.bufferedReader(CHARSET_UTF_8).use {
                        it.readText()
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return ""
    }

    /**
     * Perform HTTP PUT communication with [params] in [url] and return the result value (Nullable)
     */

    fun putRequest(url: String, params: String): String {

        try {
            with(URL(url).openConnection() as HttpURLConnection) {
                setProperties(this, METHOD_POST)
                with(outputStream) {
                    write(params.toByteArray(CHARSET_UTF_8))
                    flush()
                }
                //println(responseMessage)

                if (responseCode == 201) {
                    return inputStream.bufferedReader(CHARSET_UTF_8).use{
                        it.readText()
                    }
                }
                if (responseCode == HTTP_OK) {
                    return inputStream.bufferedReader(CHARSET_UTF_8).use {
                        it.readText()
                    }
                }

            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        return ""
    }

    /**
     * Set RequestMethod of [targetConnection] to [targetMethod] and
     * Set Request Property to [UTF8]
     */
    private fun setProperties(targetConnection: HttpURLConnection, targetMethod: String) {
        with(targetConnection) {
            requestMethod = targetMethod
            setRequestProperty("Accept", "*/*") // Accept-Charset 설정.
            setRequestProperty(
                "Context_Type",
                "application/x-www-form-urlencoded;charset=$UTF_8"
            )
        }
    }
}