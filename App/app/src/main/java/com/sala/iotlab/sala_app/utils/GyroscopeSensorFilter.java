package com.sala.iotlab.sala_app.utils;

public class GyroscopeSensorFilter {
    private boolean isInitialized = false;
    private double estimatedValue = 0.0;

    /**
     * gyroscope sensor filter reduces minor change sensor values
     * priorValue stores last gyroscope value
     * @param value current gyroscope angle
     * @param full limitaion
     * @return estimated gyroscope angle
     */
    public double applyGyroscopeSensorFilter(double value, double full) {
        double priorValue = 0.0;

        if (!isInitialized) { //for first time
            priorValue = value;
            isInitialized = true;
        }else {
            priorValue = estimatedValue;
        }

        double gain = _sigmoid(Math.abs((value-priorValue)/full));

        estimatedValue = priorValue + gain * (value - priorValue);
        return estimatedValue;
    }

    private double _sigmoid(double x) {
        return (1/( 1 + Math.pow(Math.E,(-1*x))));
    }
}
