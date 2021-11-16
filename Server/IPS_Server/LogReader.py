#!/usr/bin/env python3
import os
import sys


import pprint 

class LogReader:
    """docstring for LogReader"""
    def __init__(self):
        super(LogReader, self).__init__()

    def readFile(self, fileDir):

        dataDict = {}
        with open(fileDir, 'r') as fObj:

            pass
        return dataDict

    def readFileRPI(self, fileName):
        '''
        read rssi data:
        file name e.g., rssidata-0.90.csv
        file format: time, uuid, rssi, seq, e.g., 
        1588056532.6065931,015bc7e7-2a5b-4b4e-9160-53f0d1be2b63,-83,6
        '''

        # fName = fileName.split('-')
        # tagX=float(fName[1])
        # tagY=0.0
        count = 0
        allEles = []
        with open(fileName, 'r') as fObj:
            for line in fObj:
                sLine = line.split(',')
                if sLine[2] and count < 500:
                    count += 1
                    print(sLine[2])
                    allEles.append(float(sLine[2]))                
        # pprint.pprint(allEles)
        return allEles


    def readFileGradient(self, fileName):
        '''
        read rssi data:
        file name e.g., rssidata-0.90.csv
        file format: ap-1, ap-2, ap-3, ap4, e.g., 
        0.116597151 -0.033491162 0.076248051 0.232114196
        '''

        # fName = fileName.split('-')
        # tagX=float(fName[1])
        # tagY=0.0
        count = 0
        allEles = []
        with open(fileName, 'r') as fObj:
            for line in fObj:
                sLine = line.split(',')
                if sLine and count < 300:
                    count += 1
                    allEles.append(sLine)                
        # pprint.pprint(allEles)
        return allEles

    def readFileLocationCore(self, fileDir):

        # print(fileDir)
        fName = fileDir.split('-')
        # print(fName[1][0])
        if fName[1][0] != 'c':
            tagX=float(fName[1])
            tagY=float(fName[2])
        else:
            tagX=0.0
            tagY=0.0

        allEles = []
        with open(fileDir, 'r') as fObj:
            for line in fObj:
                sLine = line.split(' ')
                if 'TIME' in sLine:
                    num = sLine.index('TIME')
                    # print(sLine[num], sLine[num+2])

                elif 'TYPE' in sLine and 'SEQ' in sLine:
                    num = sLine.index('SEQ')
                    # print(sLine[1], sLine[num+2])
                    index = sLine.index('DATA')
                    sEles = sLine[index+2].split(',')
                    sEles = [ele.split('-') for ele in sEles]
                    for ele in sEles:
                        ele[1] = '-'+ele[1]
                        ele[1] = ele[1].strip('\n')
                        ele.append(sLine[num+2])

                    # sEles.append(sLine[num+2])
                    dataDict = {}
                    tagInfo = []
                    tagInfo.append(sLine[1])
                    tagInfo.append([tagX, tagY])

                    dataDict['tag'] = tagInfo
                    # dataDict['seq'] = sLine[num+2]
                    dataDict['apid-rssi-seq'] = sEles
                    # sEles.insert(0, sLine[1])
                    
                    allEles.append(dataDict)
                    # print(dataDict)
        # pprint.pprint(allEles)
        return allEles

    def readFolder(self, folderDir):
        caliData = {}
        # scan the directory to read every data point
        for root, dirs, files in os.walk(folderDir):
            # print(root, files)
            for filename in files:
                # filename e.g.: LocationCore.log.2020-02-13-,c-32-b-1.2,.log
                fnSplitList = filename.split(',')
                fnInfoList = fnSplitList[1].split('-')

                apId = fnInfoList[1]
                dist = fnInfoList[3]

                data = self.readFileLocationCore(root+filename)

                caliData[apId+','+dist] = data

        return caliData

    def readFolderRPI(self, folderDir):
        '''
        file name e.g., rssidata-0.90.csv
        '''
        caliData = {}
        # scan the directory to read every data point
        for root, dirs, files in os.walk(folderDir):
            # print(root, files)
            for filename in files:
                # filename e.g.: rssidata-0.90.csv
                fnSplitList = filename.split('-')
                # fnInfoList = fnSplitList[1].split('-')

                # apId = '1'
                # fnSplitList[1].split('.')[0]
                dist = fnSplitList[1].split('.')[0]+'.'+fnSplitList[1].split('.')[1]
                # print(root+filename)
                data = self.readFileRPI(root+filename)

                caliData[dist] = data

        return caliData

    def processData(self, inData):
        pass

