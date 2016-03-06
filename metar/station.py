#!/usr/bin/python
#
#  Python module to provide station information from the ICAO identifiers
#
#  Copyright 2004  Tom Pollard

from pkg_resources import resource_filename
from .datatypes import position


class Station:
  """An object representing a weather station."""

  def __init__(self, sta_id, city=None, state=None, country=None, latitude=None, longitude=None):
    self.sta_id = sta_id
    self.city = city
    self.state = state
    self.country = country
    self.position = position(latitude,longitude)
    if self.state:
      self.name = "%s, %s" % (self.city, self.state)
    else:
      self.name = self.city


station_file_name = resource_filename("metar", "nsd_cccc.txt")
station_file_url = "http://www.noaa.gov/nsd_cccc.txt"

stations = {}

fh = open(station_file_name,'r')
for line in fh:
  f = line.strip().split(";")
  stations[f[0]] = Station(f[0],f[3],f[4],f[5],f[7],f[8])
fh.close()

if __name__ == "__main__":
  for sta_id in [ 'KEWR', 'KIAD', 'KIWI', 'EKRK' ]:
    print(sta_id, stations[sta_id].name, stations[sat_id].country)
