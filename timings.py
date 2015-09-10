import sys
import re

file = open(sys.argv[1], 'r')
threshold = int(sys.argv[2])

totalSampleCount = 0
includeSampleCount = 0

for line in file:
    matchObj = re.match( r'\[\d+ +- +(\d+) *]us +\|#* +- +(\d+).*', line)
    if matchObj:
        totalSampleCount += int(matchObj.group(2))
        if int(matchObj.group(1)) < threshold:
            includeSampleCount += int(matchObj.group(2))
print("%d %d %.3f\n" % (includeSampleCount,totalSampleCount,float(includeSampleCount)/float(totalSampleCount)))
