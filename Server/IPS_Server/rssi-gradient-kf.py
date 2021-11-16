#!/home/chris/anaconda3/bin/python
##!/usr/bin/env python3

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
        dist = key.split(',')[1]
        collData[dist]=val   
    
    return collData

# def proGradientData(logData):
#     collData = {}
#     for key in logData.items():
#         # apId = key.split(',')[0]
#         dist = key.split(',')[1]
#         collData[dist]=val   
    
#     return collData

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

def sortData(x=[], y=[], errorbar=[], label=[]):
    # print(label, y, x, errorbar)

    # boxplot
    labelY=zip(label, y)
    sDataWLabel=sorted(labelY)
    label = [ele1 for ele1, ele2 in sDataWLabel]
    retY = [ele2 for ele1, ele2 in sDataWLabel]
    retX = []
    errbar = []

    if not retY:
        print("ERROR: empty retY.")
        sys.exit()
    # sDataWLabel=sorted(labelY)
    # print(sDataWLabel)

    return retX, retY, errbar, label

# this is the main entry point of this script
if __name__ == "__main__":

    args = parseArgments().parse_args()

    # load RSSI log data
    logData = {}
    reader = LogReader()

    filePath = args.path
    logData = reader.readFileGradient(fileName=filePath[0])

    # name=['ap12', 'ap3', 'ap6', 'ap9']
    name=['AP3', 'AP1', 'AP4', 'AP2']

    count = 0
    color=['k', 'r', 'b', 'g']
    colorOri=['k--', 'r--', 'b--', 'g--']

    originalTotal=[]
    filteredTotal=[]
    # fig=plt.figure()
    # ax1=fig.add_subplot(1, 1, 1)
    fig, ax1 = plt.subplots(1, 1, figsize=(15, 6))

    xx, yy, err, label = sortData(y=logData, label=name)

    for x in yy:
        beacon = Beacon()
        originalRSSIList=[]
        filteredRSSIList=[]     
        for value in x:
            originalRSSIList.append(float(value))
            # originalDistList.append(beacon.rssi2dist(float(value)))
            beacon.rssi = float(value)
            beacon.lastSeq = 1
            beacon.rssiHis.append(float(value))
            filteredRSSI = beacon.applyMA()
            #[j] filteredRSSI = beacon.applyKF4Rssi()
            # filteredRSSI = beacon.applyAvgRssi()
            # print(filteredRSSI)        
            filteredRSSIList.append(filteredRSSI)
            # filteredDistList.append(beacon.rssi2dist(filteredRSSI))
            # groundtrueDistList.append(float(groundtrueDistKey))
            # xAxis.append(count)
            # count += 1
        filteredTotal.append(filteredRSSIList)
        originalTotal.append(originalRSSIList)
        
        xAxis=np.linspace(1,len(filteredTotal[0]),len(filteredTotal[0]))

        # fig, ax1 = plt.subplots(figsize=(15,6))
        # fig = plt.figure(1, figsize=(10,4))

        # color='tab:red'
        # plt.set_xlabel('Time Step', fontsize=20)
        # plt.set_ylabel('Gradient', fontsize=20, color='b')

        ax1.plot(xAxis, originalRSSIList, colorOri[count], lw=3,label=f'RSS of {label[count]}')

        ax1.plot(xAxis, filteredRSSIList, color[count], lw=5, label=f'Filtered RSS of {label[count]}')

        # ax1.tick_params(axis='y', labelcolor='b')
        
        count+=1

    ax1.axis([1, len(filteredTotal[0]), -90, -50])

    ax1.set_xlabel('Time Step', size=15)		
    ax1.set_ylabel('RSS (dBm)', size=15)
    ax1.minorticks_on()
    ax1.tick_params(labelsize=15)
    ax1.legend(loc='best', fontsize=15, edgecolor='inherit')
    plt.grid(True)
    # fig1.tight_layout()
    plt.tight_layout()
    plt.show()
    fig.savefig('/home/chris/Figures/motion-ori-kf-rssi.eps')
