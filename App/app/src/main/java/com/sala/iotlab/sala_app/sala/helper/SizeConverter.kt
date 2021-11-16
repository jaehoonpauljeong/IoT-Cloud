package com.sala.iotlab.sala_app.sala.helper

import android.util.Log


object SizeConverter {

    /**
     * Get [xDrawMax] and [yDrawMax] as the width and height of the image view you want to draw
     * Set [xActual] and [yActual] to the corresponding image view.
     * Returns [Pair] converted to x, y coordinates
     */
    fun conversionSize(
        xDrawMax: Int, yDrawMax: Int, xActualMax: Int, yActualMax: Int, xActual: Int, yActual: Int,
        xDrawOffset: Int = 0, yDrawOffset: Int = 0,
        xDrawMin: Int = 0, yDrawMin: Int = 0,
        xActualMin: Int = 0, yActualMin: Int = 0
    ): Pair<Int, Int> {
        return Pair<Int, Int>(
            targetConversion(xDrawMax, xActual, xActualMax, xDrawOffset, xDrawMin, xActualMin),
            targetConversion(yDrawMax, yActual, yActualMax, yDrawOffset, yDrawMin, yActualMin)
        )
    }


    /**
     * so that only one axis change
     * Convert [tarActual] to fit [tarDrawMax] and return
     */
    fun targetConversion(
        tarDrawMax: Int, tarActual: Int, tarActualMax: Int,
        tarDrawOffset: Int = 0, tarDrawMin: Int = 0, tarActualMin: Int = 0
    ): Int {
        return conversionSingle(
            tarActual,
            tarActualMax - tarActualMin,
            tarDrawMax - tarDrawMin
        ) + tarDrawOffset
    }


    /**
     * Functions to help with [targetConversion]
     */
    private fun conversionSingle(originalVal: Int, originalMax: Int, targetMax: Int): Int {
        return ((originalVal.toDouble() / originalMax.toDouble()) * targetMax.toDouble()).toInt()
    }

}