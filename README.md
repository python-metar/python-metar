[![Build Status](https://travis-ci.org/phobson/python-metar.png?branch=master)](https://travis-ci.org/phobson/python-metar)

========================================================================
The metar library
========================================================================

Python-metar is a python package for interpreting METAR and SPECI coded
weather reports. 

METAR and SPECI are coded aviation weather reports.  The official
coding schemes are specified in the World Meteorological Organization
(WMO) Manual on Codes, vol I.1, Part A (WMO-306 I.i.A).  US conventions
for METAR/SPECI reports vary in a number of ways from the international
standard, and are described in chapter 12 of the Federal Meteorological
Handbook No.1. (FMH-1 1995), issued by the National Oceanic and
Atmospheric Administration (NOAA).  General information about the
use and history of the METAR standard can be found at

    http://www.ncdc.noaa.gov/oa/wdc/metar/

This module extracts the data recorded in the main-body groups of
reports that follow the WMO spec or the US conventions, except for
the runway state and trend groups, which are parsed but ignored.
The most useful remark groups defined in the US spec are parsed,
as well, such as the cumulative precipitation, min/max temperature,
peak wind and sea-level pressure groups.  No other regional conventions
are formally supported, but a large number of variant formats found
in international reports are accepted.

Current METAR reports
---------------------
Current and historical METAR data can be obtained from various places.
The current METAR report for a given airport is available at the URL

    http://weather.noaa.gov/pub/data/observations/metar/stations/<station>.TXT

where <station> is the four-letter ICAO airport station code.  The 
accompanying script get_report.py will download and decode the
current report for any specified station.  

The METAR reports for all stations (worldwide) for any "cycle" (i.e., hour) 
in the last 24 hours are available in a single file at the URL

   http://weather.noaa.gov/pub/data/observations/metar/cycles/<cycle>Z.TXT

where <cycle> is a 2-digit cycle number (e.g., "00", "05" or "23").  

METAR specifications
--------------------
The Federal Meteorological Handbook No.1. (FMH-1 1995), which
describes the U.S. standards, is available online at

   http://www.ofcm.gov/fmh-1/fmh1.htm

The World Meteorological Organization (WMO) Manual on Codes, vol I.1, 
Part A (WMO-306 I.i.A) can be downloaded from site I use to distribute
this package,

   http://homepage.mac.com/wtpollard/Software/FileSharing4.html.


Tom Pollard
pollard@alum.mit.edu
May 2, 2009

------------------------------------------------------------------------
Installation
------------------------------------------------------------------------

Install this package in the usual way,

    python setup.py install

There's a small, inadequate test suite that can be run by saying

    python test/all_tests.py

There are a couple of sample scripts, described briefly below.

There's no real documentation to speak of, yet, but feel free to
contact me with any questions you might have about how to use this package.

Current sources
---------------
You can always obtain the most recent version of this package using git, via

    git clone git://github.com/tomp/python-metar.git

This is a public copy of the code repository I use for development.
Thanks to Toby White for making me aware of github.

------------------------------------------------------------------------
Contents
------------------------------------------------------------------------

README  ............... this file

parse_metar.py  ....... a simple commandline driver for the METAR parser

get_report.py ......... a script to download and decode the current reports
                        for one or more stations.

sample.py  ............ a simple script showing how the decoded data 
                        can be accessed. (see metar/*.py sources and the
                        test/test_*.py scripts for more examples.)

sample.metar  ......... a sample METAR report (longer than most).  Try
                        feeding this to the parse_metar.py script...
metar/
    Metar.py  ......... the implementation of the Metar class.  This class
                        parses and represents a single METAR report.

    Datatypes.py  ..... a support module that defines classes representing 
                        different types of meteorological data, including
                        temperature, pressure, speed, distance, direction 
                        and position.
test/
    all_tests.py  ..... a master test driver, which invokes all of the unit tests

    test_*.py  ........ individual test modules

setup.py  ............. installation script

------------------------------------------------------------------------
Example
------------------------------------------------------------------------

See the sample.py script for an annonated demonstration of the use
of this code.  Just as an appetizer, here's an interactive example...

>>> from metar import Metar
>>> obs = Metar.Metar('METAR KEWR 111851Z VRB03G19KT 2SM R04R/3000VP6000FT TSRA BR FEW015 BKN040CB BKN065 OVC200 22/22 A2987 RMK AO2 PK WND 29028/1817 WSHFT 1812 TSB05RAB22 SLP114 FRQ LTGICCCCG TS OHD AND NW -N-E MOV NE P0013 T02270215')
>>> print obs.string()
station: KEWR
type: routine report, cycle 19 (automatic report)
time: Tue Jan 11 18:51:00 2005
temperature: 22.7 C
dew point: 21.5 C
wind: variable at 3 knots, gusting to 19 knots
peak wind: WNW at 28 knots
visibility: 2 miles
visual range: runway 04R: 3000 meters to greater than 6000 meters feet
pressure: 1011.5 mb
weather: thunderstorm with rain; mist
sky: a few clouds at 1500 feet
     broken cumulonimbus at 4000 feet
     broken clouds at 6500 feet
     overcast at 20000 feet
sea-level pressure: 1011.4 mb
1-hour precipitation: 0.13in
remarks:
- Automated station (type 2)
- peak wind 28kt from 290 degrees at 18:17
- wind shift at 18:12
- frequent lightning (intracloud,cloud-to-cloud,cloud-to-ground)
- thunderstorm overhead and NW
- TSB05RAB22 -N-E MOV NE
METAR: METAR KEWR 111851Z VRB03G19KT 2SM R04R/3000VP6000FT TSRA BR FEW015 BKN040CB BKN065 OVC200 22/22 A2987 RMK AO2 PK WND 29028/1817 WSHFT 1812 TSB05RAB22 SLP114 FRQ LTGICCCCG TS OHD AND NW -N-E MOV NE P0013 T02270215
>>>>

------------------------------------------------------------------------
LICENSE
------------------------------------------------------------------------
The metar library is

Copyright (c) 2004-2009, Tom Pollard
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

  Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.

------------------------------------------------------------------------
