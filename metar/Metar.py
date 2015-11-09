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
"""
This module defines the Metar class.  A Metar object represents the weather report encoded by a single METAR code.
"""

__author__ = "Tom Pollard"

__email__ = "pollard@alum.mit.edu"

__version__ = "1.2"

__LICENSE__ = """
Copyright (c) 2004, %s
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""" % __author__

import re
import datetime
import string
from Datatypes import *

## Exceptions

class ParserError(Exception):
  """Exception raised when an unparseable group is found in body of the report."""
  pass

## regular expressions to decode various groups of the METAR code

MISSING_RE = re.compile(r"^[M/]+$")

TYPE_RE =     re.compile(r"^(?P<type>METAR|SPECI)(\s*COR)?\s+")
STATION_RE =  re.compile(r"^(?P<station>[A-Z][A-Z0-9]{3})\s+")
TIME_RE = re.compile(r"""^(?P<day>\d\d)
                          (?P<hour>\d\d)
                          (?P<min>\d\d)Z?\s+""",
                          re.VERBOSE)
MODIFIER_RE = re.compile(r"^(?P<mod>AUTO|FINO|NIL|TEST|CORR?|RTD|CC[A-G])\s+")
WIND_RE = re.compile(r"""^(?P<dir>[\dO]{3}|[0O]|///|MMM|VRB)
                          (?P<speed>P?[\dO]{2,3}|[0O]+|[/M]{2,3})
                          (G(?P<gust>P?(\d{1,3}|[/M]{1,3})))?
                          (?P<units>KTS?|LT|K|T|KMH|MPS)?
                          (\s+(?P<varfrom>\d\d\d)V
                          (?P<varto>\d\d\d))?\s+""",
                          re.VERBOSE)
# VISIBILITY_RE =   re.compile(r"""^(?P<vis>(?P<dist>M?(\d\s+)?\d/\d\d?|M?\d+)
#                                     ( \s*(?P<units>SM|KM|M|U) | NDV |
#                                          (?P<dir>[NSEW][EW]?) )? |
#                                    CAVOK )\s+""",
#                                    re.VERBOSE)
# start patch
VISIBILITY_RE = re.compile(r"""^(?P<vis>(?P<dist>(M|P)?\d\d\d\d|////)
                                            (?P<dir>[NSEW][EW]? | NDV)? |
                                        (?P<distu>(M|P)?(\d+|\d\d?/\d\d?|\d+\s+\d/\d))
                                           (?P<units>SM|KM|M|U) |
                                        CAVOK )\s+""",
                                 re.VERBOSE)
# end patch
RUNWAY_RE = re.compile(r"""^(RVRNO |
                              R(?P<name>\d\d(RR?|LL?|C)?)/
                              (?P<low>(M|P)?\d\d\d\d)
                              (V(?P<high>(M|P)?\d\d\d\d))?
                              (?P<unit>FT)?[/NDU]*)\s+""",
                              re.VERBOSE)
WEATHER_RE = re.compile(r"""^(?P<int>(-|\+|VC)*)
                             (?P<desc>(MI|PR|BC|DR|BL|SH|TS|FZ)+)?
                             (?P<prec>(DZ|RA|SN|SG|IC|PL|GR|GS|UP|/)*)
                             (?P<obsc>BR|FG|FU|VA|DU|SA|HZ|PY)?
                             (?P<other>PO|SQ|FC|SS|DS|NSW|/+)?
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
RUNWAYSTATE_RE = re.compile(r"""(R(?P<name>\d\d(RR?|LL?|C)?))?/?
                               ((?P<special>SNOCLO|(CLRD(?P<cldr_fric>\d\d|//)?)) |
                               ((?P<deposit>(\d|/))
                               (?P<extent>(\d|/))
                               (?P<depth>(\d\d|//))
                               (?P<friction>(\d\d|//))))\s+""",
                           re.VERBOSE)
TREND_RE = re.compile(r"^(?P<trend>TEMPO|BECMG|FCST|NOSIG)\s+")

TRENDTIME_RE = re.compile(r"(?P<when>(FM|TL|AT))(?P<hour>\d\d)(?P<min>\d\d)\s+")

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
              ("VC", "nearby") ]

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

RWY_DEPOSIT = { "0": "Clear and dry",
                "1": "Damp",
                "2": "Wet or water patches",
                "3": "Rime or frost covered",
                "4": "Dry snow",
                "5": "Wet snow",
                "6": "Slush",
                "7": "Ice",
                "8": "compacted or rolled snow",
                "9": "frozen ruts or ridges",
                "/": "not reported"}

RWY_BRAKING_ACTION = { "91": "poor",
                       "92": "med/poor",
                       "93": "medium",
                       "94": "med/good",
                       "95": "good",
                       "96": "unreliable",
                       "//": "not reported"}

RWY_EXTCONTAMIN = {"1": r"10% or less",
                   "2": r"11% to 25%",
                   "5": r"26% to 50%",
                   "9": r"51% to 100%",
                   "/": r"not reported"}

RWY_DEPTHDEPOSIT = {"00": "less than 1mm",
                    "91": "not used",
                    "92": "10cm",
                    "93": "15cm",
                    "94": "20cm",
                    "95": "25cm",
                    "96": "30cm",
                    "97":"35cm",
                    "98": "40cm or more",
                    "99": "non-operational due to snow or runway clearance; depth not reported",
                    "//": "depth of deposit operationally not significant or measurable"}

## Helper functions

def _report_match(handler,match):
  """Report success or failure of the given handler function. (DEBUG)"""
  if match:
      print handler.__name__," matched '"+match+"'"
  else:
      print handler.__name__," didn't match..."

def _unparsedGroup( self, d ):
    """
    Handle otherwise unparseable main-body groups.
    """
    self._unparsed_groups.append(d['group'])

## METAR report objects

debug = False

class Metar(object):
  """METAR (aviation meteorology report)"""

  def __init__( self, metarcode, month=None, year=None, utcdelta=None):
      """Parse raw METAR code."""
      self.code = metarcode.strip()      # original METAR code with leading and trailing whitespace removed
      self.type = 'METAR'                # METAR (routine) or SPECI (special)
      self.mod = None                    # AUTO (automatic) or COR (corrected)
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
      self.runway_st = []                # runway state (list of tuples)
      self.weather = []                  # present weather (list of tuples)
      self.recent = []                   # recent weather (list of tuples)
      self.sky = []                      # sky conditions (list of tuples)
      self.windshear = []                # runways w/ wind shear (list of strings)
      self.wind_speed_peak = None        # peak wind speed in last hour
      self.wind_dir_peak = None          # direction of peak wind speed in last hour
      self.peak_wind_time = None         # time of peak wind observation [datetime]
      self.wind_shift_time = None        # time of wind shift [datetime]
      self.max_temp_6hr = None           # max temp in last 6 hours
      self.min_temp_6hr = None           # min temp in last 6 hours
      self.max_temp_24hr = None          # max temp in last 24 hours
      self.min_temp_24hr = None          # min temp in last 24 hours
      self.press_sea_level = None        # sea-level pressure
      self.precip_1hr = None             # precipitation over the last hour
      self.precip_3hr = None             # precipitation over the last 3 hours
      self.precip_6hr = None             # precipitation over the last 6 hours
      self.precip_24hr = None            # precipitation over the last 24 hours
      self._trend = False                 # trend groups present (bool)
      self._trend_groups = []            # trend forecast groups
      self._remarks = []                 # remarks (list of strings)
      self._unparsed_groups = []
      self._unparsed_remarks = []

      self._now = datetime.datetime.utcnow()
      if utcdelta:
          self._utcdelta = utcdelta
      else:
          self._utcdelta = datetime.datetime.now() - self._now

      self._month = month
      self._year = year

      code = self.code+" "    # (the regexps all expect trailing spaces...)
      try:
          ngroup = len(Metar.handlers)
          igroup = 0
          ifailed = -1
          while igroup < ngroup and code:
              pattern, handler, repeatable = Metar.handlers[igroup]
              if debug: print handler.__name__,":",code
              m = pattern.match(code)
              while m:
                  ifailed = -1
                  if debug: _report_match(handler,m.group())
                  handler(self,m.groupdict())
                  code = code[m.end():]
                  if self._trend:
                      code = self._do_trend_handlers(code)
                  if not repeatable: break

                  if debug: print handler.__name__,":",code
                  m = pattern.match(code)
              if not m and ifailed < 0:
                  ifailed = igroup
              igroup += 1
              if igroup == ngroup and not m:
                  # print "** it's not a main-body group **"
                  pattern, handler = (UNPARSED_RE, _unparsedGroup)
                  if debug: print handler.__name__,":",code
                  m = pattern.match(code)
                  if debug: _report_match(handler,m.group())
                  handler(self,m.groupdict())
                  code = code[m.end():]
                  igroup = ifailed
                  ifailed = -2  # if it's still -2 when we run out of main-body
                                #  groups, we'll try parsing this group as a remark
          if pattern == REMARK_RE or self.press:
              while code:
                  for pattern, handler in Metar.remark_handlers:
                      if debug: print handler.__name__,":",code
                      m = pattern.match(code)
                      if m:
                          if debug: _report_match(handler,m.group())
                          handler(self,m.groupdict())
                          code = pattern.sub("",code,1)
                          break

      except Exception, err:
          raise ParserError(handler.__name__+" failed while processing '"+code+"'\n"+string.join(err.args))
          raise err
      if self._unparsed_groups:
          code = ' '.join(self._unparsed_groups)
          #uncomment next line to raise error
          #raise ParserError("Unparsed groups in body: "+code)

  def _do_trend_handlers(self, code):
      for pattern, handler, repeatable in Metar.trend_handlers:
          if debug: print handler.__name__,":",code
          m = pattern.match(code)
          while m:
              if debug: _report_match(handler, m.group())
              self._trend_groups.append(string.strip(m.group()))
              handler(self,m.groupdict())
              code = code[m.end():]
              if not repeatable: break
              m = pattern.match(code)
      return code

  def __str__(self):
      return self.string()

  def _handleType( self, d ):
      """
      Parse the code-type group.

      The following attributes are set:
          type   [string]
      """
      self.type = d['type']

  def _handleStation( self, d ):
      """
      Parse the station id group.

      The following attributes are set:
          station_id   [string]
      """
      self.station_id = d['station']

  def _handleModifier( self, d ):
      """
      Parse the report-modifier group.

      The following attributes are set:
          mod   [string]
      """
      mod = d['mod']
      if mod == 'CORR': mod = 'COR'
      if mod == 'NIL' or mod == 'FINO': mod = 'NO DATA'
      self.mod = mod

  def _handleTime( self, d ):
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
      if not self._month:
          self._month = self._now.month
          if self._day > self._now.day:
              if self._month == 1:
                  self._month = 12
              else:
                  self._month = self._month - 1
      if not self._year:
          self._year = self._now.year
          if self._month > self._now.month:
              self._year = self._year - 1
          elif self._month == self._now.month and self._day > self._now.day:
              self._year = self._year - 1
      self._hour = int(d['hour'])
      self._min = int(d['min'])
      self.time = datetime.datetime(self._year, self._month, self._day,
                                                                  self._hour, self._min)
      if self._min < 45:
          self.cycle = self._hour
      else:
          self.cycle = self._hour+1

  def _handleWind( self, d ):
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
      if wind_dir != "VRB" and wind_dir != "///" and wind_dir != "MMM":
          self.wind_dir = direction(wind_dir)
      wind_speed = d['speed'].replace('O','0')
      units = d['units']
      if units == 'KTS' or units == 'K' or units == 'T' or units == 'LT':
          units = 'KT'
      if wind_speed.startswith("P"):
          self.wind_speed = speed(wind_speed[1:], units, ">")
      elif not MISSING_RE.match(wind_speed):
          self.wind_speed = speed(wind_speed, units)
      if d['gust']:
          wind_gust = d['gust']
          if wind_gust.startswith("P"):
              self.wind_gust = speed(wind_gust[1:], units, ">")
          elif not MISSING_RE.match(wind_gust):
              self.wind_gust = speed(wind_gust, units)
      if d['varfrom']:
          self.wind_dir_from = direction(d['varfrom'])
          self.wind_dir_to = direction(d['varto'])

  def _handleVisibility( self, d ):
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
      if d['dist'] and d['dist'] != '////':
          vis_dist = d['dist']
          if d['dir'] and d['dir'] != 'NDV':
              vis_dir = d['dir']
      elif d['distu']:
          vis_dist = d['distu']
          if d['units'] and d['units'] != "U":
                  vis_units = d['units']
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

  def _handleRunway( self, d ):
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

  def _handleRunwayState( self, d ):
      """
      Parse the runway state.

      The following attributes are set:
          runway state [list of tuples]
          . name       [string]
          . deposit    [string]
          . extent     [string]
          . depth      [string]
          . friction   [string]
      """
      if d['name']:
          name = d['name']
          if name == '99':
              name = 'Repetition of the last message as no new information received'

          elif name == '88':
              name = 'All runways'

          if d['special']:
              special = d['special']
              if 'SNOCLO' in special:
                  special = 'The aerodrome is closed due to contamination of the runways'

              elif 'CLRD' in special:
                  cldr_fric = d['cldr_fric']
                  if cldr_fric in [str(i) for i in range(91)]:
                      cldr_fric = "friction coefficient %s" % (cldr_fric)

                  else:
                      cldr_fric = RWY_BRAKING_ACTION.get(d['cldr_fric'], None)
                      if cldr_fric:
                          cldr_fric = "braking action %s" % (cldr_fric)

                  special = "Contamination has been cleared, %s" % (str(cldr_fric))

              self.runway_st.append((name,special))

          else:
              deposit = RWY_DEPOSIT.get(d['deposit'], None)
              extent = RWY_EXTCONTAMIN.get(d['extent'], None)
              friction = None

              if d['depth'] in [str(i) for i in range(1,91)]:
                  depth = "%smm" % (d['depth'])
              else:
                  depth = RWY_DEPTHDEPOSIT.get(d['depth'], None)

              if d['friction'] in [str(i) for i in range(1,91)]:
                  friction = r"friction coefficient %s%" % (d['friction'])

              else:
                  friction = RWY_BRAKING_ACTION.get(d['friction'], None)
                  if friction:
                      friction = "braking action %s" % (friction)

              self.runway_st.append((name,deposit,extent,depth,friction))

  def _handleWeather( self, d ):
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

  def _handleSky( self, d ):
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

  def _handleTemp( self, d ):
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

  def _handlePressure( self, d ):
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

  def _handleRecent( self, d ):
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

  def _handleWindShear( self, d ):
      """
      Parse wind-shear groups.

      The following attributes are set:
          windshear    [list of strings]
      """
      if d['name']:
          self.windshear.append(d['name'])
      else:
          self.windshear.append("ALL")

  def _handleColor( self, d ):
      """
      Parse (and ignore) the color groups.

      The following attributes are set:
          trend    [list of strings]
      """
      pass

  def _handleTrend( self, d ):
      """
      Parse (and ignore) the trend groups.
      """
      if d.has_key('trend'):
          self._trend_groups.append(d['trend'])
      self._trend = True

  def _startRemarks( self, d ):
      """
      Found the start of the remarks section.
      """
      self._remarks = []

  def _handleSealvlPressRemark( self, d ):
      """
      Parse the sea-level pressure remark group.
      """
      value = float(d['press'])/10.0
      if value < 50:
          value += 1000
      else:
          value += 900
      #if not self.press:
          #self.press = pressure(value,"MB")
      self._remarks.append('sea pressure level: %s' % (pressure(value,"MB")))

  def _handlePrecip24hrRemark( self, d ):
      """
      Parse a 3-, 6- or 24-hour cumulative preciptation remark group.
      """
      value = float(d['precip'])/100.0
      if d['type'] == "6":
          if self.cycle == 3 or self.cycle == 9 or self.cycle == 15 or self.cycle == 21:
              self._remarks.append('precip_3hr: %s' % (precipitation(value,"IN")))
          else:
              self._remarks.append('precip_6hr: %s' % (precipitation(value,"IN")))
      else:
          self._remarks.append('precip_24hr: %s' % (precipitation(value,"IN")))

  def _handlePrecip1hrRemark( self, d ):
      """Parse an hourly precipitation remark group."""
      value = float(d['precip'])/100.0
      self._remarks.append('precip_1hr: %s' % (precipitation(value,"IN")))

  def _handleTemp1hrRemark( self, d ):
      """
      Parse a temperature & dewpoint remark group.

      These values replace the temp and dewpt from the body of the report.
      """
      value = float(d['temp'])/10.0
      if d['tsign'] == "1": value = -value
      self._remarks.append('temperature: %s' % (temperature(value)))
      if d['dewpt']:
          value2 = float(d['dewpt'])/10.0
          if d['dsign'] == "1": value2 = -value2
          self._remarks.append('dew point: %s' % (temperature(value2)))

  def _handleTemp6hrRemark( self, d ):
      """
      Parse a 6-hour maximum or minimum temperature remark group.
      """
      value = float(d['temp'])/10.0
      if d['sign'] == "1": value = -value
      if d['type'] == "1":
          self._remarks.append('max_temp_6hr: %s' % (temperature(value,"C")))
      else:
          self._remarks.append('min_temp_6hr: %s' % (temperature(value,"C")))

  def _handleTemp24hrRemark( self, d ):
      """
      Parse a 24-hour maximum/minimum temperature remark group.
      """
      value = float(d['maxt'])/10.0
      if d['smaxt'] == "1": value = -value
      value2 = float(d['mint'])/10.0
      if d['smint'] == "1": value2 = -value2
      self._remarks.append('max_temp_24hr: %s' % (temperature(value,"C")))
      self._remarks.append('min_temp_24hr: %s' % (temperature(value2,"C")))

  def _handlePress3hrRemark( self, d ):
      """
      Parse a pressure-tendency remark group.
      """
      value = float(d['press'])/10.0
      descrip = PRESSURE_TENDENCY[d['tend']]
      self._remarks.append("3-hr pressure change %.1fhPa, %s" % (value,descrip))

  def _handlePeakWindRemark( self, d ):
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
      self.peak_wind_time = datetime.datetime(self._year, self._month, self._day,
                                                                  peak_hour, peak_min)
      if self.peak_wind_time > self.time:
          if peak_hour > self._hour:
              self.peak_wind_time -= datetime.timedelta(hours=24)
          else:
              self.peak_wind_time -= datetime.timedelta(hours=1)
      self._remarks.append("peak wind %dkt from %d degrees at %d:%02d" % \
                                              (peak_speed, peak_dir, peak_hour, peak_min))

  def _handleWindShiftRemark( self, d ):
      """
      Parse a wind shift remark group.
      """
      if d['hour']:
          wshft_hour = int(d['hour'])
      else:
          wshft_hour = self._hour
      wshft_min = int(d['min'])
      self.wind_shift_time = datetime.datetime(self._year, self._month, self._day,
                                                                  wshft_hour, wshft_min)
      if self.wind_shift_time > self.time:
          if wshft_hour > self._hour:
              self.wind_shift_time -= datetime.timedelta(hours=24)
          else:
              self.wind_shift_time -= datetime.timedelta(hours=1)
      text = "wind shift at %d:%02d" %  (wshft_hour, wshft_min)
      if d['front']:
          text += " (front)"
      self._remarks.append(text)

  def _handleLightningRemark( self, d ):
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

  def _handleTSLocRemark( self, d ):
      """
      Parse a thunderstorm location remark group.
      """
      text = "thunderstorm"
      if d['loc']:
          text += " "+xlate_loc(d['loc'])
      if d['dir']:
          text += " moving %s" % d['dir']
      self._remarks.append(text)

  def _handleAutoRemark( self, d ):
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
      self._unparsed_remarks.append(d['group'])

  ## the list of handler functions to use (in order) to process a METAR report

  handlers = [ (TYPE_RE, _handleType, False),
               (STATION_RE, _handleStation, False),
               (TIME_RE, _handleTime, False),
               (MODIFIER_RE, _handleModifier, False),
               (WIND_RE, _handleWind, False),
               (VISIBILITY_RE, _handleVisibility, True),
               (RUNWAY_RE, _handleRunway, True),
               (WEATHER_RE, _handleWeather, True),
               (SKY_RE, _handleSky, True),
               (TEMP_RE, _handleTemp, False),
               (PRESS_RE, _handlePressure, True),
               (RECENT_RE,_handleRecent, True),
               (WINDSHEAR_RE, _handleWindShear, True),
               (COLOR_RE, _handleColor, True),
               (RUNWAYSTATE_RE, _handleRunwayState, True),
               (TREND_RE, _handleTrend, True),
               (REMARK_RE, _startRemarks, False) ]

  trend_handlers = [ (TRENDTIME_RE, _handleTrend, False),
                     (WIND_RE, _handleTrend, False),
                     (VISIBILITY_RE, _handleTrend, False),
                     (WEATHER_RE, _handleTrend, False),
                     (SKY_RE, _handleTrend, False),
                     (COLOR_RE, _handleTrend, False)]

  ## the list of patterns for the various remark groups,
  ## paired with the handler functions to use to record the decoded remark.

  remark_handlers = [ (AUTO_RE,         _handleAutoRemark),
                      (SEALVL_PRESS_RE, _handleSealvlPressRemark),
                      (PEAK_WIND_RE,    _handlePeakWindRemark),
                      (WIND_SHIFT_RE,   _handleWindShiftRemark),
                      (LIGHTNING_RE,    _handleLightningRemark),
                      (TS_LOC_RE,       _handleTSLocRemark),
                      (TEMP_1HR_RE,     _handleTemp1hrRemark),
                      (PRECIP_1HR_RE,   _handlePrecip1hrRemark),
                      (PRECIP_24HR_RE,  _handlePrecip24hrRemark),
                      (PRESS_3HR_RE,    _handlePress3hrRemark),
                      (TEMP_6HR_RE,     _handleTemp6hrRemark),
                      (TEMP_24HR_RE,    _handleTemp24hrRemark),
                      (UNPARSED_RE,     _unparsedRemark) ]

  ## functions that return text representations of conditions for output

  def string( self, metar_code=True ):
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
      if self.wind_shift_time:
          lines.append("wind shift: %s" % self.wind_shift())
      if self.vis:
          lines.append("visibility: %s" % self.visibility())
      if self.runway:
          lines.append("visual range: %s" % self.runway_visual_range())
      if self.runway:
          lines.append("runway state: %s" % self.runway_state())
      if self.press:
          lines.append("pressure: %s" % self.press.string("mb"))
      if self.weather:
          lines.append("weather: %s" % self.present_weather())
      if self.sky:
          lines.append("sky: %s" % self.sky_conditions("\n     "))
      if self.press_sea_level:
          lines.append("sea-level pressure: %s" % self.press_sea_level.string("mb"))
      if self.max_temp_6hr:
          lines.append("6-hour max temp: %s" % str(self.max_temp_6hr))
      if self.max_temp_6hr:
          lines.append("6-hour min temp: %s" % str(self.min_temp_6hr))
      if self.max_temp_24hr:
          lines.append("24-hour max temp: %s" % str(self.max_temp_24hr))
      if self.max_temp_24hr:
          lines.append("24-hour min temp: %s" % str(self.min_temp_24hr))
      if self.precip_1hr:
          lines.append("1-hour precipitation: %s" % str(self.precip_1hr))
      if self.precip_3hr:
          lines.append("3-hour precipitation: %s" % str(self.precip_3hr))
      if self.precip_6hr:
          lines.append("6-hour precipitation: %s" % str(self.precip_6hr))
      if self.precip_24hr:
          lines.append("24-hour precipitation: %s" % str(self.precip_24hr))
      if self._remarks:
          lines.append("remarks:")
          lines.append(" - "+self.remarks("\n - "))
      if self._trend:
          lines.append("Trend: " + self.trend())
      if self._unparsed_groups:
          lines.append("unparsed code: " + ' '.join(self._unparsed_groups))
      if self._unparsed_remarks:
          lines.append("unparsed remarks:")
          lines.append(" - " + ' '.join(self._unparsed_remarks))
      if metar_code:
          lines.append("METAR: " + self.code)

      return string.join(lines,"\n")

  def json( self, metar_code=True ):
    json = {"station":"", "type":"", "time":"", "temperature":"", "dew point":"",
            "wind":"", "peak wind":"", "wind shift":"", "visibility":"",
            "visual range":"", "runway state": "","pressure":"", "weather": "", "sky":"",
            "sea-level pressure":"","6-hour max temp":"", "6-hour min temp":"",
            "24-hour max temp":"", "24-hour min temp":"", "1-hour precipitation":"",
            "3-hour precipitation":"", "6-hour precipitation":"", "24-hour precipitation":"",
            "remarks":"","Trend":"", "unparsed code":"", "unparsed remarks":"", "METAR":""}

    json["station"] = self.station_id
    if self.type:
        json["type"] = self.report_type()
    if self.time:
        json["time"] = self.time.ctime()
    if self.temp:
        json["temperature"] = self.temp.string("C")
    if self.dewpt:
        json["dew point"] = self.dewpt.string("C")
    if self.wind_speed:
        json["wind"] = self.wind()
    if self.wind_speed_peak:
        json["peak wind"] = self.peak_wind()
    if self.wind_shift_time:
        json["wind shift"] = self.wind_shift()
    if self.vis:
        json["visibility"] = self.visibility()
    if self.runway:
        json["visual range"] = self.runway_visual_range()
    if self.runway_st:
        json["runway state"] = self.runway_state()
    if self.press:
        json["pressure"] = self.press.string("mb")
    if self.weather:
        json["weather"] = self.present_weather()
    if self.sky:
        json["sky"] = self.sky_conditions("\n")
    if self.press_sea_level:
        json["sea-level pressure"] = self.press_sea_level.string("mb")
    if self.max_temp_6hr:
        json["6-hour max temp"] = str(self.max_temp_6hr)
    if self.max_temp_6hr:
        json["6-hour min temp"] = str(self.min_temp_6hr)
    if self.max_temp_24hr:
        json["24-hour max temp"] = str(self.max_temp_24hr)
    if self.max_temp_24hr:
        json["24-hour min temp"] = str(self.min_temp_24hr)
    if self.precip_1hr:
        json["1-hour precipitation"] = str(self.precip_1hr)
    if self.precip_3hr:
        json["3-hour precipitation"] = str(self.precip_3hr)
    if self.precip_6hr:
        json["6-hour precipitation"] =  str(self.precip_6hr)
    if self.precip_24hr:
        json["24-hour precipitation"] = str(self.precip_24hr)
    if self._remarks:
        json["remarks"] = " - "+self.remarks("\n - ")
    if self._trend:
        json["Trend"] = self.trend()
    if self._unparsed_groups:
        json["unparsed code"] = ' '.join(self._unparsed_groups)
    if self._unparsed_remarks:
        json["unparsed remarks"] = ' '.join(self._unparsed_remarks)
    if metar_code:
        json["METAR"] = self.code

    return json

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
              if not self.peak_wind_time == None:
                  text += " at %s" % self.peak_wind_time.strftime('%H:%M')
      return text

  def wind_shift( self, units="KT" ):
      """
      Return a textual description of the wind shift time

      Units may be specified as "MPS", "KT", "KMH", or "MPH".
      """
      if self.wind_shift_time == None:
          return "missing"
      else:
          return self.wind_shift_time.strftime('%H:%M')

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
              text += "; %s" % self.max_vis.string(units)
      return text

  def runway_visual_range( self, units=None ):
      """
      Return a textual description of the runway visual range.
      """
      lines = []
      for name,low,high in self.runway:
          if low != high:
              lines.append("on runway %s, from %d to %s" % (name, low.value(units), high.string(units)))
          else:
              lines.append("on runway %s, %s" % (name, low.string(units)))
      return string.join(lines,"; ")

  def runway_state( self ):
      """
      Return a textual description of the runway state.
      """
      lines = []
      for rwy in self.runway_st:
          if len(rwy) > 2:
              name,deposit,extent,depth,friction = rwy
              lines.append("On runway: %s, Deposits: %s, Extent of contamination: %s, Depth of deposit: %s, %s" % (name,deposit,extent,depth,friction))
          else:
              name,special = rwy
              lines.append("On runway: %s, %s" % (name,special))
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
              precip_text = ""
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
                          (SKY_COVER[cover],what,str(height)))
              else:
                  text_list.append("%s%s at %s" %
                          (SKY_COVER[cover],what,str(height)))
      return string.join(text_list,sep)

  def trend( self ):
      """
      Return the trend forecast groups
      """
      if 'NOSIG' in self._trend_groups:
          self._trend_groups[self._trend_groups.index('NOSIG')] = 'No significant changes is expected'
          trend_str = " ".join(self._trend_groups)
      elif 'TEMPO' in self._trend_groups:
          self._trend_groups[self._trend_groups.index('TEMPO')] = 'Temporary changes'
          trend_str = " ".join(self._trend_groups)
      elif 'BECMG' in self._trend_groups:
          self._trend_groups[self._trend_groups.index('BECMG')] = 'Becoming changes'
          trend_str = " ".join(self._trend_groups)
      else:
          trend_str = " ".join(self._trend_groups)
      return trend_str

  def remarks( self, sep="; "):
      """
      Return the decoded remarks.
      """
      return string.join(self._remarks,sep)
