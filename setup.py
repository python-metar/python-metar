"""Setup script for the metar package.

    Usage: python setup.py install
"""
from setuptools import setup
from metar import __version__

DESCRIPTION = "Metar - a package to parse METAR-coded weather reports"

LONG_DESCRIPTION = """
Metar is a python package for interpreting METAR and SPECI weather reports.

METAR is an international format for reporting weather observations.
The standard specification for the METAR and SPECI codes is given
in the WMO Manual on Codes, vol I.1, Part A (WMO-306 I.i.A).  US
conventions for METAR/SPECI reports are described in chapter 12 of
the Federal Meteorological Handbook No.1. (FMC-H1-2017), issued by
NOAA.  See http://www.ofcm.gov/publications/fmh/FMH1/FMH1.pdf

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
    version=__version__,
    author="Tom Pollard",
    author_email="pollard@alum.mit.edu",
    url="https://github.com/python-metar/python-metar",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license="BSD",
    packages=["metar"],
    package_data={"metar": ["nsd_cccc.txt"]},
    platforms="Python 2.5 and later.",
    extras_require={"test": ["pytest"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
