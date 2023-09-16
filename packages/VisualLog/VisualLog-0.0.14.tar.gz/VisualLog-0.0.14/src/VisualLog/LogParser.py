#!/usr/bin/env python3

import re
import datetime
import os

def defaultLineCallback(lineInfo):
    lineInfoFixed = []

    for index in range(len(lineInfo)):
        lineInfoFixed.append(lineInfo[index])
    
    return lineInfoFixed

def getFiles(path) :
    for (dirpath, dirnames, filenames) in os.walk(path) :
        dirpath = dirpath
        dirnames = dirnames
        filenames = filenames
        return filenames

    return []

def logFileParser(file = None, regex = None , callback=defaultLineCallback, fileEncode = "utf-8"):
    '''
    regex

    * r'(\d+.\d+)\s+:(.*):\s+(\w*):\s*(.*)'
    * r'(\d+)\s+(\d+)\s+(\d+)'
    * r'(\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}\.\d*)\s+\d+\s+\d+\s+\w+\s+(.*)'
    * r'(\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}\.\d*)\s+\d+\s+\d+\s+\w+\s+.*: No longer ignoring proximity \[(\d)\]'
    * r'(\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}\.\d*)\s+\d+\s+\d+\s+\w+\s+Light\s*:\s.*=(\d*),\s*.*=(\d*),\s*.*=(\d*)'
    * r'(Signed image is stored at (.*)|Processing \d*/\d*: (.*))'

    fileEncode: 

    * utf-8
    * ISO-8859-1
    * GB2312
    * gbk
    '''

    if os.path.isdir(file):
        lineInfos = []
        filenames = []
        for f in getFiles(file):
            lineInfos.append(_logFileParser(file + "/" + f, regex, callback, fileEncode))
            filenames.append(f)
        return lineInfos, filenames

    if os.path.isfile(file):
        return _logFileParser(file, regex, callback, fileEncode)

def _regexLineInfo(regex, line, callback, lineInfos):
    foundList = re.search(regex, line.strip(), re.M | re.I)
    if foundList:
        if callback != None:
            ret = callback(foundList.groups())
            if ret != None:
                lineInfos.append(ret)
        else:
            lineInfos.append(defaultLineCallback([s.strip() for s in foundList.groups()]))

def _logFileParser(file = None, regex = None , callback=defaultLineCallback, fileEncode = "utf-8"):
    lineInfos = []

    if file != None and isinstance(file, str) and (regex != None):
        with open(file, mode = "r", encoding = fileEncode) as fd:
            for line in fd:
                if isinstance(regex, list):
                    for item in regex:
                        _regexLineInfo(item, line, callback, lineInfos)
                else:
                    _regexLineInfo(regex, line, callback, lineInfos)
    else:
        return None
    
    return lineInfos

def floatLineCallback(lineInfo):
    lineInfoFixed = []

    for index in range(len(lineInfo)):
        lineInfoFixed.append(float(lineInfo[index]))
    
    return lineInfoFixed

def dateLineCallback(lineInfo, col = 1):
    lineInfoFixed = []
    today_year = str(datetime.date.today().year)

    for index in range(len(lineInfo)):
        if index == 0:
            continue

        if index == col:
            timeString = today_year + "-" + lineInfo[0] + " " + lineInfo[index]
            currentDate = datetime.datetime.strptime(timeString, "%Y-%m-%d %H:%M:%S.%f")
            lineInfoFixed.append(currentDate)
            continue

        lineInfoFixed.append(lineInfo[index])
    
    return lineInfoFixed

if __name__ == "__main__":
    # 298.039308 :    1-swapper/0       : initcall: init_menu    16.019692ms
    # 15932.513576 : 1138-android.bg      : AP_Launch: com.android.settings/.FallbackHome 756ms
    lineInfos = logFileParser("default/Android_Q_bootprof.txt", r'(\d+.\d+)\s+:(.*):\s+(\w*):\s*(.*)')
    for info in lineInfos:
        print(info)

    # 2705    42248   1025
    lineInfos = logFileParser(
            "default/zcv.txt",
            r'(\d+)\s+(\d+)\s+(\d+)',
            callback=floatLineCallback
        )
    for info in lineInfos:
        print(info)

    # 06-29 09:37:46.551252  2283  2283 I DebugLoggerUI/MainActivity: onPause
    lineInfos = logFileParser(
            "default/AndroidSystemWakeup.curf", 
            r'(\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}\.\d*)\s+\d+\s+\d+\s+\w+\s+(.*)',
            callback=dateLineCallback
            )
    for info in lineInfos:
        print(info)
