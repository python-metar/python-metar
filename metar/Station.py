#!/usr/bin/python
#
#  Python module to provide station information from the ICAO identifiers
#
#  Copyright 2004  Tom Pollard
#
import os
from math import sin, cos, atan2, sqrt
from metar.Datatypes import position, distance, direction

class station:
  """An object representing a weather station."""
  
  def __init__( self, id, city=None, state=None, country=None, latitude=None, longitude=None):
    self.id = id
    self.city = city
    self.state = state
    self.country = country
    self.position = position(latitude,longitude)
    if self.state:
      self.name = "%s, %s" % (self.city, self.state)
    else:
      self.name = self.city

current_dir = os.path.dirname(__file__)
station_file_name = os.path.join(current_dir, "nsd_cccc.txt")
station_file_url = "http://www.noaa.gov/nsd_cccc.txt"

stations = {}

fh = open(station_file_name,'r')
for line in fh:
  f = line.strip().split(";")
  stations[f[0]] = station(f[0],f[3],f[4],f[5],f[7],f[8])
fh.close()

if __name__ == "__main__":
  for id in [ 'KEWR', 'KIAD', 'KIWI', 'EKRK' ]:
    print(id, stations[id].name, stations[id].country)

