# Setup script for the metar package
# $Id: setup.py,v 1.3 2006/08/01 16:10:29 pollard Exp $
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

METAR is an international format for reporting weather observations.
The standard specification for the METAR and SPECI codes is given
in the WMO Manual on Codes, vol I.1, Part A (WMO-306 I.i.A).  US
conventions for METAR/SPECI reports are described in chapter 12 of
the Federal Meteorological Handbook No.1. (FMH-1 1995), issued by
NOAA.  See http://www.ncdc.noaa.gov/oa/wdc/metar/

This module extracts the data recorded in the main-body groups of
reports that follow the WMO spec or the US conventions, except for
the runway state and trend groups, which are parsed but ignored.
The most useful remark groups defined in the US spec are parsed,
as well, such as the cumulative precipitation, min/max temperature,
peak wind and sea-level pressure groups.  No other regional conventions
are formally supported, but a large number of variant formats found
in international reports are accepted."""

setup(
    name="metar",
    version="1.4.0",
    author="Tom Pollard",
    author_email="pollard@alum.mit.edu",
    url="http://python-metar.sourceforge.net/",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    download_url="http://sourceforge.net/project/platformdownload.php?group_id=134052",
    license="MIT",
    packages=["metar"],
    platforms="Python 2.5 and later.",
    classifiers=[
        "Development Status :: 5 - Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Intended Audience :: Science/Research",
#        "Topic :: Formats and Protocols :: Data Formats",
#        "Topic :: Scientific/Engineering :: Earth Sciences",
#        "Topic :: Software Development :: Libraries :: Python Modules"
        ]
    )
