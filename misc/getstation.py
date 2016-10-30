#!/usr/bin/python
#
import os
import sys
import getopt
import datetime
import urllib

BASE_URL = "http://tgftp.nws.noaa.gov/data/observations/metar/stations"

def usage():
  print "Usage:  $0 "
def usage():
  program = os.path.basename(sys.argv[0])
  print "Usage: ",program,"[-p] <station> [ <station> ... ]"
  print """Options:
  <station> . a four-letter ICAO station code (e.g., "KEWR")
  -p ........ send downloaded data to stdout, ratherthan a file.
"""
  sys.exit(1)

today = datetime.datetime.utcnow()

stations = []
pipe = False
debug = False

try:
  opts, stations = getopt.getopt(sys.argv[1:], 'dp')
  for opt in opts:
    if opt[0] == '-p':
      pipe = True
    elif opt[0] == '-d':
      debug = True
except:
  usage()
  
if not stations:
  usage()

for name in stations:
  url = "%s/%s.TXT" % (BASE_URL, name)
  if debug: sys.stderr.write("[ "+url+" ]")
  try:
    urlh = urllib.urlopen(url)
    for line in urlh:
      if line.startswith(name):
        report = line.strip()
        groups = report.split()
        if groups[1].endswith('Z'):
          date_str = "%02d%02d%s-%s" % (today.year-2000, today.month, 
                                    groups[1][:2], groups[1][2:])
        else:
          date_str = "%02d%02d%02d-%02d%02dZ" % (today.year-2000, 
                             today.month, today.day, today.hour, today.minute)
        break
  except:
    print "Error retrieving",name,"data"
    continue
  if pipe:
    print report+"\n"
  else:
    file = "%s-%s.metar" % (name,date_str)
    print "Saving current METAR report for station",name,"in",file
    fileh = open(file,'w')
    fileh.write(report+"\n")
    fileh.close()
