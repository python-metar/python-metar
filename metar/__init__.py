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

#import Datatypes
#import Metar
#import Station
#import Graphics

import sys
import os
from warnings import simplefilter

from numpy import errstate
import numpy.testing as nptest
from numpy.testing.noseclasses import NumpyTestProgram

from .station import *
from .graphics import *
from .exporters import *
from . import ncdc

def _show_package_info(package, name):
    print("%s version %s" % (name, package.__version__))
    packagedir = os.path.dirname(package.__file__)
    print("%s is installed in %s" % (name, packagedir))

class NoseWrapper(nptest.Tester):
    '''
    This is simply a monkey patch for numpy.testing.Tester.

    It allows extra_argv to be changed from its default None to ['--exe'] so
    that the tests can be run the same across platforms.  It also takes kwargs
    that are passed to numpy.errstate to suppress floating point warnings.
    '''


    def _show_system_info(self):
        import nose

        pyversion = sys.version.replace('\n','')
        print("Python version %s" % pyversion)
        print("nose version %d.%d.%d" % nose.__versioninfo__)

        import numpy
        _show_package_info(numpy, 'numpy')

        import scipy
        _show_package_info(scipy, 'scipy')

        import matplotlib
        _show_package_info(matplotlib, 'matplotlib')

        import pandas
        _show_package_info(pandas, 'pandas')

        import openpyxl
        _show_package_info(openpyxl, 'openpyxl')

    def test(self, label='fast', verbose=1, extra_argv=['--exe'], doctests=False,
             coverage=False, packageinfo=True, **kwargs):
        '''
        Run tests for module using nose

        %(test_header)s
        doctests : boolean
            If True, run doctests in module, default False
        coverage : boolean
            If True, report coverage of NumPy code, default False
            (Requires the coverage module:
             http://nedbatchelder.com/code/modules/coverage.html)
        kwargs
            Passed to numpy.errstate.  See its documentation for details.
        '''

        # cap verbosity at 3 because nose becomes *very* verbose beyond that
        verbose = min(verbose, 3)
        nptest.utils.verbose = verbose

        if packageinfo:
            self._show_system_info()

        if doctests:
            print("Running unit tests and doctests for %s" % self.package_name)
        else:
            print("Running unit tests for %s" % self.package_name)

        # reset doctest state on every run
        import doctest
        doctest.master = None

        argv, plugins = self.prepare_test_args(label, verbose, extra_argv,
                                               doctests, coverage)

        with errstate(**kwargs):
##            with catch_warnings():
            simplefilter('ignore', category=DeprecationWarning)
            t = NumpyTestProgram(argv=argv, exit=False, plugins=plugins)
        return t.result

test = NoseWrapper().test
