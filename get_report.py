#!/usr/bin/python
#
from __future__ import print_function

import os
import sys
import getopt
import string

try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen
from metar import Metar

BASE_URL = "http://tgftp.nws.noaa.gov/data/observations/metar/stations"


def usage():
    program = os.path.basename(sys.argv[0])
    print("Usage: ", program, "<station> [ <station> ... ]")
    print(
        """Options:
    <station> . a four-letter ICAO station code (e.g., "KEWR")
  """
    )
    sys.exit(1)


stations = []
debug = False

try:
    opts, stations = getopt.getopt(sys.argv[1:], "d")
    for opt in opts:
        if opt[0] == "-d":
            debug = True
except:
    usage()

if not stations:
    usage()

for name in stations:
    url = "%s/%s.TXT" % (BASE_URL, name)
    if debug:
        sys.stderr.write("[ " + url + " ]")
    try:
        urlh = urlopen(url)
        report = ""
        for line in urlh:
            if not isinstance(line, str):
                line = line.decode()  # convert Python3 bytes buffer to string
            if line.startswith(name):
                report = line.strip()
                obs = Metar.Metar(line)
                print(obs.string())
                break
        if not report:
            print("No data for ", name, "\n\n")
    except Metar.ParserError as exc:
        print("METAR code: ", line)
        print(string.join(exc.args, ", "), "\n")
    except:
        import traceback

        print(traceback.format_exc())
        print("Error retrieving", name, "data", "\n")
