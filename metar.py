#!/usr/bin/python
#
#  A python module for interpreting METAR and SPECI weather reports.
#  
#  Follows US conventions for METAR/SPECI reports, described in chapter 12 of
#  the Federal Meteorological Handbook No.1. (FMH-1 1995), issued by NOAA. 
#  See <http://metar.noaa.gov/>
# 
#  International conventions for the METAR and SPECI codes are specified in 
#  the WMO Manual on Codes, vol I.1, Part A (WMO-306 I.i.A).  This module
#  doesn't handle any of the more general encodings in the WMO spec.
#
#  The current METAR report for a given station is available at the URL
#  http://weather.noaa.gov/pub/data/observations/metar/stations/<station>.TXT
#  where <station> is the four-letter ICAO station code.  
#
#  metar.py was inspired by Tobias Klausmann's pymetar.py module, but shares no 
#  code with it and is more narrowly focussed on parsing the raw METAR code.
# 
#  Copyright 2004  Tom Pollard
# 
import re
import datetime
import string

__author__ = "mlpollard@earthlink.net"

__version__ = "1.0.1"

__doc__ = """metar.py v%s (c) 2004, Walter Thomas Pollard

Metar.py is a python module that interprets METAR and SPECI weather reports
following US conventions.

Please e-mail bugs to: %s""" % (__version__, __author__)

__LICENSE__ = """
Copyright (c) 2004, Walter Thomas Pollard
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

## regular expressions to decode various groups of the METAR code

TYPE_RE =     re.compile(r"^(?P<type>METAR|SPECI|TESTM)\s+")
MODIFIER_RE = re.compile(r"^(?P<mod>AUTO|COR)\s+")
STATION_RE =  re.compile(r"^(?P<station>[A-Z][A-Z0-9]{3})\s+")
TIME_RE = re.compile(r"""^(?P<day>\d\d)
                          (?P<hour>\d\d)
                          (?P<min>\d\d)Z\s+""",
                     re.VERBOSE)
WIND_RE = re.compile(r"""^(?P<dir>\d\d\d|VRB)
                          (?P<speed>P?\d\d\d?)
                        (G(?P<gust>P?\d\d\d?))?
                          (?P<unit>KT|KMH|MPS)
                      (\s+(?P<varfrom>\d\d\d)V
                          (?P<varto>\d\d\d))?\s+""",
                     re.VERBOSE)
VISIBILITY_RE =   re.compile(r"""^(?P<vis>M?(\d+|(\d\s+)?\d/\d\d?)|CAVOK)?
                                  (?P<unit>(SM)?)\s+""",
                             re.VERBOSE)
FRACTION_RE = re.compile(r"^((?P<i>\d+)\s+)?(?P<n>\d+)/(?P<d>\d+)$")
RUNWAY_RE = re.compile(r"""^R(?P<name>\d\d(R|L|C)?)/
                             (?P<low>(M|P)?\d\d\d\d)
                           (V(?P<high>(M|P)?\d\d\d\d))?
                            FT\s+""",
                       re.VERBOSE)
WEATHER_RE = re.compile(r"""^(?P<int>(-|\+|VC)*)?
                             (?P<desc>MI|PR|BC|DR|BL|SH|TS|FZ)?
                             (?P<prec>(DZ|RA|SN|SG|IC|PL|GR|GS|UP)*)?
                             (?P<obsc>BR|FG|FU|VA|DU|SA|HZ|PY)?
                             (?P<other>PO|SQ|FC|SS|DS)?\s+""",
                        re.VERBOSE)
SKY_RE= re.compile(r"""^(?P<cover>VV|CLR|SKC|BKN|SCT|FEW|OVC)
                        (?P<height>\d\d\d|///)?
                        (?P<cloud>CB|TCU)?\s+""",
                   re.VERBOSE)
TEMP_RE = re.compile(r"""^(?P<temp>M?\d+)/
                          (?P<dewpt>M?\d+)?\s+""",
                     re.VERBOSE)
PRESS_RE = re.compile(r"""^(?P<unit>A|Q)
                           (?P<press>\d\d\d\d)\s+""",
                      re.VERBOSE)

## regular expressions for remark groups

AUTO_RE = re.compile(r"^AO(?P<type>\d)\s+")
SEALVL_PRESS_RE = re.compile(r"^SLP(?P<press>\d\d\d)\s+")
PEAK_WIND_RE = re.compile(r"""^PK\s+WND\s+
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
TEMP_24HR_RE = re.compile(r"""^4(?P<smax>0|1)
                                (?P<tmax>\d\d\d)
                                (?P<smin>0|1)
                                (?P<tmin>\d\d\d)\s+""",
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
              "FEW":"a few ",
              "SCT":"scattered ",
              "BKN":"broken ",
              "OVC":"overcast",
              "VV":"indefinite ceiling" }
              
CLOUD_TYPE = { "TCU":"towering cumulus",
               "CB":"cumulonimbus",
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
                 "UP":"unknown precipitation" }
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

## translation of various remark codes into english
        
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
                "AUTO":"automatic",
                "COR":"manually corrected" }

## Exceptions

class MetarError(Exception):
  """Base class for exceptions raised by the metar class."""
  pass
  
class UnitError(MetarError):
  """Exception raised when an unrecognized unit is used."""
  pass
  
## classes representing dimensioned values
    
class temperature:
  """A temperature value."""
  legal_units = [ "F", "C", "K" ]
  
  def __init__( self, value, units="C" ):
    self._value = float(value)
    self._units = units.upper()
    if not units.upper() in temperature.legal_units:
      raise UnitError("unknown temperature unit: "+units)
    
  def value( self, units=None ):
    """Return the temperature in the specified units."""
    if units == None:
      return self._value
    else:
      if not units.upper() in temperature.legal_units:
        raise UnitError("unknown temperature unit: "+units)
      units = units.upper()
    if self._units == "C":
      celsius_value = self._value
    elif self._units == "F":
      celsius_value = (self._value-32.0)/1.8
    elif self._units == "K":
      celsius_value = 273.15+self._value
    if units == "C":
        return celsius_value
    elif units == "K":
        return 273.15+celsius_value
    elif units == "F":
      return 32.0+self._value*1.8
      
  def string( self, units=None ):
    """Return a string representation of the temperature, using the given units."""
    if units == None:
      units = self._units
    else:
      if not units.upper() in temperature.legal_units:
        raise UnitError("unknown temperature unit: "+units)
      units = units.upper()
    val = self.value(units)
    if units == "C":
      return "%.1f C" % val
    elif units == "F":
      return "%.1f F" % val
    elif units == "K":
      return "%.1f K" % val

class pressure:
  """A barometric pressure value."""
  legal_units = [ "MB", "HPA", "IN" ]
  
  def __init__( self, value, units="MB" ):
    self._value = float(value)
    self._units = units.upper()
    if not units.upper() in pressure.legal_units:
      raise UnitError("unknown pressure unit: "+units)
    
  def value( self, units=None ):
    """Return the pressure in the specified units."""
    if units == None:
      return self._value
    else:
      if not units.upper() in pressure.legal_units:
        raise UnitError("unknown pressure unit: "+units)
      units = units.upper()
    if units == self._units:
      return self._value
    if self._units == "IN":
      mb_value = self._value*33.86398
    else:
      mb_value = self._value
    if units == "MB" or units == "HPA":
      return mb_value
    elif units == "IN":
        return mb_value/33.86398
    else:
      raise UnitError("unknown pressure unit: "+units)
      
  def string( self, units=None ):
    """Return a string representation of the pressure, using the given units."""
    if units == None:
      units = self._units
    else:
      if not units.upper() in pressure.legal_units:
        raise UnitError("unknown pressure unit: "+units)
      units = units.upper()
    val = self.value(units)
    if units == "MB":
      return "%.1f mb" % val
    elif units == "HPA":
      return "%.1f hPa" % val
    elif units == "IN":
      return "%.2f inches" % val

class speed:
  """A wind speed value."""
  legal_units = [ "KT", "MPS", "KMH", "MPH" ]
  
  def __init__( self, value, units="MPS" ):
    self._value = float(value)
    self._units = units.upper()
    if not units.upper() in speed.legal_units:
      raise UnitError("unknown speed unit: "+units)
    
  def value( self, units=None ):
    """Return the pressure in the specified units."""
    if not units:
      return self._value
    else:
      if not units.upper() in speed.legal_units:
        raise UnitError("unknown speed unit: "+units)
      units = units.upper()
    if units == self._units:
      return self._value
    if self._units == "KMH":
      mps_value = self._units/3.6
    elif self._units == "KT":
      mps_value = self._value*0.514444
    elif self._units == "MPH":
      mbs_value = self._value*0.447000
    else:
      mps_value = self._value
    if units == "KMH":
      return mps_value*3.6
    elif units == "KT":
      return mps_value/0.514444
    elif units == "MPH":
      return mps_value/0.447000
    elif units == "MPS":
      return mps_value
      
  def string( self, units=None ):
    """Return a string representation of the speed in the given units."""
    if not units:
      units = self._units
    else:
      if not units.upper() in speed.legal_units:
        raise UnitError("unknown speed unit: "+units)
      units = units.upper()
    val = self.value(units)
    if units == "KMH":
      return "%.0f km/h" % val
    elif units == "KT":
      return "%.0f knots" % val
    elif units == "MPH":
      return "%.0f mph" % val
    elif units == "MPS":
      return "%.1f mps" % val

class distance:
  """A distance value."""
  legal_units = [ "SM", "MI", "M", "KM", "FT" ]
  
  def __init__( self, value, units="M" ):
    self._value = float(value)
    self._units = units.upper()
    if not units.upper() in distance.legal_units:
      raise UnitError("unknown distance unit: "+units)
    
  def value( self, units=None ):
    """Return the distance in the specified units."""
    if not units:
      return self._value
    else:
      if not units.upper() in distance.legal_units:
        raise UnitError("unknown distance unit: "+units)
      units = units.upper()
    if units == self._units:
      return self._value
    if self._units == "SM":
      m_value = self._units*1609.344
    elif self._units == "FT":
      m_value = self._value/3.28084
    elif self._units == "KM":
      m_value = self._value*1000
    else:
      m_value = self._value
    if units == "SM":
      return m_value/1609.344
    elif units == "FT":
      return m_value*3.28084
    elif units == "KM":
      return m_value/0.447000
    elif units == "M":
      return m_value
      
  def string( self, units=None ):
    """Return a string representation of the distance in the given units."""
    if not units:
      units = self._units
    else:
      if not units.upper() in distance.legal_units:
        raise UnitError("unknown distance unit: "+units)
      units = units.upper()
    val = self.value(units)
    if units == "SM":
      return "%.0f miles" % val
    elif units == "M":
      return "%.0f meters" % val
    elif units == "KM":
      return "%.0f km" % val
    elif units == "FT":
      return "%.0f feet" % val

## METAR report objects

class metar:
  """METAR (aviation meteorology report)"""
  
  def __init__( self, metarcode, month=None, year=None, utcdelta=None ):
    """Parse raw METAR code."""
    self.code = metarcode

    self.type = None                   # METAR (routine) or SPECI (special)
    self.mod = "AUTO"                  # AUTO (automatic) or COR (corrected)
    self.station_id = None             # 4-character ICAO station code
    self.time = None                   # observation time [datetime]
    self.cycle = None                  # observation cycle (0-23) [int]
    self.wind_dir = None               # wind direction (degrees) [int]
    self.wind_variable = None          # wind direction variable? [bool]
    self.wind_speed = None             # wind speed [speed]
    self.wind_speed_greater = None     # wind speed is lower limit? [bool]
    self.wind_gust = None              # wind gust speed (kt) [int]
    self.wind_gust_greater = None      # wind gust speed is lower limit? [bool]
    self.wind_dir_from = None          # beginning of range for win dir (degrees) [int]
    self.wind_dir_to = None            # end of range for win dir (degrees) [int]
    self.vis = None                    # visibility (stautue miles) [distance]
    self.vis_less = None               # visibilty is upper limit? [bool]
    self._vis_frac = None              
    self.temp = None                   # temperature (C) [temperature]
    self.dewpt = None                  # dew point (C) [temperature]
    self.press = None                  # barometric pressure [pressure]
    self.runway = []                   # runway visibility (list of tuples)
    self.weather = []                  # present weather (list of tuples)
    self.sky = []                      # sky conditions (list of tuples)
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
    
    code = self.code+" "    # (my regexp's all expect trailing spaces...)
    for parser in metar.parsers:
      code, match = parser(self,code)
      while match:
         code, match = parser(self,code)
    
          
  def _parseType( self, code ):
    """
    Parse the code-type group.
    
    The following attributes are set:
      type   [string]
    """
    m = TYPE_RE.match(code)
    if not m: 
      return (code,None)
    self.type = m.groupdict()['type'] 
    return TYPE_RE.sub("",code), m.group()
      
  def _parseStation( self, code ):
    """
    Parse the station id group.
    
    The following attributes are set:
      station_id   [string]
    """
    m = STATION_RE.match(code)
    if not m: 
      return (code,None)
    self.station_id = m.groupdict()['station'] 
    return STATION_RE.sub("",code), m.group()
      
  def _parseModifier( self, code ):
    """
    Parse the report-modifier group.
    
    The following attributes are set:
      mod   [string]
    """
    m = MODIFIER_RE.match(code)
    if not m: 
      return (code,None)
    self.mod = m.groupdict()['mod'] 
    return MODIFIER_RE.sub("",code), m.group()
              
  def _parseTime( self, code ):
    """
    Parse the observation-time group.
    
    The following attributes are set:
      time   [datetime]
      cycle  [int]
      _day   [int]
      _hour  [int]
      _min   [int]
    """
    m = TIME_RE.match(code)
    if not m: 
      return (code,None)
    d = m.groupdict()
    self._day = int(d['day'])
    self._hour = int(d['hour'])
    self._min = int(d['min'])
    self.time = datetime.datetime(self._year, self._month, self._day,
                                  self._hour, self._min)
    if self._min < 45:
      self.cycle = self._hour
    else:
      self.cycle = self._hour+1
    return TIME_RE.sub("",code), m.group()
              
  def _parseWind( self, code ):
    """
    Parse the wind and variable-wind groups.
    
    The following attributes are set:
      wind_dir           [int]
      wind_speed         [int]
      wind_speed_greater [bool]
      wind_gust          [int]
      wind_gust_greater  [bool]
      wind_dir_from      [int]
      wind_dir_to        [int]
    """
    m = WIND_RE.match(code)
    if not m: 
      return (code,None)
    d = m.groupdict()
    self.wind_dir = d['dir']
    if self.wind_dir == "VRB":
      self.wind_variable = True
    else:
      self.wind_dir = int(self.wind_dir)    
    wind_speed = d['speed']
    if wind_speed.startswith("P"):
      self.wind_speed_greater = True
      wind_speed = wind_speed[1:]
    self.wind_speed = speed(wind_speed,d['unit'])
    if d['gust']:
      self.wind_gust = d['gust']
      if self.wind_gust.startswith("P"):
        self.wind_gust_greater = True
        self.wind_gust = self.wind_gust[1:]
        self.wind_gust = speed(self.wind_gust,d['unit'])
    if d['varfrom']:
      self.wind_dir_from = int(d['varfrom'])
      self.wind_dir_to = int(d['varto'])      
    return WIND_RE.sub("",code), m.group()
    
  def _parseVisibility( self, code ):
    """
    Parse the visibility group.
    
    The following attributes are set:
      vis           [float]
      vis_less      [bool]
      _vis_frac     [string]
    """
    m = VISIBILITY_RE.match(code)
    if not m: 
      return (code,None)
    d = m.groupdict()
    self.vis = d['vis']
    if self.vis.startswith("M"):
      self.vis_less = True
      self.vis = self.vis[1:]
    mf = FRACTION_RE.match(self.vis)
    if mf:
      df = mf.groupdict()
      self._vis_frac = mf.group()
      vis_num = float(df['n'])
      vis_den = float(df['d'])
      value = vis_num/vis_den
      if df['i']:
        value += int(df['i'])
      self.vis = distance(value,d['unit'])
    elif self.vis == "CAVOK" or self.vis == "9999":
      self.vis = distance(10000)
    else:
      self.vis = distance(self.vis,d['unit'])  
    return VISIBILITY_RE.sub("",code), m.group()
              
  def _parseRunway( self, code ):
    """
    Parse a runway visual range group.
    
    The following attributes are set:
      range              [list of tuples, each...]
        (name,low,high) [...string, string, string]
    """
    m = RUNWAY_RE.match(code)
    if not m: 
      return (code,None)
    d = m.groupdict()
    name = d['name']
    low = distance(d['low'])
    if d['high']:
      high = distance(d['high'])
    else:
      high = low
    self.runway.append((name,low,high))
    return RUNWAY_RE.sub("",code), m.group()
              
  def _parseWeather( self, code ):
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
    m = WEATHER_RE.match(code)
    if not m: 
      return (code,None)
    d = m.groupdict()
    intensity = d['int']
    description = d['desc']
    precipitation = d['prec']
    obscuration = d['obsc']
    other = d['other']
    self.weather.append((intensity,description,precipitation,obscuration,other))
    return WEATHER_RE.sub("",code), m.group()
              
  def _parseSky( self, code ):
    """
    Parse a sky-conditions group.
    
    The following attributes are set:
      sky                       [list of tuples]
      .  cover   [string]
      .  height  [int]
      .  cloud   [string]
    """
    m = SKY_RE.match(code)
    if not m: 
      return (code,None)
    d = m.groupdict()
    height = d['height']
    if height == "///":
      height = None
    else:
      height = int(height)*100
    self.sky.append((d['cover'],height,d['cloud']))
    return SKY_RE.sub("",code), m.group()
              
  def _parseTemp( self, code ):
    """
    Parse a temperature-dewpoint group.
    
    The following attributes are set:
      temp    temperature (Celsius) [float]
      dewpt   dew point (Celsius) [float]
    """
    m = TEMP_RE.match(code)
    if not m: 
      return (code,None)
    d = m.groupdict()
    self.temp = temperature(d['temp'])
    if d['dewpt']:
      self.dewpt = temperature(d['dewpt'])
    return TEMP_RE.sub("",code), m.group()
    
  def _parsePressure( self, code ):
    """
    Parse an altimeter-pressure group.
    
    The following attributes are set:
      press    [int]
    """
    m = PRESS_RE.match(code)
    if not m: 
      return (code,None)
    d = m.groupdict()
    if d['unit'] == "A":
      self.press = pressure(float(d['press'])/100,"IN")
    else:
      self.press = pressure(d['press'],"MB")
    return PRESS_RE.sub("",code), m.group()
    
  def _parseRemarks( self, code ):
    """
    Parse the remarks groups.
    
    The following attributes are set:
      remarks    [list of strings]
    """
    if not code.startswith("RMK "):
      return (code,None)
    code = code[4:].lstrip()
    while code:
      for pattern, parser in metar.remark_parsers:
        m = pattern.match(code)
        if m:
          parser(self,m.groupdict())
          code = pattern.sub("",code,1)
          break
    return ("", "RMK")
          
  def _parseSealvlPressRemark( self, d ):
    """
    Parse the sea-level pressure remark group.
    """
    value = float(d['press'])/10.0
    if value < 50: 
      value += 1000
    else: 
      value += 900
    self._remarks.append("sea-level pressure %.1fhPa" % value)
        
  def _parsePrecip24hrRemark( self, d ):
    """
    Parse a 3-, 6- or 24-hour cumulative preciptation remark group.
    """
    value = float(d['precip'])/100.0
    if d['type'] == "6":
      if self.cycle == 3 or self.cycle == 9 or self.cycle == 15 or self.cycle == 21:
        self._remarks.append("3-hour precipitation %.2fin" % value)
      else:
        self._remarks.append("6-hr precip %.2fin" % value)  
    else:
      self._remarks.append("24-hr precip %.2fin" % value)
        
  def _parsePrecip1hrRemark( self, d ):
    """Parse an hourly precipitation remark group."""
    value = float(d['precip'])/100.0
    self._remarks.append("1-hr precip %.2fin" % value)
                
  def _parseTemp1hrRemark( self, d ):
    """
    Parse a temperature & dewpoint remark group.
    
    These values replace the temp and dewpt from the main body of the report.
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
      self._remarks.append("6-hr max temp %.1fC" % value)
    else:
      self._remarks.append("6-hr min temp %.1fC" % value)
    
  def _parseTemp24hrRemark( self, d ):
    """
    Parse a 24-hour maximum/minimum temperature remark group.
    """
    value = float(d['maxt'])/10.0
    if d['maxs'] == "1": value = -value
    value2 = float(d['mint'])/10.0
    if d['mins'] == "1": value2 = -value2
    self._remarks.append("24-hr max temp %.1fC" % value)
    self._remarks.append("24-hr min temp %.1fC" % value2)
            
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
    wshft_hour = int(d['hour'])
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
    
  ## the list of parser functions to use (in order) to parse a raw METAR code

  parsers = [ _parseType, _parseStation, _parseTime, _parseModifier, _parseWind, 
              _parseVisibility, _parseRunway, _parseWeather, _parseSky, 
              _parseTemp, _parsePressure, _parseRemarks ]
  
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

  def report( self ):
    """
    Return a complete decoded report.
    
    (At this stage, this is more for debugging than for any real use.)
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
    lines.append("wind: %s" % self.wind())
    lines.append("visibility: %s" % self.visibility())
    if self.runway:
      lines.append("visual range: %s" % self.runway_visual_range())
    if self.press:
      lines.append("pressure: %s" % self.press.string("mb"))
    lines.append("weather: %s" % self.present_weather())
    lines.append("sky: %s" % self.sky_conditions("\n     "))
    if self._remarks:
      lines.append("remarks:")
      lines.append("- "+self.remarks("\n- "))
    return string.join(lines,"\n")

  def report_type( self ):
    """
    Return a textual description of the report type.
    """
    if self.type == None:
      text = "unknown report type"
    if REPORT_TYPE.has_key(self.type):
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
    
    Units may be specified as "KMH", "CMPS" or "KT".
    """
    if self.wind_speed.value() == 0.0:
      text = "calm"
    else:
      wind_speed = self.wind_speed.string(units)
      if self.wind_variable:
        text = "variable at %s" % wind_speed
      elif self.wind_dir_from:
        text = "%s, variable from %d to %d degrees" % \
               (speed, self.wind_dir_from, self.wind_dir_to)
      else:
        text = "%s from %d degrees" % (wind_speed, self.wind_dir)
      if self.wind_gust:
        wind_gust = self.wind_gust.string(units)
        text += ", gusting to %s" % wind_gust
    return text

  def visibility( self, units="SM" ):
    """
    Return a textual description of the visibility.
    
    Units may be statute miles ("SM") or meters ("M").
    """
    if self.vis == None:
      return "missing"
    if units == "SM" and self._vis_frac:
        text = "%s miles" % self._vis_frac
    else:
      text = self.vis.string()
    if self.vis_less:
      text = "less than "+text
    return text
  
  def runway_visual_range( self ):
    """
    Return a textual description of the runway visual range.
    """
    lines = []
    for name,low,high in self.runway:
      if low.startswith("M"):
        low = "less than %s" % low[1:]
      if low.startswith("P"):
        low = "greater than %s" % low[1:]
      if high.startswith("P"):
        high = "greater than %s" % high[1:]
      if low != high:
        lines.append("runway %s: %s to %s feet" % (name,low,high))
      else:
        lines.append("runway %s: %s feet" % (name,low))
    return string.join(lines,"; ")
  
  def present_weather( self ):
    """
    Return a textual description of the present weather.
    """
    text_list = []
    for weatheri in self.weather:
      (intensity,description,precipitation,obscuration,other) = weatheri
      text_parts = []
      code_parts = []
      
      if intensity:
        code_parts.append(intensity)
        text_parts.append(WEATHER_INT[intensity])
        
      if description:
        code_parts.append(description)
        if description != "SH" or not precipitation:
          text_parts.append(WEATHER_DESC[description])
        
      if precipitation:
        code_parts.append(precipitation)        
        
        if len(precipitation) == 2:
          precip_text = WEATHER_PREC[precipitation]
        elif len(precipitation) == 4:
          precip_text = WEATHER_PREC[precipitation[:2]]+" and "
          precip_text += WEATHER_PREC[precipitation[2:]]
        elif len(precipitation) == 6:
          precip_text = WEATHER_PREC[precipitation[:2]]+", "
          precip_text += WEATHER_PREC[precipitation[2:4]]+" and "
          precip_text += WEATHER_PREC[precipitation[4:]]

        if description == "TS":
          text_parts.append("with")
        text_parts.append(precip_text)
        if description == "SH":
          text_parts.append(WEATHER_DESC[description])
        
      if obscuration:
        code_parts.append(obscuration)
        text_parts.append(WEATHER_OBSC[obscuration])
        
      if other:
        code_parts.append(other)
        text_parts.append(WEATHER_OTHER[other])
        
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
          text.list.append("%s%s, visibility to %d ft" % (SKY_COVER[cover],what,height))
        else:
          text_list.append("%s%s at %d ft" % (SKY_COVER[cover],what,height))
    return string.join(text_list,sep)
      
  def remarks( self, sep="; "):
    """
    Return the decoded remarks.
    """
    return string.join(self._remarks,sep)

## simple command-line driver

if __name__ == "__main__":
  import sys
  while True:
    print "raw METAR report: ",
    try:
      raw = sys.stdin.readline()
      if raw == "":
        break
      raw = raw.strip()
      if len(raw):
        obs = metar(raw)
        print obs.report()
    except KeyboardInterrupt:
      break