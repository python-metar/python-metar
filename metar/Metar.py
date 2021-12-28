# Copyright (c) 2004,2018 Python-Metar Developers.
# Distributed under the terms of the BSD 2-Clause License.
# SPDX-License-Identifier: BSD-2-Clause
"""This module defines the Metar class.

A Metar object represents the weather report encoded by a single METAR code.
"""
import re
import datetime
import warnings
import logging

from metar import __version__, __author__, __email__, __LICENSE__
from metar.Datatypes import (
    temperature,
    pressure,
    speed,
    distance,
    direction,
    precipitation,
)

# logger
_logger = logging.getLogger(__name__)


# Exceptions
class ParserError(Exception):
    """Exception raised when an unparseable group is found in body of the report."""

    pass


# regular expressions to decode various groups of the METAR code
MISSING_RE = re.compile(r"^[M/]+$")

TYPE_RE = re.compile(r"^(?P<type>METAR|SPECI)\s+")
COR_RE = re.compile(r"^(?P<cor>COR)\s+")
STATION_RE = re.compile(r"^(?P<station>[A-Z][A-Z0-9]{3})\s+")
TIME_RE = re.compile(
    r"""^(?P<day>\d\d)
        (?P<hour>\d\d)
        (?P<min>\d\d)Z?\s+""",
    re.VERBOSE,
)
MODIFIER_RE = re.compile(r"^(?P<mod>AUTO|COR AUTO|FINO|NIL|TEST|CORR?|RTD|CC[A-G])\s+")
WIND_RE = re.compile(
    r"""^(?P<dir>[\dO]{3}|[0O]|///|MMM|VRB)
        (?P<speed>P?[\dO]{2,3}|[/M]{2,3})
        (G(?P<gust>P?(\d{1,3}|[/M]{1,3})))?
        (?P<units>KTS?|LT|K|T|KMH|MPS)?
        (\s+(?P<varfrom>\d\d\d)V
        (?P<varto>\d\d\d))?\s+""",
    re.VERBOSE,
)
VISIBILITY_RE = re.compile(
    r"""^(?P<vis>(?P<dist>(M|P)?\d\d\d\d|////)
        (?P<dir>[NSEW][EW]? | NDV)? |
        (?P<distu>(M|P)?(\d+|\d\d?/\d\d?|\d+\s+\d/\d))
        (?P<units>SM|KM|M|U) |
        CAVOK )\s+""",
    re.VERBOSE,
)
RUNWAY_RE = re.compile(
    r"""^(RVRNO |
        R(?P<name>\d\d(RR?|LL?|C)?)/
        (?P<low>(M|P)?(\d\d\d\d|/{4}))
        (V(?P<high>(M|P)?\d\d\d\d))?
        (?P<unit>FT)?[/NDU]*)\s+""",
    re.VERBOSE,
)
WEATHER_RE = re.compile(
    r"""^(?P<int>(-|\+|VC)*)
        (?P<desc>(MI|PR|BC|DR|BL|SH|TS|FZ)+)?
        (?P<prec>(DZ|RA|SN|SG|IC|PL|GR|GS|UP|/)*)
        (?P<obsc>BR|FG|FU|VA|DU|SA|HZ|PY)?
        (?P<other>PO|SQ|FC|SS|DS|NSW|/+)?
        (?P<int2>[-+])?\s+""",
    re.VERBOSE,
)
SKY_RE = re.compile(
    r"""^(?P<cover>VV|CLR|SKC|SCK|NSC|NCD|BKN|SCT|FEW|[O0]VC|///)
        (?P<height>[\dO]{2,4}|///)?
        (?P<cloud>([A-Z][A-Z]+|///))?\s+""",
    re.VERBOSE,
)
TEMP_RE = re.compile(
    r"""^(?P<temp>(M|-)?\d{1,2}|//|XX|MM)/
        (?P<dewpt>(M|-)?\d{1,2}|//|XX|MM)?\s+""",
    re.VERBOSE,
)
PRESS_RE = re.compile(
    r"""^(?P<unit>A|Q|QNH)?
        (?P<press>[\dO]{3,4}|////)
        (?P<unit2>INS)?\s+""",
    re.VERBOSE,
)
RECENT_RE = re.compile(
    r"""^RE(?P<desc>MI|PR|BC|DR|BL|SH|TS|FZ)?
        (?P<prec>(DZ|RA|SN|SG|IC|PL|GR|GS|UP)*)?
        (?P<obsc>BR|FG|FU|VA|DU|SA|HZ|PY)?
        (?P<other>PO|SQ|FC|SS|DS)?\s+""",
    re.VERBOSE,
)
WINDSHEAR_RE = re.compile(r"^(WS\s+)?(ALL\s+RWY|R(WY)?(?P<name>\d\d(RR?|L?|C)?))\s+")
COLOR_RE = re.compile(
    r"""^(BLACK)?(BLU|GRN|WHT|RED)\+?
                        (/?(BLACK)?(BLU|GRN|WHT|RED)\+?)*\s*""",
    re.VERBOSE,
)
RUNWAYSTATE_RE = re.compile(
    r"""((?P<snoclo>R/SNOCLO) |
        ((?P<name>\d\d) | R(?P<namenew>\d\d)(RR?|LL?|C)?/?)
        ((?P<special> SNOCLO|CLRD(\d\d|//)) |
        (?P<deposit>(\d|/))
        (?P<extent>(\d|/))
        (?P<depth>(\d\d|//))
        (?P<friction>(\d\d|//))))\s+""",
    re.VERBOSE,
)
TREND_RE = re.compile(r"^(?P<trend>TEMPO|BECMG|FCST|NOSIG)\s+")

TRENDTIME_RE = re.compile(r"(?P<when>(FM|TL|AT))(?P<hour>\d\d)(?P<min>\d\d)\s+")

REMARK_RE = re.compile(r"^(RMKS?|NOSPECI|NOSIG)\s+")

# regular expressions for remark groups
AUTO_RE = re.compile(r"^AO(?P<type>\d)\s+")
SEALVL_PRESS_RE = re.compile(r"^SLP(?P<press>\d\d\d)\s+")
PEAK_WIND_RE = re.compile(
    r"""^P[A-Z]\s+WND\s+
        (?P<dir>\d\d\d)
        (?P<speed>P?\d\d\d?)/
        (?P<hour>\d\d)?
        (?P<min>\d\d)\s+""",
    re.VERBOSE,
)
WIND_SHIFT_RE = re.compile(
    r"""^WSHFT\s+
        (?P<hour>\d\d)?
        (?P<min>\d\d)
        (\s+(?P<front>FROPA))?\s+""",
    re.VERBOSE,
)
PRECIP_1HR_RE = re.compile(r"^P(?P<precip>\d\d\d\d)\s+")
PRECIP_24HR_RE = re.compile(
    r"""^(?P<type>6|7)
        (?P<precip>\d\d\d\d)\s+""",
    re.VERBOSE,
)
PRESS_3HR_RE = re.compile(
    r"""^5(?P<tend>[0-8])
(?P<press>\d\d\d)\s+""",
    re.VERBOSE,
)
TEMP_1HR_RE = re.compile(
    r"""^T(?P<tsign>0|1)
        (?P<temp>\d\d\d)
        ((?P<dsign>0|1)
        (?P<dewpt>\d\d\d))?\s+""",
    re.VERBOSE,
)
TEMP_6HR_RE = re.compile(
    r"""^(?P<type>1|2)
        (?P<sign>0|1)
        (?P<temp>\d\d\d)\s+""",
    re.VERBOSE,
)
TEMP_24HR_RE = re.compile(
    r"""^4(?P<smaxt>0|1)
        (?P<maxt>\d\d\d)
        (?P<smint>0|1)
        (?P<mint>\d\d\d)\s+""",
    re.VERBOSE,
)
UNPARSED_RE = re.compile(r"(?P<group>\S+)\s+")

LIGHTNING_RE = re.compile(
    r"""^((?P<freq>OCNL|FRQ|CONS)\s+)?
        LTG(?P<type>(IC|CC|CG|CA)*)
        ( \s+(?P<loc>( OHD | VC | DSNT\s+ | \s+AND\s+ |
        [NSEW][EW]? (-[NSEW][EW]?)* )+) )?\s+""",
    re.VERBOSE,
)

TS_LOC_RE = re.compile(
    r"""TS(\s+(?P<loc>( OHD | VC | DSNT\s+ | \s+AND\s+ |
        [NSEW][EW]? (-[NSEW][EW]?)* )+))?
        ( \s+MOV\s+(?P<dir>[NSEW][EW]?) )?\s+""",
    re.VERBOSE,
)
SNOWDEPTH_RE = re.compile(r"""^4/(?P<snowdepth>\d\d\d)\s+""")
ICE_ACCRETION_RE = re.compile(
    r"^I(?P<ice_accretion_hours>[136])(?P<ice_accretion_depth>\d\d\d)\s+"
)


# translation of weather location codes
loc_terms = [("OHD", "overhead"), ("DSNT", "distant"), ("AND", "and"), ("VC", "nearby")]


def xlate_loc(loc):
    """Substitute English terms for the location codes in the given string."""
    for code, english in loc_terms:
        loc = loc.replace(code, english)
    return loc


# translation of the sky-condition codes into english
SKY_COVER = {
    "SKC": "clear",
    "CLR": "clear",
    "NSC": "clear",
    "NCD": "clear",
    "FEW": "a few ",
    "SCT": "scattered ",
    "BKN": "broken ",
    "OVC": "overcast",
    "///": "",
    "VV": "indefinite ceiling",
}


CLOUD_TYPE = {
    "AC": "altocumulus",
    "ACC": "altocumulus castellanus",
    "ACSL": "standing lenticular altocumulus",
    "AS": "altostratus",
    "CB": "cumulonimbus",
    "CBMAM": "cumulonimbus mammatus",
    "CCSL": "standing lenticular cirrocumulus",
    "CC": "cirrocumulus",
    "CI": "cirrus",
    "CS": "cirrostratus",
    "CU": "cumulus",
    "NS": "nimbostratus",
    "SC": "stratocumulus",
    "ST": "stratus",
    "SCSL": "standing lenticular stratocumulus",
    "TCU": "towering cumulus",
}

# translation of the present-weather codes into english
WEATHER_INT = {
    "-": "light",
    "+": "heavy",
    "-VC": "nearby light",
    "+VC": "nearby heavy",
    "VC": "nearby",
}
WEATHER_DESC = {
    "MI": "shallow",
    "PR": "partial",
    "BC": "patches of",
    "DR": "low drifting",
    "BL": "blowing",
    "SH": "showers",
    "TS": "thunderstorm",
    "FZ": "freezing",
}
WEATHER_PREC = {
    "DZ": "drizzle",
    "RA": "rain",
    "SN": "snow",
    "SG": "snow grains",
    "IC": "ice crystals",
    "PL": "ice pellets",
    "GR": "hail",
    "GS": "snow pellets",
    "UP": "unknown precipitation",
    "//": "",
}
WEATHER_OBSC = {
    "BR": "mist",
    "FG": "fog",
    "FU": "smoke",
    "VA": "volcanic ash",
    "DU": "dust",
    "SA": "sand",
    "HZ": "haze",
    "PY": "spray",
}
WEATHER_OTHER = {
    "PO": "sand whirls",
    "SQ": "squalls",
    "FC": "funnel cloud",
    "SS": "sandstorm",
    "DS": "dust storm",
}

WEATHER_SPECIAL = {"+FC": "tornado"}

COLOR = {"BLU": "blue", "GRN": "green", "WHT": "white"}

# translation of various remark codes into English
PRESSURE_TENDENCY = {
    "0": "increasing, then decreasing",
    "1": "increasing more slowly",
    "2": "increasing",
    "3": "increasing more quickly",
    "4": "steady",
    "5": "decreasing, then increasing",
    "6": "decreasing more slowly",
    "7": "decreasing",
    "8": "decreasing more quickly",
}

LIGHTNING_FREQUENCY = {"OCNL": "occasional", "FRQ": "frequent", "CONS": "constant"}
LIGHTNING_TYPE = {
    "IC": "intracloud",
    "CC": "cloud-to-cloud",
    "CG": "cloud-to-ground",
    "CA": "cloud-to-air",
}

REPORT_TYPE = {
    "METAR": "routine report",
    "SPECI": "special report",
    "AUTO": "automatic report",
    "COR": "manually corrected report",
}


# Helper functions
def _sanitize(code):
    """Some string prep to improve parsing fidelity."""
    # Remove extraneous whitespace, any trailing =, then add trailing
    # whitespace as regex matches need that.
    return "%s " % (code.strip().rstrip("="),)


def _report_match(handler, match):
    """Report success or failure of the given handler function. (DEBUG)"""
    if match:
        _logger.debug("%s matched '%s'", handler.__name__, match)
    else:
        _logger.debug("%s didn't match...", handler.__name__)


def _unparsedGroup(self, d):
    """
    Handle otherwise unparseable main-body groups.
    """
    self._unparsed_groups.append(d["group"])


# METAR report objects
debug = False


class Metar(object):
    """METAR (aviation meteorology report)"""

    def __init__(self, metarcode, month=None, year=None, utcdelta=None, strict=True):
        """
        Parse raw METAR code.

        Parameters
        ----------
        metarcode : str
        month, year : int, optional
          Date values to be used when parsing a non-current METAR code. If not
          provided, then the month and year are guessed from the current date.
        utcdelta : int or datetime.timedelta, optional
          An int of hours or a timedelta object used to specify the timezone.
        strict : bool (default is True)
          This option determines if a ``ParserError`` is raised when
          unparsable groups are found or an unexpected exception is encountered.
          Setting this to `False` will prevent exceptions from being raised and
          only generate warning messages.
        """

        self.code = metarcode  # original METAR code
        self.type = "METAR"  # METAR (routine) or SPECI (special)
        self.correction = None  # COR (corrected - WMO spec)
        self.mod = "AUTO"  # AUTO (automatic) or COR (corrected - US spec)
        self.station_id = None  # 4-character ICAO station code
        self.time = None  # observation time [datetime]
        self.cycle = None  # observation cycle (0-23) [int]
        self.wind_dir = None  # wind direction [direction]
        self.wind_speed = None  # wind speed [speed]
        self.wind_gust = None  # wind gust speed [speed]
        self.wind_dir_from = None  # beginning of range for win dir [direction]
        self.wind_dir_to = None  # end of range for wind dir [direction]
        self.vis = None  # visibility [distance]
        self.vis_dir = None  # visibility direction [direction]
        self.max_vis = None  # visibility [distance]
        self.max_vis_dir = None  # visibility direction [direction]
        self.temp = None  # temperature (C) [temperature]
        self.dewpt = None  # dew point (C) [temperature]
        self.press = None  # barometric pressure [pressure]
        self.runway = []  # runway visibility (list of tuples)
        self.weather = []  # present weather (list of tuples)
        self.recent = []  # recent weather (list of tuples)
        self.sky = []  # sky conditions (list of tuples)
        self.windshear = []  # runways w/ wind shear (list of strings)
        self.wind_speed_peak = None  # peak wind speed in last hour
        self.wind_dir_peak = None  # direction of peak wind speed in last hour
        self.peak_wind_time = None  # time of peak wind observation [datetime]
        self.wind_shift_time = None  # time of wind shift [datetime]
        self.max_temp_6hr = None  # max temp in last 6 hours
        self.min_temp_6hr = None  # min temp in last 6 hours
        self.max_temp_24hr = None  # max temp in last 24 hours
        self.min_temp_24hr = None  # min temp in last 24 hours
        self.press_sea_level = None  # sea-level pressure
        self.precip_1hr = None  # precipitation over the last hour
        self.precip_3hr = None  # precipitation over the last 3 hours
        self.precip_6hr = None  # precipitation over the last 6 hours
        self.precip_24hr = None  # precipitation over the last 24 hours
        self.snowdepth = None  # snow depth (distance)
        self.ice_accretion_1hr = None  # ice accretion over the past hour
        self.ice_accretion_3hr = None  # ice accretion over the past 3 hours
        self.ice_accretion_6hr = None  # ice accretion over the past 6 hours
        self._trend = False  # trend groups present (bool)
        self._trend_groups = []  # trend forecast groups
        self._remarks = []  # remarks (list of strings)
        self._unparsed_groups = []
        self._unparsed_remarks = []

        self._now = datetime.datetime.utcnow()
        if utcdelta:
            self._utcdelta = utcdelta
        else:
            self._utcdelta = datetime.datetime.now() - self._now

        self._month = month
        self._year = year

        # Do some string prep before parsing
        code = _sanitize(self.code)
        try:
            ngroup = len(self.handlers)
            igroup = 0
            ifailed = -1
            while igroup < ngroup and code:
                pattern, handler, repeatable = self.handlers[igroup]
                if debug:
                    _logger.debug("%s: %s", handler.__name__, code)
                m = pattern.match(code)
                while m:
                    ifailed = -1
                    if debug:
                        _report_match(handler, m.group())
                    handler(self, m.groupdict())
                    code = code[m.end():]
                    if self._trend:
                        code = self._do_trend_handlers(code)
                    if not repeatable:
                        break

                    if debug:
                        _logger.debug("%s: %s", handler.__name__, code)
                    m = pattern.match(code)
                if not m and ifailed < 0:
                    ifailed = igroup
                igroup += 1
                if igroup == ngroup and not m:
                    pattern, handler = (UNPARSED_RE, _unparsedGroup)
                    if debug:
                        _logger.debug("%s: %s", handler.__name__, code)
                    m = pattern.match(code)
                    if debug:
                        _report_match(handler, m.group())
                    handler(self, m.groupdict())
                    code = code[m.end():]
                    igroup = ifailed
                    ifailed = -2  # if it's still -2 when we run out of main-body
                    #  groups, we'll try parsing this group as a remark
            if pattern == REMARK_RE or self.press:
                while code:
                    for pattern, handler in self.remark_handlers:
                        if debug:
                            _logger.debug("%s: %s", handler.__name__, code)
                        m = pattern.match(code)
                        if m:
                            if debug:
                                _report_match(handler, m.group())
                            handler(self, m.groupdict())
                            code = pattern.sub("", code, 1)
                            break

        except Exception as err:
            message = ("%s failed while processing '%s'\n\t%s") % (
                handler.__name__,
                code,
                "\n\t".join(err.args),
            )
            if strict:
                raise ParserError(message)
            else:
                warnings.warn(message, RuntimeWarning)

        if self._unparsed_groups:
            code = " ".join(self._unparsed_groups)
            message = "Unparsed groups in body '%s' while processing '%s'" % (
                code,
                metarcode,
            )
            if strict:
                raise ParserError(message)
            else:
                warnings.warn(message, RuntimeWarning)

    @property
    def decode_completed(self):
        """
        Indicate whether the decoding was complete for non-remark elements.
        """
        return not self._unparsed_groups

    def _do_trend_handlers(self, code):
        for pattern, handler, repeatable in self.trend_handlers:
            if debug:
                print(handler.__name__, ":", code)
            m = pattern.match(code)
            while m:
                if debug:
                    _report_match(handler, m.group())
                self._trend_groups.append(m.group().strip())
                handler(self, m.groupdict())
                code = code[m.end():]
                if not repeatable:
                    break
                m = pattern.match(code)
        return code

    def __str__(self):
        return self.string()

    def _handleType(self, d):
        """
        Parse the report-type group.

        The following attributes are set:
            type   [string]
        """
        self.type = d["type"]

    def _handleCorrection(self, d):
        """
        Parse the correction group.

        The following attributes are set:
            correction   [string]
        """
        self.correction = d["cor"]

    def _handleStation(self, d):
        """
        Parse the station id group.

        The following attributes are set:
            station_id   [string]
        """
        self.station_id = d["station"]

    def _handleModifier(self, d):
        """
        Parse the report-modifier group.

        The following attributes are set:
            mod   [string]
        """
        mod = d["mod"]
        if mod == "CORR":
            mod = "COR"
        if mod == "NIL" or mod == "FINO":
            mod = "NO DATA"
        self.mod = mod

    def _handleTime(self, d):
        """
        Parse the observation-time group.

        The following attributes are set:
            time   [datetime]
            cycle  [int]
            _day   [int]
            _hour  [int]
            _min   [int]
        """
        self._day = int(d["day"])
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
        self._hour = int(d["hour"])
        self._min = int(d["min"])
        self.time = datetime.datetime(
            self._year, self._month, self._day, self._hour, self._min
        )
        if self._min < 45:
            self.cycle = self._hour
        else:
            self.cycle = self._hour + 1

    def _handleWind(self, d):
        """
        Parse the wind and variable-wind groups.

        The following attributes are set:
            wind_dir           [direction]
            wind_speed         [speed]
            wind_gust          [speed]
            wind_dir_from      [int]
            wind_dir_to        [int]
        """
        wind_dir = d["dir"].replace("O", "0")
        if wind_dir != "VRB" and wind_dir != "///" and wind_dir != "MMM":
            self.wind_dir = direction(wind_dir)
        wind_speed = d["speed"].replace("O", "0")
        units = d["units"]
        # Ambiguous METAR when no wind speed units are provided
        if units is None and self.station_id is not None:
            # Assume US METAR sites are reporting in KT
            if len(self.station_id) == 3 or self.station_id.startswith("K"):
                units = "KT"
        # If units are still None, default to MPS
        if units is None:
            units = "MPS"
        if units == "KTS" or units == "K" or units == "T" or units == "LT":
            units = "KT"
        if wind_speed.startswith("P"):
            self.wind_speed = speed(wind_speed[1:], units, ">")
        elif not MISSING_RE.match(wind_speed):
            self.wind_speed = speed(wind_speed, units)
        if d["gust"]:
            wind_gust = d["gust"]
            if wind_gust.startswith("P"):
                self.wind_gust = speed(wind_gust[1:], units, ">")
            elif not MISSING_RE.match(wind_gust):
                self.wind_gust = speed(wind_gust, units)
        if d["varfrom"]:
            self.wind_dir_from = direction(d["varfrom"])
            self.wind_dir_to = direction(d["varto"])

    def _handleVisibility(self, d):
        """
        Parse the minimum and maximum visibility groups.

        The following attributes are set:
            vis          [distance]
            vis_dir      [direction]
            max_vis      [distance]
            max_vis_dir  [direction]
        """
        vis = d["vis"]
        vis_less = None
        vis_dir = None
        vis_units = "M"
        vis_dist = "10000"
        if d["dist"] and d["dist"] != "////":
            vis_dist = d["dist"]
            if d["dir"] and d["dir"] != "NDV":
                vis_dir = d["dir"]
        elif d["distu"]:
            vis_dist = d["distu"]
            if d["units"] and d["units"] != "U":
                vis_units = d["units"]
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

    def _handleRunway(self, d):
        """
        Parse a runway visual range group.

        The following attributes are set:
            range   [list of tuples]
            . name  [string]
            . low   [distance]
            . high  [distance]
            . unit  [string]
        """
        if d["name"] is None:
            return
        unit = d["unit"] if d["unit"] is not None else "M"
        if d["low"] == "////":
            return
        else:
            low = distance(d["low"], unit)
        if d["high"] is None:
            high = low
        else:
            high = distance(d["high"], unit)
        self.runway.append([d["name"], low, high, unit])

    def _handleWeather(self, d):
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
        inteni = d["int"]
        if not inteni and d["int2"]:
            inteni = d["int2"]
        desci = d["desc"]
        preci = d["prec"]
        obsci = d["obsc"]
        otheri = d["other"]
        self.weather.append((inteni, desci, preci, obsci, otheri))

    def _handleSky(self, d):
        """
        Parse a sky-conditions group.

        The following attributes are set:
            sky        [list of tuples]
            .  cover   [string]
            .  height  [distance]
            .  cloud   [string]
        """
        height = d["height"]
        if not height or height == "///":
            height = None
        else:
            height = height.replace("O", "0")
            height = distance(int(height) * 100, "FT")
        cover = d["cover"]
        if cover == "SCK" or cover == "SKC" or cover == "CL":
            cover = "CLR"
        if cover == "0VC":
            cover = "OVC"
        cloud = d["cloud"]
        if cloud == "///":
            cloud = ""
        self.sky.append((cover, height, cloud))

    def _handleTemp(self, d):
        """
        Parse a temperature-dewpoint group.

        The following attributes are set:
            temp    temperature (Celsius) [float]
            dewpt   dew point (Celsius) [float]
        """
        temp = d["temp"]
        dewpt = d["dewpt"]
        if temp and temp != "//" and temp != "XX" and temp != "MM":
            self.temp = temperature(temp)
        if dewpt and dewpt != "//" and dewpt != "XX" and dewpt != "MM":
            self.dewpt = temperature(dewpt)

    def _handlePressure(self, d):
        """
        Parse an altimeter-pressure group.

        The following attributes are set:
            press    [int]
        """
        press = d["press"]
        if press != "////":
            press = float(press.replace("O", "0"))
            if d["unit"]:
                if d["unit"] == "A" or (d["unit2"] and d["unit2"] == "INS"):
                    self.press = pressure(press / 100, "IN")
                elif d["unit"] == "SLP":
                    if press < 500:
                        press = press / 10 + 1000
                    else:
                        press = press / 10 + 900
                    self.press = pressure(press, "MB")
                    self._remarks.append("sea-level pressure %.1fhPa" % press)
                else:
                    self.press = pressure(press, "MB")
            elif press > 2500:
                self.press = pressure(press / 100, "IN")
            else:
                self.press = pressure(press, "MB")

    def _handleRecent(self, d):
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
        desci = d["desc"]
        preci = d["prec"]
        obsci = d["obsc"]
        otheri = d["other"]
        self.recent.append(("", desci, preci, obsci, otheri))

    def _handleWindShear(self, d):
        """
        Parse wind-shear groups.

        The following attributes are set:
            windshear    [list of strings]
        """
        if d["name"]:
            self.windshear.append(d["name"])
        else:
            self.windshear.append("ALL")

    def _handleColor(self, d):
        """
        Parse (and ignore) the color groups.

        The following attributes are set:
            trend    [list of strings]
        """
        pass

    def _handleRunwayState(self, d):
        """
        Parse (and ignore) the runway state.

        The following attributes are set:
        """
        pass

    def _handleTrend(self, d):
        """
        Parse (and ignore) the trend groups.
        """
        if "trend" in d:
            self._trend_groups.append(d["trend"])
        self._trend = True

    def _startRemarks(self, d):
        """
        Found the start of the remarks section.
        """
        self._remarks = []

    def _handleSealvlPressRemark(self, d):
        """
        Parse the sea-level pressure remark group.
        """
        value = float(d["press"]) / 10.0
        if value < 50:
            value += 1000
        else:
            value += 900
        self.press_sea_level = pressure(value, "MB")

    def _handlePrecip24hrRemark(self, d):
        """
        Parse a 3-, 6- or 24-hour cumulative preciptation remark group.
        """
        value = float(d["precip"]) / 100.0
        if d["type"] == "6":
            if self.cycle in [3, 9, 15, 21]:
                self.precip_3hr = precipitation(value, "IN")
            else:
                self.precip_6hr = precipitation(value, "IN")
        else:
            self.precip_24hr = precipitation(value, "IN")

    def _handlePrecip1hrRemark(self, d):
        """Parse an hourly precipitation remark group."""
        value = float(d["precip"]) / 100.0
        self.precip_1hr = precipitation(value, "IN")

    def _handleTemp1hrRemark(self, d):
        """
        Parse a temperature & dewpoint remark group.

        These values replace the temp and dewpt from the body of the report.
        """
        value = float(d["temp"]) / 10.0
        if d["tsign"] == "1":
            value = -value
        self.temp = temperature(value)
        if d["dewpt"]:
            value2 = float(d["dewpt"]) / 10.0
            if d["dsign"] == "1":
                value2 = -value2
            self.dewpt = temperature(value2)

    def _handleTemp6hrRemark(self, d):
        """
        Parse a 6-hour maximum or minimum temperature remark group.
        """
        value = float(d["temp"]) / 10.0
        if d["sign"] == "1":
            value = -value
        if d["type"] == "1":
            self.max_temp_6hr = temperature(value, "C")
        else:
            self.min_temp_6hr = temperature(value, "C")

    def _handleTemp24hrRemark(self, d):
        """
        Parse a 24-hour maximum/minimum temperature remark group.
        """
        value = float(d["maxt"]) / 10.0
        if d["smaxt"] == "1":
            value = -value
        value2 = float(d["mint"]) / 10.0
        if d["smint"] == "1":
            value2 = -value2
        self.max_temp_24hr = temperature(value, "C")
        self.min_temp_24hr = temperature(value2, "C")

    def _handlePress3hrRemark(self, d):
        """
        Parse a pressure-tendency remark group.
        """
        value = float(d["press"]) / 10.0
        descrip = PRESSURE_TENDENCY[d["tend"]]
        self._remarks.append("3-hr pressure change %.1fhPa, %s" % (value, descrip))

    def _handlePeakWindRemark(self, d):
        """
        Parse a peak wind remark group.
        """
        peak_dir = int(d["dir"])
        peak_speed = int(d["speed"])
        self.wind_speed_peak = speed(peak_speed, "KT")
        self.wind_dir_peak = direction(peak_dir)
        peak_min = int(d["min"])
        if d["hour"]:
            peak_hour = int(d["hour"])
        else:
            peak_hour = self._hour
        self.peak_wind_time = datetime.datetime(
            self._year, self._month, self._day, peak_hour, peak_min
        )
        if self.peak_wind_time > self.time:
            if peak_hour > self._hour:
                self.peak_wind_time -= datetime.timedelta(hours=24)
            else:
                self.peak_wind_time -= datetime.timedelta(hours=1)
        self._remarks.append(
            "peak wind %dkt from %d degrees at %d:%02d"
            % (peak_speed, peak_dir, peak_hour, peak_min)
        )

    def _handleWindShiftRemark(self, d):
        """
        Parse a wind shift remark group.
        """
        if d["hour"]:
            wshft_hour = int(d["hour"])
        else:
            wshft_hour = self._hour
        wshft_min = int(d["min"])
        self.wind_shift_time = datetime.datetime(
            self._year, self._month, self._day, wshft_hour, wshft_min
        )
        if self.wind_shift_time > self.time:
            if wshft_hour > self._hour:
                self.wind_shift_time -= datetime.timedelta(hours=24)
            else:
                self.wind_shift_time -= datetime.timedelta(hours=1)
        text = "wind shift at %d:%02d" % (wshft_hour, wshft_min)
        if d["front"]:
            text += " (front)"
        self._remarks.append(text)

    def _handleLightningRemark(self, d):
        """
        Parse a lightning observation remark group.
        """
        parts = []
        if d["freq"]:
            parts.append(LIGHTNING_FREQUENCY[d["freq"]])
        parts.append("lightning")
        if d["type"]:
            ltg_types = []
            group = d["type"]
            while group:
                ltg_types.append(LIGHTNING_TYPE[group[:2]])
                group = group[2:]
            parts.append("(" + ",".join(ltg_types) + ")")
        if d["loc"]:
            parts.append(xlate_loc(d["loc"]))
        self._remarks.append(" ".join(parts))

    def _handleTSLocRemark(self, d):
        """
        Parse a thunderstorm location remark group.
        """
        text = "thunderstorm"
        if d["loc"]:
            text += " " + xlate_loc(d["loc"])
        if d["dir"]:
            text += " moving %s" % d["dir"]
        self._remarks.append(text)

    def _handleAutoRemark(self, d):
        """
        Parse an automatic station remark group.
        """
        if d["type"] == "1":
            self._remarks.append("Automated station")
        elif d["type"] == "2":
            self._remarks.append("Automated station (type 2)")

    def _handleSnowDepthRemark(self, d):
        """
        Parse the 4/ group snowdepth report
        """
        self.snowdepth = distance(float(d["snowdepth"]), "IN")
        self._remarks.append(" snowdepth %s" % (self.snowdepth,))

    def _handleIceAccretionRemark(self, d):
        """
        Parse the I/ group ice accretion report.
        """
        myattr = "ice_accretion_%shr" % (d["ice_accretion_hours"],)
        value = precipitation(float(d["ice_accretion_depth"]) / 100.0, "IN")
        setattr(self, myattr, value)

    def _unparsedRemark(self, d):
        """
        Handle otherwise unparseable remark groups.
        """
        self._unparsed_remarks.append(d["group"])

    # the list of handler functions to use (in order) to process a METAR report

    handlers = [
        (TYPE_RE, _handleType, False),
        (COR_RE, _handleCorrection, False),
        (STATION_RE, _handleStation, False),
        (TIME_RE, _handleTime, False),
        (MODIFIER_RE, _handleModifier, False),
        (WIND_RE, _handleWind, False),
        (VISIBILITY_RE, _handleVisibility, True),
        (RUNWAY_RE, _handleRunway, True),
        (WEATHER_RE, _handleWeather, True),
        (SKY_RE, _handleSky, True),
        (WIND_RE, _handleWind, False),
        (VISIBILITY_RE, _handleVisibility, True),
        (TEMP_RE, _handleTemp, False),
        (PRESS_RE, _handlePressure, True),
        (SEALVL_PRESS_RE, _handleSealvlPressRemark, False),
        (RECENT_RE, _handleRecent, True),
        (WINDSHEAR_RE, _handleWindShear, True),
        (COLOR_RE, _handleColor, True),
        (RUNWAYSTATE_RE, _handleRunwayState, True),
        (TREND_RE, _handleTrend, True),
        (REMARK_RE, _startRemarks, False),
    ]

    trend_handlers = [
        (TRENDTIME_RE, _handleTrend, True),
        (WIND_RE, _handleTrend, True),
        (VISIBILITY_RE, _handleTrend, True),
        (WEATHER_RE, _handleTrend, True),
        (SKY_RE, _handleTrend, True),
        (COLOR_RE, _handleTrend, True),
    ]

    # the list of patterns for the various remark groups,
    # paired with the handler functions to use to record the decoded remark.

    remark_handlers = [
        (AUTO_RE, _handleAutoRemark),
        (SEALVL_PRESS_RE, _handleSealvlPressRemark),
        (PEAK_WIND_RE, _handlePeakWindRemark),
        (WIND_SHIFT_RE, _handleWindShiftRemark),
        (LIGHTNING_RE, _handleLightningRemark),
        (TS_LOC_RE, _handleTSLocRemark),
        (TEMP_1HR_RE, _handleTemp1hrRemark),
        (PRECIP_1HR_RE, _handlePrecip1hrRemark),
        (PRECIP_24HR_RE, _handlePrecip24hrRemark),
        (PRESS_3HR_RE, _handlePress3hrRemark),
        (TEMP_6HR_RE, _handleTemp6hrRemark),
        (TEMP_24HR_RE, _handleTemp24hrRemark),
        (SNOWDEPTH_RE, _handleSnowDepthRemark),
        (ICE_ACCRETION_RE, _handleIceAccretionRemark),
        (UNPARSED_RE, _unparsedRemark),
    ]

    # functions that return text representations of conditions for output

    def string(self):
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
        if self.ice_accretion_1hr:
            lines.append("1-hour Ice Accretion: %s" % str(self.ice_accretion_1hr))
        if self.ice_accretion_3hr:
            lines.append("3-hour Ice Accretion: %s" % str(self.ice_accretion_3hr))
        if self.ice_accretion_6hr:
            lines.append("6-hour Ice Accretion: %s" % str(self.ice_accretion_6hr))
        if self._remarks:
            lines.append("remarks:")
            lines.append("- " + self.remarks("\n- "))
        if self._unparsed_remarks:
            lines.append("- " + " ".join(self._unparsed_remarks))
        lines.append("METAR: " + self.code)
        return "\n".join(lines)

    def report_type(self):
        """
        Return a textual description of the report type.
        """
        if self.type is None:
            text = "unknown report type"
        elif self.type in REPORT_TYPE:
            text = REPORT_TYPE[self.type]
        else:
            text = self.type + " report"
        if self.cycle:
            text += ", cycle %d" % self.cycle
        if self.mod:
            if self.mod in REPORT_TYPE:
                text += " (%s)" % REPORT_TYPE[self.mod]
            else:
                text += " (%s)" % self.mod
        if self.correction:
            text += " (%s)" % REPORT_TYPE[self.correction]
        return text

    def wind(self, units="KT"):
        """
        Return a textual description of the wind conditions.

        Units may be specified as "MPS", "KT", "KMH", or "MPH".
        """
        if self.wind_speed is None:
            return "missing"
        elif self.wind_speed.value() == 0.0:
            text = "calm"
        else:
            wind_speed = self.wind_speed.string(units)
            if not self.wind_dir:
                text = "variable at %s" % wind_speed
            elif self.wind_dir_from:
                text = "%s to %s at %s" % (
                    self.wind_dir_from.compass(),
                    self.wind_dir_to.compass(),
                    wind_speed,
                )
            else:
                text = "%s at %s" % (self.wind_dir.compass(), wind_speed)
            if self.wind_gust:
                text += ", gusting to %s" % self.wind_gust.string(units)
        return text

    def peak_wind(self, units="KT"):
        """
        Return a textual description of the peak wind conditions.

        Units may be specified as "MPS", "KT", "KMH", or "MPH".
        """
        if self.wind_speed_peak is None:
            return "missing"
        elif self.wind_speed_peak.value() == 0.0:
            text = "calm"
        else:
            wind_speed = self.wind_speed_peak.string(units)
            if not self.wind_dir_peak:
                text = wind_speed
            else:
                text = "%s at %s" % (self.wind_dir_peak.compass(), wind_speed)
                if self.peak_wind_time is not None:
                    text += " at %s" % self.peak_wind_time.strftime("%H:%M")
        return text

    def wind_shift(self, units="KT"):
        """
        Return a textual description of the wind shift time

        Units may be specified as "MPS", "KT", "KMH", or "MPH".
        """
        if self.wind_shift_time is None:
            return "missing"
        else:
            return self.wind_shift_time.strftime("%H:%M")

    def visibility(self, units=None):
        """
        Return a textual description of the visibility.

        Units may be statute miles ("SM") or meters ("M").
        """
        if self.vis is None:
            return "missing"
        if self.vis_dir:
            text = "%s to %s" % (self.vis.string(units), self.vis_dir.compass())
        else:
            text = self.vis.string(units)
        if self.max_vis:
            if self.max_vis_dir:
                text += "; %s to %s" % (
                    self.max_vis.string(units),
                    self.max_vis_dir.compass(),
                )
            else:
                text += "; %s" % self.max_vis.string(units)
        return text

    def runway_visual_range(self, units=None):
        """
        Return a textual description of the runway visual range.
        """
        lines = []
        for name, low, high, unit in self.runway:
            reportunits = unit if units is None else units
            if low != high:
                lines.append(
                    ("on runway %s, from %d to %s")
                    % (name, low.value(reportunits), high.string(reportunits))
                )
            else:
                lines.append("on runway %s, %s" % (name, low.string(reportunits)))
        return "; ".join(lines)

    def present_weather(self):
        """
        Return a textual description of the present weather.
        """
        return self._weather(self.weather)

    def recent_weather(self):
        """
        Return a textual description of the recent weather.
        """
        return self._weather(self.recent)

    def _weather(self, weather):
        """
        Return a textual description of weather.
        """
        text_list = []
        for weatheri in weather:
            (inteni, desci, preci, obsci, otheri) = weatheri
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
                    precip_text = WEATHER_PREC[preci[:2]] + " and "
                    precip_text += WEATHER_PREC[preci[2:]]
                elif len(preci) == 6:
                    precip_text = WEATHER_PREC[preci[:2]] + ", "
                    precip_text += WEATHER_PREC[preci[2:4]] + " and "
                    precip_text += WEATHER_PREC[preci[4:]]
                else:
                    precip_text = preci
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
            code = " ".join(code_parts)
            if code in WEATHER_SPECIAL:
                text_list.append(WEATHER_SPECIAL[code])
            else:
                text_list.append(" ".join(text_parts))
        return "; ".join(text_list)

    def sky_conditions(self, sep="; "):
        """
        Return a textual description of the sky conditions.
        """
        text_list = []
        for skyi in self.sky:
            (cover, height, cloud) = skyi
            if cover in ["SKC", "CLR", "NSC"]:
                text_list.append(SKY_COVER[cover])
            else:
                if cloud:
                    what = CLOUD_TYPE.get(cloud, "unknown CLOUD_TYPE of %s" % (cloud,))
                elif SKY_COVER[cover].endswith(" "):
                    what = "clouds"
                else:
                    what = ""
                label = "%s %s" % (SKY_COVER[cover], what)
                # HACK here to account for 'empty' entries with above format
                label = " ".join(label.strip().split())
                if cover == "VV":
                    label += ", vertical visibility to %s" % (str(height),)
                else:
                    label += " at %s" % (str(height),)
                text_list.append(label)
        return sep.join(text_list)

    def trend(self):
        """
        Return the trend forecast groups
        """
        return " ".join(self._trend_groups)

    def remarks(self, sep="; "):
        """
        Return the decoded remarks.
        """
        return sep.join(self._remarks)
