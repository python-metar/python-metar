#!/usr/bin/python
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
#  Copyright 2004-2009  Tom Pollard
#  All rights reserved.
# 
__author__ = "Tom Pollard"

__email__ = "pollard@alum.mit.edu"

__version__ = "1.4"

__doc__ = """metar v%s (c) 2009, %s

Metar is a python package that interprets coded METAR and SPECI weather reports.

Please e-mail bug reports to: %s""" % (__version__, __author__,__email__)

__LICENSE__ = """
Copyright (c) 2009, %s
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.


THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""" % __author__

