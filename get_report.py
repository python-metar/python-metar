#!/usr/bin/python
#
import sys
import getopt
import string
import urllib
from metar import Metar

BASE_URL = "http://weather.noaa.gov/pub/data/observations/metar/stations"

def usage():
  program = os.path.basename(sys.argv[0])
  print "Usage: ",program,"<station> [ <station> ... ]"
  print """Options:
  <station> . a four-letter ICAO station code (e.g., "KEWR")
"""
  sys.exit(1)

stations = []
debug = False

try:
  opts, stations = getopt.getopt(sys.argv[1:], 'd')
  for opt in opts:
    if opt[0] == '-d':
      debug = True
except:
  usage()
  
if not stations:
  usage()

for name in stations:
  url = "%s/%s.TXT" % (BASE_URL, name)
  if debug: 
    sys.stderr.write("[ "+url+" ]")
  try:
    urlh = urllib.urlopen(url)
    report = ''
    for line in urlh:
      if line.startswith(name):
        report = line.strip()
        obs = Metar.Metar(line)
        print obs.string()
        break
    if not report:
      print "No data for ",name,"\n\n"
  except Metar.ParserError:
    print "METAR code: ",line
    print string.join(err.args,", "),"\n"
  except:
    print "Error retrieving",name,"data","\n"
 
