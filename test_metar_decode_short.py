#!/usr/bin/env python
#
#  This is a minimal sample script showing how the individual data
#  are accessed from the decoded report.  To produce the standard text 
#  summary of a report, the string() method of the Metar object.
#
#  The parsed data are stored as attributes of a Metar object.
#  Individual attributes are either strings. instances of one of the
#  metar.Datatypes classes, or lists of tuples of these scalars.
#  Here's a summary, adapted from the comments in the Metar.Metar.__init__()
#  method:
# 
#    Attribute       Comments [data type]
#    --------------  --------------------
#    code             original METAR code [string]
#    type             METAR (routine) or SPECI (special) [string]
#    mod              AUTO (automatic) or COR (corrected) [string]
#    station_id       4-character ICAO station code [string]
#    time             observation time [datetime]
#    cycle            observation cycle (0-23) [int]
#    wind_dir         wind direction [direction]
#    wind_speed       wind speed [speed]
#    wind_gust        wind gust speed [speed]
#    wind_dir_from    beginning of range for win dir [direction]
#    wind_dir_to      end of range for wind dir [direction]
#    vis              visibility [distance]
#    vis_dir          visibility direction [direction]
#    max_vis          visibility [distance]
#    max_vis_dir      visibility direction [direction]
#    temp             temperature (C) [temperature]
#    dewpt            dew point (C) [temperature]
#    press            barometric pressure [pressure]
#    runway           runway visibility [list of tuples...]
#                        name [string]
#                        low  [distance]
#                        high [distance]
#    weather          present weather [list of tuples...]
#                        intensity     [string]
#                        description   [string]
#                        precipitation [string]
#                        obscuration   [string]
#                        other         [string]
#    recent           recent weather [list of tuples...]
#    sky              sky conditions [list of tuples...]
#                        cover   [string]
#                        height  [distance]
#                        cloud   [string]
#    windshear        runways w/ wind shear [list of strings]
#
#    press_sea_level  sea-level pressure [pressure]
#    wind_speed_peak  peak wind speed in last hour [speed]
#    wind_dir_peak    direction of peak wind speed in last hour [direction]
#    max_temp_6hr     max temp in last 6 hours [temperature]
#    min_temp_6hr     min temp in last 6 hours [temperature]
#    max_temp_24hr    max temp in last 24 hours [temperature]
#    min_temp_24hr    min temp in last 24 hours [temperature]
#    precip_1hr       precipitation over the last hour [precipitation]
#    precip_3hr       precipitation over the last 3 hours [precipitation]
#    precip_6hr       precipitation over the last 6 hours [precipitation]
#    precip_24hr      precipitation over the last 24 hours [precipitation]
#
#    _remarks         remarks [list of strings]
#    _unparsed        unparsed remarks [list of strings]
#
#  The metar.Datatypes classes (temperature, pressure, precipitation,
#  speed, direction) describe an observation and its units.  They provide
#  value() and string() methods to that return numerical and string
#  representations of the data in any of a number of supported units.  
# 
#  (You're going to have to study the source code for more details,
#  like the available methods and supported unit conversions for the
#  metar.Datatypes objects, etc..)  

#  In particular, look at the Metar.string()
#  method, and the functions it calls.  
#
#  Feb 4, 2005 
#  Tom Pollard 
#
from metar.Metar import Metar

# A sample METAR report

#code = "METAR KEWR 111851Z VRB03G19KT 2SM R04R/3000VP6000FT TSRA BR FEW015 BKN040CB BKN065 OVC200 22/22 A2987 RMK AO2 PK WND 29028/1817 WSHFT 1812 TSB05RAB22 SLP114 FRQ LTGICCCCG TS OHD AND NW-N-E MOV NE P0013 T02270215"
#code = 'METAR TFFF 151430Z AUTO 08016KT 050V110 9999 SCT032 BKN038 BKN044'
#code = 'METAR SVVA 092200Z 36004KT 9999 -DZ BKN016'
#code = 'METAR CYPY 120000Z AUTO 27008KT 9SM BKN090 OVC110 13/M00 A3001 RMK    SLP171'
#code='METAR SVVA 092200Z 36004KT 9999 -DZ BKN016 30/21 Q1011'
#code = 'METAR LCPH 120000Z 01008KT FEW020 22/18'
#code = 'METAR LBBG 120000Z 05004MPS 9999 FEW033 19/17 Q1015 NOSIG'
#code = '   METAR LCPH 120000Z 01008KT 9999 FEW020 22/18 Q1013'
#code = 'SPECI YSNF 220000Z 22017G28KT 9999 FEW024 SCT300 18/11 Q1021'
#code = 'METAR OYRN 220100Z 36004KT CAVOK 29/26 Q1005'
#code = 'METAR SPIM 120000Z 29006KT 9999 OVC010 16/13 Q1013 NOSIG RMK PP000 SLP171'
#code='METAR TNCM 220100Z 06010KT 9999 VCSH SCT017TCU 29/24 Q1016 A3001 NOSI G'
#code ='METAR ETSI 220020Z AUTO 30006KT 6000 // ////// 12/11 Q1017 ///'
#code='METAR EBLB 220125Z AUTO 34011KT 3600 SCT002/// BKN004/// BKN006/// 09/09 Q1021 AMB'
#code='METAR CYYF 220200Z VRB02KT 15SM SKC 20/11 A2983 RMK SLP102 DENSITY ALT 2000FT'
#code='METAR VTCT 220000Z 19003KT 9999 BKN015 OVC100 25/23 Q1010 A2983 RMK/RWY03 INFO A'
#code= 'METAR CZBF 220100Z 20005KT 170V230 15SM FEW100 OVC250 19/15 A2973 RMK AC2CS6 SLP068 DENSITY ALT 800FT'
#code = 'METAR SVMG 220100Z /////KT 9999 TS FEW010 CB/NE 28/25 Q1012 TEMPO'
#code = 'METAR FKKD 220000Z 00000KT 9999 TS BKN013 FEW016CB 25/24 Q1014 TEMPO 4000 -TSRA'
#code='METAR OMDW 220000Z 09006KT 2500 BR NSC 26/25 Q1004 BECMG 0800 BCFG'
#code='METAR LCEN 302350Z 28008KT CAVOK 17/09 Q1016 NOSIG'
#code='SPECI CZCP 302353Z AUTO 11016KT 2 3/4SM OVC005 OVC015 OVC020 M03/ A2989 RMK ICG PAST HR'
#code='METAR VANP 302340Z 00000KT 3500 HZ NSC 21/18 Q1014 TEMPO 3000 HZ/BR'
#code='METAR SEGU 010000Z 22009KT 9999 SCT023 BKN100 26/20 Q1009 RMK A2983 NOSIG'
code='METAR SEQM 010000Z 12007KT CAVOK 16/03 Q1024 NOSIG RMK A3024'

print "-----------------------------------------------------------------------"
print "METAR: ",code
print "-----------------------------------------------------------------------"

# Initialize a Metar object with the coded report
obs = Metar(code)

print obs.string()
#print obs.string().split('\n')

metar_header = {}
metar_header['ICAO_code'] = obs.station_id
metar_header['origin_time'] = obs.time.isoformat(' ')
metar_header['origin_date'] = obs.time.day
metar_header['origin_hours'] = obs.time.isoformat()[11:13]
metar_header['origin_minutes'] = obs.time.isoformat()[14:16]
print metar_header

