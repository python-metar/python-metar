#!/usr/bin/env python
#
#  This is a minimal sample script showing how the individual data
#  are accessed from the decoded report.  To produce the standard text 
#  summary of a report, the string() method of the Metar object.
#
#  The parsed data are stored as attributes of a Metar object.
#  Individual attributes are either strings. instances of one of the
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
#
#    press_sea_level  sea-level pressure [pressure]
#    wind_speed_peak  peak wind speed in last hour [speed]
#    wind_dir_peak    direction of peak wind speed in last hour [direction]
#    max_temp_6hr     max temp in last 6 hours [temperature]
#    min_temp_6hr     min temp in last 6 hours [temperature]
#    max_temp_24hr    max temp in last 24 hours [temperature]
#    min_temp_24hr    min temp in last 24 hours [temperature]
#    precip_1hr       precipitation over the last hour [precipitation]
#    precip_3hr       precipitation over the last 3 hours [precipitation]
#    precip_6hr       precipitation over the last 6 hours [precipitation]
#    precip_24hr      precipitation over the last 24 hours [precipitation]
#
#    _remarks         remarks [list of strings]
#    _unparsed        unparsed remarks [list of strings]
#
#  The metar.Datatypes classes (temperature, pressure, precipitation,
#  speed, direction) describe an observation and its units.  They provide
#  value() and string() methods to that return numerical and string
#  representations of the data in any of a number of supported units.  
# 
#  (You're going to have to study the source code for more details,
#  like the available methods and supported unit conversions for the
#  metar.Datatypes objects, etc..)  

#  In particular, look at the Metar.string()
#  method, and the functions it calls.  
#
#  Feb 4, 2005 
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

# The wind() method returns a string describing wind observations
# which may include speed, direction, variability and gusts.
if obs.wind_speed:
  print "wind: %s" % obs.wind()

# The peak_wind() method returns a string describing the peak wind 
# speed and direction.
if obs.wind_speed_peak:
  print "wind: %s" % obs.peak_wind()

# The visibility() method summarizes the visibility observation.
if obs.vis:
  print "visibility: %s" % obs.visibility()

# The runway_visual_range() method summarizes the runway visibility
# observations.
if obs.runway:
  print "visual range: %s" % obs.runway_visual_range()

# The 'press' attribute is a pressure object.
if obs.press:
  print "pressure: %s" % obs.press.string("mb")

# The 'precip_1hr' attribute is a precipitation object.
if obs.precip_1hr:
  print "precipitation: %s" % obs.precip_1hr.string("in")

# The present_weather() method summarizes the weather description (rain, etc.)
print "weather: %s" % obs.present_weather()

# The sky_conditions() method summarizes the cloud-cover observations.
print "sky: %s" % obs.sky_conditions("\n     ")

# The remarks() method describes the remark groups that were parsed, but 
# are not available directly as Metar attributes.  The precipitation, 
# min/max temperature and peak wind remarks, for instance, are stored as
# attributes and won't be listed here.
if obs._remarks:
  print "remarks:"
  print "- "+obs.remarks("\n- ")

print "-----------------------------------------------------------------------\n"
