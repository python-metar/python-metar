#!/usr/bin/env python
#
#  A python package for interpreting METAR and SPECI weather reports.
#  
#  US conventions for METAR/SPECI reports are described in chapter 12 of
#  the Federal Meteorological Handbook No.1. (FMH-1 1995), issued by NOAA. 
#  See <http://metar.noaa.gov/>
# 
#  International conventions for the METAR and SPECI codes are specified in 
#  the WMO Manual on Codes, vol I.1, Part A (WMO-306 I.i.A).  
#
#  This module handles a reports that follow the US conventions, as well
#  the more general encodings in the WMO spec.  Other regional conventions
#  are not supported at present.
#
#  The current METAR report for a given station is available at the URL
#  http://weather.noaa.gov/pub/data/observations/metar/stations/<station>.TXT
#  where <station> is the four-letter ICAO station code.  
#
#  The METAR reports for all reporting stations for any "cycle" (i.e., hour) 
#  in the last 24 hours is available in a single file at the URL
#  http://weather.noaa.gov/pub/data/observations/metar/cycles/<cycle>Z.TXT
#  where <cycle> is a 2-digit cycle number (e.g., "00", "05" or "23").  
# 
#  Copyright 2004  Tom Pollard
# 
__author__ = "Tom Pollard"

__email__ = "pollard@alum.mit.edu"

__version__ = "1.2"

__doc__ = """metar v%s (c) 2004, %s

Metar is a python package that interprets coded METAR and SPECI weather reports.

Please e-mail bug reports to: %s""" % (__version__, __author__,__email__)

__LICENSE__ = """
Copyright (c) 2004, %s
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""" % __author__

"""
This module defines the Metar class.  A Metar object represents 
the weather report encoded by a single METAR code.
"""
import re
import datetime
import string
from Datatypes import *

## Exceptions

class ParserError(Exception):
  """Exception raised when an unparseable group is found in body of the report."""
  pass

## regular expressions to decode various groups of the METAR code

TYPE_RE =     re.compile(r"^(?P<type>METAR|SPECI)\s+")
STATION_RE =  re.compile(r"^(?P<station>[A-Z][A-Z0-9]{3})\s+")
TIME_RE = re.compile(r"""^(?P<day>\d\d)
                          (?P<hour>\d\d)
                          (?P<min>\d\d)Z?\s+""",
                     re.VERBOSE)
MODIFIER_RE = re.compile(r"^(?P<mod>AUTO|FINO|NIL|TEST|CORR?|RTD|CC[A-G])\s+")
WIND_RE = re.compile(r"""^(?P<dir>[\dO]{3}|[0O]|///|VRB)
                          (?P<speed>P?[\dO]{2,3}|[0O]+|//)
                        (G(?P<gust>P?\d\d\d?))?
                          (?P<units>KTS?|LT|K|T|KMH|MPS)?
                      (\s+(?P<varfrom>\d\d\d)V
                          (?P<varto>\d\d\d))?\s+""",
                     re.VERBOSE)
VISIBILITY_RE =   re.compile(r"""^(?P<vis>(?P<dist>M?(\d\s+)?\d/\d\d?|M?\d+)
                                          ( (\s*(?P<units>SM|KM|M|U))? | 
                                            (?P<dir>[NSEW][EW]?)? ) |
                                          CAVOK )\s+""",
                             re.VERBOSE)
RUNWAY_RE = re.compile(r"""^(RVRNO | 
                            R(?P<name>\d\d(RR?|LL?|C)?)/
                             (?P<low>(M|P)?\d\d\d\d)
                           (V(?P<high>(M|P)?\d\d\d\d))?
                            (?P<unit>FT)?[/NDU]*)\s+""",
                       re.VERBOSE)
WEATHER_RE = re.compile(r"""^(?P<int>(-|\+|VC)*)
                             (?P<desc>(MI|PR|BC|DR|BL|SH|TS|FZ)+)?
                             (?P<prec>(DZ|RA|SN|SG|IC|PL|GR|GS|UP|//)*)
                             (?P<obsc>BR|FG|FU|VA|DU|SA|HZ|PY)?
                             (?P<other>PO|SQ|FC|SS|DS|NSW)?
                             (?P<int2>[-+])?\s+""",
                        re.VERBOSE)
SKY_RE= re.compile(r"""^(?P<cover>VV|CLR|SKC|SCK|NSC|NCD|BKN|SCT|FEW|[O0]VC|///)
                        (?P<height>[\dO]{2,4}|///)?
                        (?P<cloud>([A-Z][A-Z]+|///))?\s+""",
                   re.VERBOSE)
TEMP_RE = re.compile(r"""^(?P<temp>(M|-)?\d+|//|XX|MM)/
                          (?P<dewpt>(M|-)?\d+|//|XX|MM)?\s+""",
                     re.VERBOSE)
PRESS_RE = re.compile(r"""^(?P<unit>A|Q|QNH|SLP)?
                           (?P<press>[\dO]{3,4}|////)
                           (?P<unit2>INS)?\s+""",
                      re.VERBOSE)
RECENT_RE = re.compile(r"""^RE(?P<desc>MI|PR|BC|DR|BL|SH|TS|FZ)?
                              (?P<prec>(DZ|RA|SN|SG|IC|PL|GR|GS|UP)*)?
                              (?P<obsc>BR|FG|FU|VA|DU|SA|HZ|PY)?
                              (?P<other>PO|SQ|FC|SS|DS)?\s+""",
                        re.VERBOSE)
WINDSHEAR_RE = re.compile(r"^(WS\s+)?(ALL\s+RWY|RWY(?P<name>\d\d(RR?|L?|C)?))\s+")
COLOR_RE = re.compile(r"""^(BLACK)?(BLU|GRN|WHT|RED)\+?
                        (/?(BLACK)?(BLU|GRN|WHT|RED)\+?)*\s*""",
                             re.VERBOSE)
TREND_RE = re.compile(r"^(?P<trend>TEMPO|BECMG|FCST|NOSIG)\s+")

REMARK_RE = re.compile(r"^(RMKS?|NOSPECI|NOSIG)\s+")

## regular expressions for remark groups

AUTO_RE = re.compile(r"^AO(?P<type>\d)\s+")
SEALVL_PRESS_RE = re.compile(r"^SLP(?P<press>\d\d\d)\s+")
PEAK_WIND_RE = re.compile(r"""^P[A-Z]\s+WND\s+
                             (?P<dir>\d\d\d)
                             (?P<speed>P?\d\d\d?)/
                             (?P<hour>\d\d)?
                             (?P<min>\d\d)\s+""",
                        re.VERBOSE)
WIND_SHIFT_RE = re.compile(r"""^WSHFT\s+
                              (?P<hour>\d\d)?
                              (?P<min>\d\d)
                          (\s+(?P<front>FROPA))?\s+""",
                           re.VERBOSE)
PRECIP_1HR_RE = re.compile(r"^P(?P<precip>\d\d\d\d)\s+")
PRECIP_24HR_RE = re.compile(r"""^(?P<type>6|7)
                                 (?P<precip>\d\d\d\d)\s+""",
                            re.VERBOSE)
PRESS_3HR_RE = re.compile(r"""^5(?P<tend>[0-8])
                                (?P<press>\d\d\d)\s+""",
                            re.VERBOSE)
TEMP_1HR_RE = re.compile(r"""^T(?P<tsign>0|1)
                               (?P<temp>\d\d\d)
                              ((?P<dsign>0|1)
                               (?P<dewpt>\d\d\d))?\s+""",
                          re.VERBOSE)
TEMP_6HR_RE = re.compile(r"""^(?P<type>1|2)
                              (?P<sign>0|1)
                              (?P<temp>\d\d\d)\s+""",
                          re.VERBOSE)
TEMP_24HR_RE = re.compile(r"""^4(?P<smaxt>0|1)
                                (?P<maxt>\d\d\d)
                                (?P<smint>0|1)
                                (?P<mint>\d\d\d)\s+""",
                          re.VERBOSE)
UNPARSED_RE = re.compile(r"(?P<group>\S+)\s+")

LIGHTNING_RE = re.compile(r"""^((?P<freq>OCNL|FRQ|CONS)\s+)?
                             LTG(?P<type>(IC|CC|CG|CA)*)
                           ( \s+(?P<loc>( OHD | VC | DSNT\s+ | \s+AND\s+ | 
                                          [NSEW][EW]? (-[NSEW][EW]?)* )+) )?\s+""",
                          re.VERBOSE)
                          
TS_LOC_RE = re.compile(r"""TS(\s+(?P<loc>( OHD | VC | DSNT\s+ | \s+AND\s+ | 
                                          [NSEW][EW]? (-[NSEW][EW]?)* )+))?
                      ( \s+MOV\s+(?P<dir>[NSEW][EW]?) )?\s+""",
                       re.VERBOSE)

## translation of weather location codes

loc_terms = [ ("OHD", "overhead"), 
              ("DSNT", "distant"),
              ("AND", "and"),
              ("VC", "nearby" ) ]
              
def xlate_loc( loc ):
  """Substitute English terms for the location codes in the given string."""
  for code, english in loc_terms:
    loc = loc.replace(code,english)
  return loc
  
## translation of the sky-condition codes into english

SKY_COVER = { "SKC":"clear",
              "CLR":"clear",
              "NSC":"clear",
              "NCD":"clear",
              "FEW":"a few ",
              "SCT":"scattered ",
              "BKN":"broken ",
              "OVC":"overcast",
              "///":"",
              "VV":"indefinite ceiling" }
              
CLOUD_TYPE = { "TCU":"towering cumulus",
               "CU":"cumulus",
               "CB":"cumulonimbus",
               "SC":"stratocumulus",
               "CBMAM":"cumulonimbus mammatus",
               "ACC":"altocumulus castellanus",
               "SCSL":"standing lenticular stratocumulus",
               "CCSL":"standing lenticular cirrocumulus",
               "ACSL":"standing lenticular altocumulus" }
                
## translation of the present-weather codes into english

WEATHER_INT = { "-":"light", 
                "+":"heavy", 
                "-VC":"nearby light", 
                "+VC":"nearby heavy", 
                "VC":"nearby" }
WEATHER_DESC = { "MI":"shallow",
                 "PR":"partial",
                 "BC":"patches of", 
                 "DR":"low drifting", 
                 "BL":"blowing",
                 "SH":"showers",
                 "TS":"thunderstorm",
                 "FZ":"freezing" }
WEATHER_PREC = { "DZ":"drizzle",
                 "RA":"rain",
                 "SN":"snow",
                 "SG":"snow grains",
                 "IC":"ice crystals",
                 "PL":"ice pellets",
                 "GR":"hail",
                 "GS":"snow pellets",
                 "UP":"unknown precipitation",
                 "//":"" }
WEATHER_OBSC = { "BR":"mist",
                 "FG":"fog",
                 "FU":"smoke",
                 "VA":"volcanic ash",
                 "DU":"dust",
                 "SA":"sand",
                 "HZ":"haze",
                 "PY":"spray" }
WEATHER_OTHER = { "PO":"sand whirls",
                  "SQ":"squalls",
                  "FC":"funnel cloud",
                  "SS":"sandstorm",
                  "DS":"dust storm" }

WEATHER_SPECIAL = { "+FC":"tornado" }

COLOR = { "BLU":"blue",
          "GRN":"green",
          "WHT":"white" }
          
## translation of various remark codes into English
        
PRESSURE_TENDENCY = { "0":"increasing, then decreasing",
                      "1":"increasing more slowly",
                      "2":"increasing",        
                      "3":"increasing more quickly",
                      "4":"steady",
                      "5":"decreasing, then increasing",
                      "6":"decreasing more slowly",
                      "7":"decreasing",
                      "8":"decreasing more quickly" }

LIGHTNING_FREQUENCY = { "OCNL":"occasional",
                        "FRQ":"frequent",
                        "CONS":"constant" }
LIGHTNING_TYPE = { "IC":"intracloud",
                   "CC":"cloud-to-cloud",
                   "CG":"cloud-to-ground",
                   "CA":"cloud-to-air" }

REPORT_TYPE = { "METAR":"routine report",
                "SPECI":"special report",
                "AUTO":"automatic report",
                "COR":"manually corrected report" }
    
## METAR report objects

debug = False

def _report_match(parser,match):
  """Report success or failure of the given parser function. (DEBUG)"""
  if match:
    print parser.__name__," matched '"+match+"'"
  else:
    print parser.__name__," didn't match..."

class Metar(object):
  """METAR (aviation meteorology report)"""
  
  def __init__( self, metarcode, month=None, year=None, utcdelta=None):
    """Parse raw METAR code."""
    self.code = metarcode              # original METAR code
    self.type = 'METAR'                # METAR (routine) or SPECI (special)
    self.mod = "AUTO"                  # AUTO (automatic) or COR (corrected)
    self.station_id = None             # 4-character ICAO station code
    self.time = None                   # observation time [datetime]
    self.cycle = None                  # observation cycle (0-23) [int]
    self.wind_dir = None               # wind direction [direction]
    self.wind_speed = None             # wind speed [speed]
    self.wind_gust = None              # wind gust speed [speed]
    self.wind_dir_from = None          # beginning of range for win dir [direction]
    self.wind_dir_to = None            # end of range for wind dir [direction]
    self.vis = None                    # visibility [distance]
    self.vis_dir = None                # visibility direction [direction]
    self.max_vis = None                # visibility [distance]
    self.max_vis_dir = None            # visibility direction [direction]
    self.temp = None                   # temperature (C) [temperature]
    self.dewpt = None                  # dew point (C) [temperature]
    self.press = None                  # barometric pressure [pressure]
    self.runway = []                   # runway visibility (list of tuples)
    self.weather = []                  # present weather (list of tuples)
    self.recent = []                   # recent weather (list of tuples)
    self.sky = []                      # sky conditions (list of tuples)
    self.windshear = []                # runways w/ wind shear (list of strings)
    self.wind_speed_peak = None        # peak wind speed in last hour
    self.wind_dir_peak = None          # direction of peak wind speed in last hour
    self.max_temp_6hr = None           # max temp in last 6 hours
    self.min_temp_6hr = None           # min temp in last 6 hours
    self.max_temp_24hr = None          # max temp in last 24 hours
    self.min_temp_24hr = None          # min temp in last 24 hours
    self.press_sea_level = None        # sea-level pressure
    self.precip_1hr = None             # precipitation over the last hour
    self.precip_3hr = None             # precipitation over the last 3 hours
    self.precip_6hr = None             # precipitation over the last 6 hours
    self.precip_24hr = None            # precipitation over the last 24 hours
    self._remarks = []                 # remarks (list of strings)
    self._unparsed = []
    
    # Assume report is for the current month, unless otherwise specified.
    # (the year and month are implicit in METAR reports)    
    
    self._now = datetime.datetime.utcnow()
    
    if utcdelta:
      self._utcdelta = utcdelta
    else:
      self._utcdelta = datetime.datetime.now() - self._now
    
    if month:
      self._month = month
    else:
      self._month = self._now.month
    
    if year:
      self._year = year
    else:
      self._year = self._now.year
    
    code = self.code+" "    # (the regexps all expect trailing spaces...)
    try:
      for pattern, parser, repeatable in Metar.parsers:
        if debug: print parser.__name__,":",code
        m = pattern.match(code)
        while m:
          if debug: _report_match(parser,m.group())
          parser(self,m.groupdict())
          code = code[m.end():]
          if not repeatable: break
          if debug: print parser.__name__,":",code
          m = pattern.match(code)
    except Exception, err:
      raise ParserError(parser.__name__+" failed while parsing '"+code+"'\n"+string.join(err.args))
      raise err

    m = REMARK_RE.match(code)
    if m:
      code = code[m.end():]
    if m or self.press:
      while code:
        for pattern, parser in Metar.remark_parsers:
          if debug: print parser.__name__,":",code
          m = pattern.match(code)
          if m:
            if debug: _report_match(parser,m.group())
            parser(self,m.groupdict())
            code = pattern.sub("",code,1)
            break
    elif code and self.mod != 'NO DATA':
      raise ParserError("Unparsed groups in body: "+code)
          
  def _parseType( self, d ):
    """
    Parse the code-type group.
    
    The following attributes are set:
      type   [string]
    """
    self.type = d['type'] 
      
  def _parseStation( self, d ):
    """
    Parse the station id group.
    
    The following attributes are set:
      station_id   [string]
    """
    self.station_id = d['station'] 
      
  def _parseModifier( self, d ):
    """
    Parse the report-modifier group.
    
    The following attributes are set:
      mod   [string]
    """
    mod = d['mod'] 
    if mod == 'CORR': mod = 'COR'
    if mod == 'NIL' or mod == 'FINO': mod = 'NO DATA'
    self.mod = mod
              
  def _parseTime( self, d ):
    """
    Parse the observation-time group.
    
    The following attributes are set:
      time   [datetime]
      cycle  [int]
      _day   [int]
      _hour  [int]
      _min   [int]
    """
    self._day = int(d['day'])
    if self._day > self._now.day: 
      if self._month == 1:
        self._month = 12
      else:
        self._month = self._month - 1
    self._hour = int(d['hour'])
    self._min = int(d['min'])
    self.time = datetime.datetime(self._year, self._month, self._day,
                                  self._hour, self._min)
    if self._min < 45:
      self.cycle = self._hour
    else:
      self.cycle = self._hour+1
              
  def _parseWind( self, d ):
    """
    Parse the wind and variable-wind groups.
    
    The following attributes are set:
      wind_dir           [direction]
      wind_speed         [speed]
      wind_gust          [speed]
      wind_dir_from      [int]
      wind_dir_to        [int]
    """
    wind_dir = d['dir'].replace('O','0')
    if wind_dir != "VRB" and wind_dir != "///":
      self.wind_dir = direction(wind_dir)    
    wind_speed = d['speed'].replace('O','0')
    units = d['units']
    if units == 'KTS' or units == 'K' or units == 'T' or units == 'LT': 
      units = 'KT'
    if wind_speed.startswith("P"):
      self.wind_speed = speed(wind_speed[1:], units, ">")
    elif wind_speed != "//":
      self.wind_speed = speed(wind_speed, units)
    if d['gust']:
      wind_gust = d['gust']
      if wind_gust.startswith("P"):
        self.wind_gust = speed(wind_gust[1:], units, ">")
      else:
        self.wind_gust = speed(wind_gust, units)
    if d['varfrom']:
      self.wind_dir_from = direction(d['varfrom'])
      self.wind_dir_to = direction(d['varto'])      
    
  def _parseVisibility( self, d ):
    """
    Parse the minimum and maximum visibility groups.
    
    The following attributes are set:
      vis          [distance]
      vis_dir      [direction]
      max_vis      [distance]
      max_vis_dir  [direction]
    """
    vis = d['vis']
    vis_less = None
    vis_dir = None
    vis_units = "M"
    vis_dist = "10000"
    if d['dist']:
      vis_dist = d['dist']
    if d['units'] and d['units'] != "U":
        vis_units = d['units']
    if d['dir']:
      vis_dir = d['dir']    
    if vis_dist == "9999":
      vis_dist = "10000"
      vis_less = ">"
    if self.vis:
      if vis_dir:
        self.max_vis_dir = direction(vis_dir)
      self.max_vis = distance(vis_dist, vis_units, vis_less)
    else:
      if vis_dir:
        self.vis_dir = direction(vis_dir)
      self.vis = distance(vis_dist, vis_units, vis_less)
              
  def _parseRunway( self, d ):
    """
    Parse a runway visual range group.
    
    The following attributes are set:
      range   [list of tuples]
      . name  [string]
      . low   [distance]
      . high  [distance]
    """
    if d['name']:
      name = d['name']
      low = distance(d['low'])
      if d['high']:
        high = distance(d['high'])
      else:
        high = low
      self.runway.append((name,low,high))
              
  def _parseWeather( self, d ):
    """
    Parse a present-weather group.
    
    The following attributes are set:
      weather    [list of tuples]
      .  intensity     [string]
      .  description   [string]
      .  precipitation [string]
      .  obscuration   [string]
      .  other         [string]
    """
    inteni = d['int']
    if not inteni and d['int2']:
      inteni = d['int2']
    desci = d['desc']
    preci = d['prec']
    obsci = d['obsc']
    otheri = d['other']
    self.weather.append((inteni,desci,preci,obsci,otheri))
              
  def _parseSky( self, d ):
    """
    Parse a sky-conditions group.
    
    The following attributes are set:
      sky        [list of tuples]
      .  cover   [string]
      .  height  [distance]
      .  cloud   [string]
    """
    height = d['height']
    if not height or height == "///":
      height = None
    else:
      height = height.replace('O','0')
      height = distance(int(height)*100,"FT")
    cover = d['cover']
    if cover == 'SCK' or cover == 'SKC' or cover == 'CL': cover = 'CLR'
    if cover == '0VC': cover = 'OVC'
    cloud = d['cloud']
    if cloud == '///': cloud = ""
    self.sky.append((cover,height,cloud))
              
  def _parseTemp( self, d ):
    """
    Parse a temperature-dewpoint group.
    
    The following attributes are set:
      temp    temperature (Celsius) [float]
      dewpt   dew point (Celsius) [float]
    """
    temp = d['temp']
    dewpt = d['dewpt']
    if  temp and temp != "//" and temp != "XX" and temp != "MM" :
      self.temp = temperature(temp)
    if dewpt and dewpt != "//" and dewpt != "XX" and dewpt != "MM" :
      self.dewpt = temperature(dewpt)
    
  def _parsePressure( self, d ):
    """
    Parse an altimeter-pressure group.
    
    The following attributes are set:
      press    [int]
    """
    press = d['press']
    if press != '////':
      press = float(press.replace('O','0'))
      if d['unit']:
        if d['unit'] == 'A' or (d['unit2'] and d['unit2'] == 'INS'):
          self.press = pressure(press/100,'IN')
        elif d['unit'] == 'SLP':
          if press < 500:
            press = press/10 + 1000
          else:
            press = press/10 + 900
          self.press = pressure(press,'MB')
          self._remarks.append("sea-level pressure %.1fhPa" % press)
        else:
          self.press = pressure(press,'MB')
      elif press > 2500:
        self.press = pressure(press/100,'IN')
      else:
        self.press = pressure(press,'MB')
              
  def _parseRecent( self, d ):
    """
    Parse a recent-weather group.
    
    The following attributes are set:
      weather    [list of tuples]
      .  intensity     [string]
      .  description   [string]
      .  precipitation [string]
      .  obscuration   [string]
      .  other         [string]
    """
    desci = d['desc']
    preci = d['prec']
    obsci = d['obsc']
    otheri = d['other']
    self.recent.append(("",desci,preci,obsci,otheri))
    
  def _parseWindShear( self, d ):
    """
    Parse wind-shear groups.
    
    The following attributes are set:
      windshear    [list of strings]
    """
    if d['name']:
      self.windshear.append(d['name'])
    else:
      self.windshear.append("ALL")
    
  def _parseColor( self, d ):
    """
    Parse (and ignore) the color groups.
    
    The following attributes are set:
      trend    [list of strings]
    """
    pass

  def _parseTrend( self, d ):
    """
    Parse (and ignore) the trend groups.
    """
#    if not d['trend'] == "NOSIG":
#      while code and not code.startswith('RMK'):
#        try:
#          (group, code) = code.split(None,1)
#        except:
#          return("",trend)
    pass
    
  def _parseSealvlPressRemark( self, d ):
    """
    Parse the sea-level pressure remark group.
    """
    value = float(d['press'])/10.0
    if value < 50: 
      value += 1000
    else: 
      value += 900
    if not self.press:
      self.press = pressure(value,"MB")
    self.press_sea_level = pressure(value,"MB")
#    self._remarks.append("sea-level pressure %.1fhPa" % value)
        
  def _parsePrecip24hrRemark( self, d ):
    """
    Parse a 3-, 6- or 24-hour cumulative preciptation remark group.
    """
    value = float(d['precip'])/100.0
    if d['type'] == "6":
      if self.cycle == 3 or self.cycle == 9 or self.cycle == 15 or self.cycle == 21:
        self.precip_3hr = precipitation(value,"IN")
#        self._remarks.append("3-hour precipitation %.2fin" % value)
      else:
        self.precip_6hr = precipitation(value,"IN")
#        self._remarks.append("6-hr precip %.2fin" % value)  
    else:
      self.precip_24hr = precipitation(value,"IN")
#      self._remarks.append("24-hr precip %.2fin" % value)
        
  def _parsePrecip1hrRemark( self, d ):
    """Parse an hourly precipitation remark group."""
    value = float(d['precip'])/100.0
    self.precip_1hr = precipitation(value,"IN")
#    self._remarks.append("1-hr precip %.2fin" % value)
                
  def _parseTemp1hrRemark( self, d ):
    """
    Parse a temperature & dewpoint remark group.
    
    These values replace the temp and dewpt from the body of the report.
    """
    value = float(d['temp'])/10.0
    if d['tsign'] == "1": value = -value
    self.temp = temperature(value)
    if d['dewpt']:
      value2 = float(d['dewpt'])/10.0
      if d['dsign'] == "1": value2 = -value2
      self.dewpt = temperature(value2)
                
  def _parseTemp6hrRemark( self, d ):
    """
    Parse a 6-hour maximum or minimum temperature remark group.
    """
    value = float(d['temp'])/10.0
    if d['sign'] == "1": value = -value
    if d['type'] == "1":
      self.max_temp_6hr = temperature(value,"C")
#      self._remarks.append("6-hr max temp %.1fC" % value)
    else:
      self.min_temp_6hr = temperature(value,"C")
#      self._remarks.append("6-hr min temp %.1fC" % value)
    
  def _parseTemp24hrRemark( self, d ):
    """
    Parse a 24-hour maximum/minimum temperature remark group.
    """
    value = float(d['maxt'])/10.0
    if d['smaxt'] == "1": value = -value
    value2 = float(d['mint'])/10.0
    if d['smint'] == "1": value2 = -value2
    self.max_temp_24hr = temperature(value,"C")
    self.min_temp_24hr = temperature(value2,"C")
#    self._remarks.append("24-hr max temp %.1fC" % value)
#    self._remarks.append("24-hr min temp %.1fC" % value2)
            
  def _parsePress3hrRemark( self, d ):
    """
    Parse a pressure-tendency remark group.
    """
    value = float(d['press'])/10.0
    descrip = PRESSURE_TENDENCY[d['tend']]
    self._remarks.append("3-hr pressure change %.1fhPa, %s" % (value,descrip))
      
  def _parsePeakWindRemark( self, d ):
    """
    Parse a peak wind remark group.
    """
    peak_dir = int(d['dir'])
    peak_speed = int(d['speed'])
    self.wind_speed_peak = speed(peak_speed, "KT")
    self.wind_dir_peak = direction(peak_dir)
    peak_min = int(d['min'])
    if d['hour']:
      peak_hour = int(d['hour'])
    else:
      peak_hour = self._hour
    self._remarks.append("peak wind %dkt from %d degrees at %d:%02d" % \
                        (peak_speed, peak_dir, peak_hour, peak_min))
      
  def _parseWindShiftRemark( self, d ):
    """
    Parse a wind shift remark group.
    """
    if d['hour']:
      wshft_hour = int(d['hour'])
    else:
      wshft_hour = self._hour
    wshft_min = int(d['min'])
    text = "wind shift at %d:%02d" %  (wshft_hour, wshft_min)
    if d['front']:
      text += " (front)"
    self._remarks.append(text)
      
  def _parseLightningRemark( self, d ):
    """
    Parse a lightning observation remark group.
    """
    parts = []
    if d['freq']:
      parts.append(LIGHTNING_FREQUENCY[d['freq']])
    parts.append("lightning")        
    if d['type']:
      ltg_types = []
      group = d['type']
      while group:
        ltg_types.append(LIGHTNING_TYPE[group[:2]])
        group = group[2:]
      parts.append("("+string.join(ltg_types,",")+")")
    if d['loc']:
      parts.append(xlate_loc(d['loc']))
    self._remarks.append(string.join(parts," "))
      
  def _parseTSLocRemark( self, d ):
    """
    Parse a thunderstorm location remark group.
    """
    text = "thunderstorm"
    if d['loc']:
      text += " "+xlate_loc(d['loc'])
    if d['dir']:
      text += " moving %s" % d['dir']
    self._remarks.append(text)
    
  def _parseAutoRemark( self, d ):
    """
    Parse an automatic station remark group.
    """
    if d['type'] == "1":
      self._remarks.append("Automated station")
    elif d['type'] == "2":
      self._remarks.append("Automated station (type 2)")
    
  def _unparsedRemark( self, d ):
    """
    Handle otherwise unparseable remark groups.
    """
    self._unparsed.append(d['group'])
    
  ## the list of parser functions to use (in order) to parse a METAR report

  parsers = [ (TYPE_RE, _parseType, False),
              (STATION_RE, _parseStation, False), 
              (TIME_RE, _parseTime, False), 
              (MODIFIER_RE, _parseModifier, False), 
              (WIND_RE, _parseWind, False), 
              (VISIBILITY_RE, _parseVisibility, True), 
              (RUNWAY_RE, _parseRunway, True), 
              (WEATHER_RE, _parseWeather, True), 
              (SKY_RE, _parseSky, True), 
              (TEMP_RE, _parseTemp, False), 
              (PRESS_RE, _parsePressure, False), 
              (RECENT_RE,_parseRecent, True), 
              (WINDSHEAR_RE, _parseWindShear, True), 
              (COLOR_RE, _parseColor, True), 
              (TREND_RE, _parseTrend, False) ]
  
  ## the list of patterns for the various remark groups, 
  ## paired with the parser functions to use to record the decoded remark.

  remark_parsers = [ (AUTO_RE,         _parseAutoRemark),
                     (SEALVL_PRESS_RE, _parseSealvlPressRemark),
                     (PEAK_WIND_RE,    _parsePeakWindRemark),
                     (WIND_SHIFT_RE,   _parseWindShiftRemark),
                     (LIGHTNING_RE,    _parseLightningRemark),
                     (TS_LOC_RE,       _parseTSLocRemark),
                     (TEMP_1HR_RE,     _parseTemp1hrRemark),
                     (PRECIP_1HR_RE,   _parsePrecip1hrRemark),
                     (PRECIP_24HR_RE,  _parsePrecip24hrRemark),
                     (PRESS_3HR_RE,    _parsePress3hrRemark),
                     (TEMP_6HR_RE,     _parseTemp6hrRemark),
                     (TEMP_24HR_RE,    _parseTemp24hrRemark),
                     (UNPARSED_RE,     _unparsedRemark) ]
  
  ## functions that return text representations of conditions for output

  def string( self ):
    """
    Return a human-readable version of the decoded report.
    """
    lines = []
    lines.append("station: %s" % self.station_id)
    if self.type:
      lines.append("type: %s" % self.report_type())
    if self.time:
      lines.append("time: %s" % self.time.ctime())
    if self.temp:
      lines.append("temperature: %s" % self.temp.string("C"))
    if self.dewpt:
      lines.append("dew point: %s" % self.dewpt.string("C"))
    if self.wind_speed:
      lines.append("wind: %s" % self.wind())
    if self.wind_speed_peak:
      lines.append("peak wind: %s" % self.peak_wind())
    if self.vis:
      lines.append("visibility: %s" % self.visibility())
    if self.runway:
      lines.append("visual range: %s" % self.runway_visual_range())
    if self.press:
      lines.append("pressure: %s" % self.press.string("mb"))
    if self.weather:
      lines.append("weather: %s" % self.present_weather())
    if self.sky:
      lines.append("sky: %s" % self.sky_conditions("\n     "))
    if self.press_sea_level:
      lines.append("sea-level pressure: %s" % self.press_sea_level.string("mb"))
    if self.max_temp_6hr:
      lines.append("6-hour max temp: %s" % self.max_temp_6hr.string())
    if self.max_temp_6hr:
      lines.append("6-hour min temp: %s" % self.min_temp_6hr.string())
    if self.max_temp_24hr:
      lines.append("24-hour max temp: %s" % self.max_temp_24hr.string())
    if self.max_temp_24hr:
      lines.append("24-hour min temp: %s" % self.min_temp_24hr.string())
    if self.precip_1hr:
      lines.append("1-hour precipitation: %s" % self.precip_1hr.string())
    if self.precip_3hr:
      lines.append("3-hour precipitation: %s" % self.precip_3hr.string())
    if self.precip_6hr:
      lines.append("6-hour precipitation: %s" % self.precip_6hr.string())
    if self.precip_24hr:
      lines.append("24-hour precipitation: %s" % self.precip_24hr.string())
    if self._remarks:
      lines.append("remarks:")
      lines.append("- "+self.remarks("\n- "))
    if self._unparsed:
      lines.append("- "+' '.join(self._unparsed))
    lines.append("METAR: "+self.code)
    return string.join(lines,"\n")

  def report_type( self ):
    """
    Return a textual description of the report type.
    """
    if self.type == None:
      text = "unknown report type"
    elif REPORT_TYPE.has_key(self.type):
      text  = REPORT_TYPE[self.type]
    else:
      text = self.type+" report"
    if self.cycle:
      text += ", cycle %d" % self.cycle
    if self.mod:
      if REPORT_TYPE.has_key(self.mod):
        text += " (%s)" % REPORT_TYPE[self.mod]
      else:
        text += " (%s)" % self.mod
    return text

  def wind( self, units="KT" ):
    """
    Return a textual description of the wind conditions.
    
    Units may be specified as "MPS", "KT", "KMH", or "MPH".
    """
    if self.wind_speed == None:
      return "missing"
    elif self.wind_speed.value() == 0.0:
      text = "calm"
    else:
      wind_speed = self.wind_speed.string(units)
      if not self.wind_dir:
        text = "variable at %s" % wind_speed
      elif self.wind_dir_from:
        text = "%s to %s at %s" % \
               (self.wind_dir_from.compass(), self.wind_dir_to.compass(), wind_speed)
      else:
        text = "%s at %s" % (self.wind_dir.compass(), wind_speed)
      if self.wind_gust:
        text += ", gusting to %s" % self.wind_gust.string(units)
    return text

  def peak_wind( self, units="KT" ):
    """
    Return a textual description of the peak wind conditions.
    
    Units may be specified as "MPS", "KT", "KMH", or "MPH".
    """
    if self.wind_speed_peak == None:
      return "missing"
    elif self.wind_speed_peak.value() == 0.0:
      text = "calm"
    else:
      wind_speed = self.wind_speed_peak.string(units)
      if not self.wind_dir_peak:
        text = wind_speed
      else:
        text = "%s at %s" % (self.wind_dir_peak.compass(), wind_speed)
    return text

  def visibility( self, units=None ):
    """
    Return a textual description of the visibility.
    
    Units may be statute miles ("SM") or meters ("M").
    """
    if self.vis == None:
      return "missing"
    if self.vis_dir:
      text = "%s to %s" % (self.vis.string(units), self.vis_dir.compass())
    else:
      text = self.vis.string(units)
    if self.max_vis:
      if self.max_vis_dir:
        text += "; %s to %s" % (self.max_vis.string(units), self.max_vis_dir.compass())
      else:
        text += "; %s" % self.max_vis.string()
    return text
  
  def runway_visual_range( self, units=None ):
    """
    Return a textual description of the runway visual range.
    """
    lines = []
    for name,low,high in self.runway:
      if low != high:
        lines.append("runway %s: %s to %s feet" % (name, low.string(units), high.string(units)))
      else:
        lines.append("runway %s: %s feet" % (name, low.string(units)))
    return string.join(lines,"; ")
  
  def present_weather( self ):
    """
    Return a textual description of the present weather.
    """
    text_list = []
    for weatheri in self.weather:
      (inteni,desci,preci,obsci,otheri) = weatheri
      text_parts = []
      code_parts = []
      
      if inteni:
        code_parts.append(inteni)
        text_parts.append(WEATHER_INT[inteni])
        
      if desci:
        code_parts.append(desci)
        if desci != "SH" or not preci:
          text_parts.append(WEATHER_DESC[desci[0:2]])
          if len(desci) == 4:
            text_parts.append(WEATHER_DESC[desci[2:]])
        
      if preci:
        code_parts.append(preci)        
        
        if len(preci) == 2:
          precip_text = WEATHER_PREC[preci]
        elif len(preci) == 4:
          precip_text = WEATHER_PREC[preci[:2]]+" and "
          precip_text += WEATHER_PREC[preci[2:]]
        elif len(preci) == 6:
          precip_text = WEATHER_PREC[preci[:2]]+", "
          precip_text += WEATHER_PREC[preci[2:4]]+" and "
          precip_text += WEATHER_PREC[preci[4:]]

        if desci == "TS":
          text_parts.append("with")
        text_parts.append(precip_text)
        if desci == "SH":
          text_parts.append(WEATHER_DESC[desci])
        
      if obsci:
        code_parts.append(obsci)
        text_parts.append(WEATHER_OBSC[obsci])
        
      if otheri:
        code_parts.append(otheri)
        text_parts.append(WEATHER_OTHER[otheri])
        
      code = string.join(code_parts)
      if WEATHER_SPECIAL.has_key(code):
        text_list.append(WEATHER_SPECIAL[code])
      else:
        text_list.append(string.join(text_parts," "))
    return string.join(text_list,"; ")
  
  def sky_conditions( self, sep="; " ):
    """
    Return a textual description of the sky conditions.
    """
    text_list = []
    for skyi in self.sky:
      (cover,height,cloud) = skyi
      if cover == "SKC" or cover == "CLR":
        text_list.append(SKY_COVER[cover])
      else:
        if cloud:
          what = CLOUD_TYPE[cloud]
        elif cover != "OVC":
          what = "clouds"
        else: 
          what = ""
        if cover == "VV":
          text_list.append("%s%s, visibility to %s" % 
                           (SKY_COVER[cover],what,height.string()))
        else:
          text_list.append("%s%s at %s" % 
                           (SKY_COVER[cover],what,height.string()))
    return string.join(text_list,sep)
      
  def remarks( self, sep="; "):
    """
    Return the decoded remarks.
    """
    return string.join(self._remarks,sep)

