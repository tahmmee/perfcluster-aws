#!/usr/bin/env python
import sys
import re

file = open(sys.argv[1], 'r')
threshold = int(sys.argv[2])

totalSampleCount = 0
includeSampleCount = 0

for line in file:
    matchObj = re.match( r'\[\d+ +- +(\d+) *]us +\|#* +- +(\d+).*', line)
    if matchObj:
        sample = int(matchObj.group(2))
        totalSampleCount += sample
        if int(matchObj.group(1)) < threshold:
            includeSampleCount += sample

    matchObj = re.match( r'\[\d+ +- +(\d+) *]ms +\|#* +- +(\d+).*', line)
    if matchObj:
        sample = int(matchObj.group(2))
        totalSampleCount += sample
        if (int(matchObj.group(1)))*1000 < threshold:
            includeSampleCount += sample


print("%d %d %.3f\n" % (includeSampleCount,totalSampleCount,float(includeSampleCount)/float(totalSampleCount)))
