#!/usr/bin/env python
#
#  This is a minimal sample script showing how the individual data
#  are accessed from the decoded report.  
#
#  The parsed data are stored as attributes of a Metar object.
#  Indiviual attributes are either strings. instances of one of the
#  metar.Datatypes classes, or lists of tuples of these scalars.
#  Here's a summary, adapted from the comments in the Metar.Metar.__init__()
#  method:
# 
#    Attribute       Comments [data type]
#    --------------  --------------------
#    code             original METAR code [string]
#    type             METAR (routine) or SPECI (special) [string]
#    mod              AUTO (automatic) or COR (corrected) [string]
#    station_id       4-character ICAO station code [string]
#    time             observation time [datetime]
#    cycle            observation cycle (0-23) [int]
#    wind_dir         wind direction [direction]
#    wind_speed       wind speed [speed]
#    wind_gust        wind gust speed [speed]
#    wind_dir_from    beginning of range for win dir [direction]
#    wind_dir_to      end of range for wind dir [direction]
#    vis              visibility [distance]
#    vis_dir          visibility direction [direction]
#    max_vis          visibility [distance]
#    max_vis_dir      visibility direction [direction]
#    temp             temperature (C) [temperature]
#    dewpt            dew point (C) [temperature]
#    press            barometric pressure [pressure]
#    runway           runway visibility [list of tuples...]
#                        name [string]
#                        low  [distance]
#                        high [distance]
#    weather          present weather [list of tuples...]
#                        intensity     [string]
#                        description   [string]
#                        precipitation [string]
#                        obscuration   [string]
#                        other         [string]
#    recent           recent weather [list of tuples...]
#    sky              sky conditions [list of tuples...]
#                        cover   [string]
#                        height  [distance]
#                        cloud   [string]
#    windshear        runways w/ wind shear [list of strings]
#    _remarks         remarks [list of strings]
#    _unparsed        unparsed remarks [list of strings]
# 
#  (You're going to have to study the source code for more details,
#  like the available methods and supported unit conversions for the
#  metar.Datatypes objects, etc..)
#
#  Jan 25, 2005
#  Tom Pollard 
#
from metar import Metar

# A sample METAR report
code = "METAR KEWR 111851Z VRB03G19KT 2SM R04R/3000VP6000FT TSRA BR FEW015 BKN040CB BKN065 OVC200 22/22 A2987 RMK AO2 PK WND 29028/1817 WSHFT 1812 TSB05RAB22 SLP114 FRQ LTGICCCCG TS OHD AND NW-N-E MOV NE P0013 T02270215"

print "-----------------------------------------------------------------------"
print "METAR: ",code
print "-----------------------------------------------------------------------"

# Initialize a Metar object with the coded report
obs = Metar.Metar(code)

# Print the individual data

# The 'station_id' attribute is a string.
print "station: %s" % obs.station_id

if obs.type:
  print "type: %s" % obs.report_type()

# The 'time' attribute is a datetime object
if obs.time:
  print "time: %s" % obs.time.ctime()

# The 'temp' and 'dewpt' attributes are temperature objects
if obs.temp:
  print "temperature: %s" % obs.temp.string("C")

if obs.dewpt:
  print "dew point: %s" % obs.dewpt.string("C")

# The wind() method returns a string describing wind speed and direction
if obs.wind_speed:
  print "wind: %s" % obs.wind()

# The 'vis' attribute is a distance object
# 
if obs.vis:
  print "visibility: %s" % obs.visibility()

if obs.runway:
  print "visual range: %s" % obs.runway_visual_range()

if obs.press:
  print "pressure: %s" % obs.press.string("mb")

print "weather: %s" % obs.present_weather()

print "sky: %s" % obs.sky_conditions("\n     ")

if obs._remarks:
  print "remarks:"
  print "- "+obs.remarks("\n- ")

print "-----------------------------------------------------------------------\n"
