# Setup script for the metar package
# $Id: setup.py,v 1.1 2005/01/26 22:30:09 pollard Exp $
#
# Usage: python setup.py install
#
from distutils.core import setup

try:
    # add download_url syntax to distutils
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
except:
    pass

DESCRIPTION="Metar - a package to parse METAR coded weather reports"

LONG_DESCRIPTION="""
Metar is a python package for interpreting METAR and SPECI weather reports.

US conventions for METAR/SPECI reports are described in chapter 12 of
the Federal Meteorological Handbook No.1. (FMH-1 1995), issued by NOAA. 
See <http://metar.noaa.gov/>

International conventions for the METAR and SPECI codes are specified in 
the WMO Manual on Codes, vol I.1, Part A (WMO-306 I.i.A).  

This module handles a reports that follow the US conventions, as well
the more general encodings in the WMO spec.  Other regional conventions
are not supported at present.
"""

setup(
    name="metar",
    version="1.1.0",
    author="Tom Pollard",
    author_email="pollard@alumni.mit.edu",
    url="",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    download_url="http://homepage.mac.com/wtpollard/Software/FileSharing4.html",
    license="BSD-style",
    packages=["metar"],
    platforms="Python 2.3 and later.",
    classifiers=[
    "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering"
        ]
    )
