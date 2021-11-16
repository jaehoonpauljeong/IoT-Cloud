package com.sala.iotlab.sala_app

import com.sala.iotlab.sala_app.sala.connect.HttpConnection
import org.junit.Test

import org.junit.Assert.*

/**
 * Example local unit test, which will execute on the development machine (host).
 *
 * See [testing documentation](http://d.android.com/tools/testing).
 */
class ExampleUnitTest {
    @Test
    fun addition_isCorrect() {
        assertEquals(4, 2 + 2)
    }

    @Test
    fun main() {
        HttpConnection.getRequest("http://192.168.0.8:8090/skku/cpslab/400609/IoTLists")


    }


}
