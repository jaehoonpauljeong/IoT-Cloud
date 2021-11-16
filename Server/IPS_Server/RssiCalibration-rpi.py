#!/usr/bin/env python3

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

from LogReader import LogReader

def parseArgments():
	parser = argparse.ArgumentParser(description='Specify log data path.')
	parser.add_argument('--path', type=str, nargs=1, help='Log data path')	

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
        dist = key
        # collData[dist] = []
        # pprint.pprint(val)
        # localYData = []
        # for ele in val:
        #     if 'apid-rssi-seq' in ele:
        #         # print(ele['apid-rssi-seq'])
        #         for data in ele['apid-rssi-seq']:
        #             if apId == data[0][len(data[0])-2:]:
        #                 localYData.append(float(data[1]))
        # print(localYData)
        collData[dist]=val   
    
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

    collData = proCaliData(logData)
    # print(collData)
    print(sorted(collData))

    # collData, key: distance, value: [rssi list]
    # sys.exit()

    xAxis=[float(i) for i in sorted(collData)]
    avgYAxis = []

    extXAxis = []
    extYAxis = []
    pointSize = []
    for key in sorted(collData):
        valCount = {}
        for ele in collData[key]:
            if ele not in valCount:
                valCount[ele] = 1
            else:
                valCount[ele] += 1

        extXAxis += [key] * len(valCount.keys())
        extYAxis += [i for i in valCount.keys()]
        pointSize += [i*2.5 for i in valCount.values()]

        # mean y
        avgYAxis += [statistics.mean(collData[key])]

        # pprint.pprint(valCount)
    print(xAxis)
    print(avgYAxis)
    
    popt, pcov = curve_fit(funcRSSI, xAxis, avgYAxis)
    print(popt)

    # print(len(extXAxis))
    # print(len(extYAxis))
    # print(func(xAxis, *popt))
    fig = plt.figure(1, figsize=(10,7))

    # plt.plot(xAxis, funcRSSI(xAxis, *popt), 'g--', linewidth=5, label='Front:n=%5.3f, a=%5.3f' % tuple(popt))
    # plt.axis([0, 7.5, -92, -60])

    plt.plot(xAxis, funcRSSI(xAxis, *popt), 'g--', linewidth=5, label='Front:n=%5.3f, a=%5.3f' % tuple(popt))
    plt.axis([0, 7, -90, -50])

    plt.scatter(extXAxis, extYAxis, pointSize, color="0.6", label='Raw RSSI data')
    plt.xlabel('Distance (m)', fontsize=20)
    plt.ylabel('RSSI (dBm)', fontsize=20)

    plt.scatter(xAxis, avgYAxis,label='Average', color="b")

    plt.legend(loc='best',fontsize=20)
    plt.show()
    fig.savefig('/home/chris/test.eps')