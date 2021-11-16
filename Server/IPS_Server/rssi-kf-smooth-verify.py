#!/home/chris/anaconda3/bin/python
## !/usr/bin/env python3

import os
import sys
import numpy as np
import math
import time
import argparse
import statistics

# plotting
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from scipy.optimize import curve_fit

# pretty printer
import pprint

# local
from LogReader import LogReader
# from KalmanFilter import KalmanFilter
from Beacon import Beacon

def parseArgments():
    parser = argparse.ArgumentParser(description='Specify log data path.')
    parser.add_argument('--path', type=str, nargs=1, help='Log data path')
    parser.add_argument('--dist', type=str, nargs=1, help='rssi data distance')

    return parser
	# args = parser.parse_args()


'''
a    9.4249
b   -0.5870
c  -63.3589
'''
def func(x, a, b, c):
    # print(x)
    # print(a, b ,c)
    return a * np.exp(b * x) + c

def proCaliData(logData):
    collData = {}
    for key, val in logData.items():
        # apId = key.split(',')[0]
        # dist = key.split(',')[1]
        # dist = key.split(',')[1]
        
        collData[key]=val   
    
    return collData

def funcRSSI(x, n, c):
    # print(x)
    # print(a, b ,c)
    rssi = -10*n*np.log10(x)+c
    return rssi

'''
front:
n = 1.14671509 
c = -72.6929423

back:
n = 0.32933467 
c = -80.59605795
'''

# this is the main entry point of this script
if __name__ == "__main__":

    args = parseArgments().parse_args()

    # load RSSI log data
    logData = {}
    reader = LogReader()

    filePath = args.path
    logData = reader.readFolderRPI(folderDir=filePath[0])
    # print(logData)
    collData = proCaliData(logData)
    # print(collData)
    # print(sorted(collData))

    # collData, key: distance, value: [rssi list]
    # sys.exit()

    # xAxis=[float(i) for i in sorted(collData)]
    # avgYAxis = []

    # extXAxis = []
    # extYAxis = []
    # pointSize = []

    xAxis = []
    count = 1
    originalRSSIList=[]
    filteredRSSIList=[]

    originalDistList=[]
    filteredDistList=[]

    key=args.dist
    groundtrueDistKey=key[0]
    groundtrueDistList=[]

    beacon = Beacon()
    for value in collData[groundtrueDistKey]:
        originalRSSIList.append(float(value))
        originalDistList.append(beacon.rssi2dist(float(value)))
        beacon.rssi = float(value)
        beacon.lastSeq = 1
        beacon.rssiHis.append(float(value))
        filteredRSSI = beacon.applyMA()
        #[j]filteredRSSI = beacon.applyKF4Rssi()
        # filteredRSSI = beacon.applyAvgRssi()
        # print(filteredRSSI)        
        filteredRSSIList.append(filteredRSSI)
        filteredDistList.append(beacon.rssi2dist(filteredRSSI))
        groundtrueDistList.append(float(groundtrueDistKey))
        xAxis.append(count)
        count += 1
    
    # print(originalRSSIList)
    # print(filteredRSSIList)

    # for key in sorted(collData):
    #     valCount = {} # key: y data point, value: count
    #     for ele in collData[key]:
    #         if ele not in valCount:
    #             valCount[ele] = 1
    #         else:
    #             valCount[ele] += 1

    #     extXAxis += [key] * len(valCount.keys())
    #     extYAxis += [i for i in valCount.keys()]
    #     pointSize += [i*2.5 for i in valCount.values()]

    #     # mean y
    #     avgYAxis += [statistics.mean(collData[key])]

        # pprint.pprint(valCount)
    # print(xAxis)
    # print(avgYAxis)
    
    # popt, pcov = curve_fit(funcRSSI, xAxis, avgYAxis)
    # print(popt)

    # print(len(extXAxis))
    # print(len(extYAxis))
    # print(func(xAxis, *popt))

    fig, ax1 = plt.subplots(figsize=(15,5))
    # fig = plt.figure(1, figsize=(10,4))

    ax2 = ax1.twinx()
    ax2.set_ylabel('Distance (m)', fontsize=20, color='g')
    ax2.axis([1, 500, 0.0, 8])
    ax2.tick_params(labelsize=15)

    ax2.plot(xAxis, groundtrueDistList, color='r', lw=3, ls=':', label=f'Ground truth distance ({groundtrueDistKey}m)')
    # ax2.plot(xAxis, originalDistList, 'k--', lw=2, label='Raw-data mapped distance')

    # color='tab:red'
    ax1.set_xlabel('Time Step', fontsize=20)
    ax1.set_ylabel('RSSI (dBm)', fontsize=20, color='b')
    ax1.tick_params(labelsize=15)
    ax1.plot(xAxis, originalRSSIList, color='0.6', lw=3, label='Raw RSSI data')
    ax1.plot(xAxis, filteredRSSIList, 'b-', lw=5, ls='--', label='Smoothed RSSI data')

    ax1.axis([1, 500, -80, -50])

    ax1.tick_params(axis='y', labelcolor='b')


    # color='tab:blue'


    ax2.plot(xAxis, filteredDistList, 'g-', lw=5, label='Smoothed-data mapped distance')

    ax2.tick_params(axis='y', labelcolor='g')

    fig.tight_layout()

    # plt.plot(xAxis, funcRSSI(xAxis, *popt), 'g--', linewidth=5, label='Front:n=%5.3f, a=%5.3f' % tuple(popt))
    # plt.axis([0, 7.5, -92, -60])

    # plt.plot(xAxis, funcRSSI(xAxis, *popt), 'g--', linewidth=5, label='Back:n=%5.3f, a=%5.3f' % tuple(popt))
    # plt.axis([0, 7, -95, -70])

    # plt.scatter(extXAxis, extYAxis, pointSize, color="0.6", label='Raw RSSI data')

    # plt.scatter(xAxis, avgYAxis,label='Average', color="b")
    ax1.legend(loc='upper left',fontsize=20, edgecolor='inherit')
    ax2.legend(loc='upper right',fontsize=20, edgecolor='inherit')
    # plt.legend(loc='best', fontsize=20, handles=[ax1, ax2])
    plt.show()
    fig.savefig('/home/chris/test-d-{}.eps'.format(groundtrueDistKey) )