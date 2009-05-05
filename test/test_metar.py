import unittest
from metar import Metar

# METAR fragments used in tests, below
sta_time = "KEWR 101651Z "
sta_time_mod = "KEWR 101651Z AUTO "
sta_time_wind = "KEWR 101651Z 00000KT "

from datetime import datetime, timedelta
today = datetime.utcnow()
tomorrow = today + timedelta(days=1)

class MetarTest(unittest.TestCase):

  def raisesParserError(self, code):
    self.assertRaises(Metar.ParserError, Metar.Metar, code )

  def raisesParserError(self, code):
    self.assertRaises(Metar.ParserError, Metar.Metar, code )

  def test_010_parseType_default(self):
    """Check default value of the report type."""
    self.assertEqual( Metar.Metar("KEWR").type, "METAR" )

  def test_011_parseType_legal(self):
    """Check parsing of the report type."""
    self.assertEqual( Metar.Metar("METAR").type, "METAR" )
    self.assertEqual( Metar.Metar("SPECI").type, "SPECI" )
    self.raisesParserError("TAF" )

  def test_020_parseStation_legal(self):
    """Check parsing of the station code."""
    self.assertEqual( Metar.Metar("KEWR").station_id, "KEWR" )
    self.assertEqual( Metar.Metar("METAR KEWR").station_id, "KEWR" )
    self.assertEqual( Metar.Metar("BIX1").station_id, "BIX1" )
    self.assertEqual( Metar.Metar("K256").station_id, "K256" )

  def test_021_parseStation_illegal(self):
    """Check rejection of illegal station codes."""
    self.raisesParserError( "1ABC" )
    self.raisesParserError( "METAR METAR" )
    self.raisesParserError( "METAR DC" )
    self.raisesParserError( "METAR A" )
    self.raisesParserError( "kewr" )

  def test_030_parseTime_legal(self):
    """Check parsing of the time stamp."""
    report =  Metar.Metar("KEWR 101651Z")
    self.assertEqual( report.time.day, 10 )
    self.assertEqual( report.time.hour, 16 )
    self.assertEqual( report.time.minute, 51 )
    if today.day > 10 or (today.hour > 16 and today.day == 10):
        self.assertEqual( report.time.month, today.month )
    if today.month > 1 or today.day > 10:
        self.assertEqual( report.time.year, today.year )

  def test_031_parseTime_specify_year(self):
    """Check that the year can be specified."""
    other_year = 2003

    report =  Metar.Metar("KEWR 101651Z", year=other_year)
    self.assertEqual( report.time.year, other_year )

  def test_032_parseTime_specify_month(self):
    """Check that the month can be specified."""
    last_month = ((today.month - 2) % 12) + 1
    last_year = today.year - 1

    report =  Metar.Metar("KEWR 101651Z", month=last_month)
    self.assertEqual( report.time.month, last_month )

  def test_033_parseTime_auto_month(self):
    """Check that we assign report to previous month if it can't be in this month."""
    next_day = tomorrow.day
    if next_day > today.day:
        last_month = ((today.month - 2) % 12) + 1
        last_year = today.year - 1

        timestr = "%02d1651Z" % (next_day)
        report =  Metar.Metar("KEWR " + timestr)
        self.assertEqual( report.time.day, next_day )
        self.assertEqual( report.time.month, last_month )
        if today.month > 1:
            self.assertEqual( report.time.year, today.year )
        else:
            self.assertEqual( report.time.year, last_year )

  def test_034_parseTime_auto_year(self):
    """Check that year is adjusted correctly if specified month is in the future."""
    next_month = (today.month % 12) + 1
    last_year = today.year - 1

    report =  Metar.Metar("KEWR 101651Z", month=next_month)
    self.assertEqual( report.time.month, next_month )
    if next_month > 1:
        self.assertEqual( report.time.year, last_year )
    else:
        self.assertEqual( report.time.year, today.year )

  def test_035_parseTime_suppress_auto_month(self):
    """Check that explicit month suppresses automatic month rollback."""
    next_day = tomorrow.day
    if next_day > today.day:
        last_month = ((today.month - 2) % 12) + 1
        last_year = today.year - 1

        timestr = "%02d1651Z" % (next_day)
        report =  Metar.Metar("KEWR " + timestr, month=1)
        self.assertEqual( report.time.day, next_day )
        self.assertEqual( report.time.month, 1 )
        if today.month > 1:
            self.assertEqual( report.time.year, today.year )
        else:
            self.assertEqual( report.time.year, last_year )

  def test_040_parseModifier_default(self):
    """Check default 'modifier' value."""
    self.assertEqual( Metar.Metar("KEWR").mod, "AUTO" )

  def test_041_parseModifier(self):
    """Check parsing of 'modifier' groups."""
    self.assertEqual( Metar.Metar(sta_time+"AUTO").mod, "AUTO" )
    self.assertEqual( Metar.Metar(sta_time+"COR").mod, "COR" )

  def test_042_parseModifier_nonstd(self):
    """Check parsing of nonstandard 'modifier' groups."""

    def report(mod_group):
      """(Macro) Return Metar object from parsing the given modifier group."""
      return Metar.Metar(sta_time+mod_group)

    self.assertEqual( report("RTD").mod, "RTD" )
    self.assertEqual( report("TEST").mod, "TEST" )
    self.assertEqual( report("CCA").mod, "CCA" )
    self.assertEqual( report("CCB").mod, "CCB" )
    self.assertEqual( report("CCC").mod, "CCC" )
    self.assertEqual( report("CCD").mod, "CCD" )
    self.assertEqual( report("CCE").mod, "CCE" )
    self.assertEqual( report("CCF").mod, "CCF" )
    self.assertEqual( report("CCG").mod, "CCG" )
    self.assertEqual( report("CORR").mod, "COR" )
    self.assertEqual( report("FINO").mod, "NO DATA" )
    self.assertEqual( report("NIL").mod, "NO DATA" )

  def test_043_parseModifier_illegal(self):
    """Check rejection of illegal 'modifier' groups."""
#    self.raisesParserError( "KEWR AUTO" )
    self.raisesParserError( sta_time+"auto" )
    self.raisesParserError( sta_time+"CCH" )
    self.raisesParserError( sta_time+"MAN" )

  def test_140_parseWind(self):
    """Check parsing of wind groups."""
    report = Metar.Metar(sta_time+"09010KT" )
    self.assertEqual( report.wind_dir.value(), 90 )
    self.assertEqual( report.wind_speed.value(), 10 )
    self.assertEqual( report.wind_gust, None )
    self.assertEqual( report.wind_dir_from, None )
    self.assertEqual( report.wind_dir_from, None )
    self.assertEqual( report.wind(), "E at 10 knots" )

    report = Metar.Metar(sta_time+"09010MPS" )
    self.assertEqual( report.wind_speed.value(), 10 )
    self.assertEqual( report.wind_speed.value("KMH"), 36 )
    self.assertEqual( report.wind(), "E at 19 knots" )
    self.assertEqual( report.wind("MPS"), "E at 10 mps" )
    self.assertEqual( report.wind("KMH"), "E at 36 km/h" )

    report = Metar.Metar(sta_time+"09010KMH" )
    self.assertEqual( report.wind_speed.value(), 10 )
    self.assertEqual( report.wind(), "E at 5 knots" )
    self.assertEqual( report.wind('KMH'), "E at 10 km/h" )

    report = Metar.Metar(sta_time+"090010KT" )
    self.assertEqual( report.wind_dir.value(), 90 )
    self.assertEqual( report.wind_speed.value(), 10 )

    report = Metar.Metar(sta_time+"000000KT" )
    self.assertEqual( report.wind_dir.value(), 0 )
    self.assertEqual( report.wind_speed.value(), 0 )
    self.assertEqual( report.wind(), "calm" )

    report = Metar.Metar(sta_time+"VRB03KT" )
    self.assertEqual( report.wind_dir, None )
    self.assertEqual( report.wind_speed.value(), 3 )
    self.assertEqual( report.wind(), "variable at 3 knots" )

    report = Metar.Metar(sta_time+"VRB00KT" )
    self.assertEqual( report.wind(), "calm" )

    report = Metar.Metar(sta_time+"VRB03G40KT" )
    self.assertEqual( report.wind_dir, None )
    self.assertEqual( report.wind_speed.value(), 3 )
    self.assertEqual( report.wind_gust.value(), 40 )
    self.assertEqual( report.wind_dir_from, None )
    self.assertEqual( report.wind_dir_to, None )
    self.assertEqual( report.wind(), "variable at 3 knots, gusting to 40 knots" )

    report = Metar.Metar(sta_time+"21010G30KT" )
    self.assertEqual( report.wind(), "SSW at 10 knots, gusting to 30 knots" )

    report = Metar.Metar(sta_time+"21010KT 180V240" )
    self.assertEqual( report.wind_dir.value(), 210 )
    self.assertEqual( report.wind_speed.value(), 10 )
    self.assertEqual( report.wind_gust, None )
    self.assertEqual( report.wind_dir_from.value(), 180 )
    self.assertEqual( report.wind_dir_to.value(), 240 )
    self.assertEqual( report.wind(), "S to WSW at 10 knots" )

  def test_141_parseWind_nonstd(self):
    """Check parsing of nonstandard wind groups."""

    def report(wind_group):
      """(Macro) Return Metar object from parsing the given wind group."""
      return Metar.Metar(sta_time+wind_group)

    self.assertEqual( report("OOOOOKT").wind_speed.value(), 0 )
    self.assertEqual( report("OOOOOKT").wind(), "calm" )

    self.assertEqual( report("09010K").wind_speed.string(), "10 knots" )
    self.assertEqual( report("09010T").wind_speed.string(), "10 knots" )
    self.assertEqual( report("09010LT").wind_speed.string(), "10 knots" )
    self.assertEqual( report("09010KTS").wind_speed.string(), "10 knots" )
    self.assertEqual( report("09010").wind_speed.string(), "10 mps" )

    self.assertEqual( report("VRBOOK").wind_speed.value(), 0 )
    self.assertEqual( report("VRBOOK").wind(), "calm" )

    self.assertEqual( report("///00KT").wind(), "calm" )
    self.assertEqual( report("/////KT").wind(), "missing" )
    self.assertEqual( report("000//KT").wind(), "missing" )
    self.assertEqual( report("/////").wind(), "missing" )

    self.assertEqual( report("09010G//KT").wind_gust, None )
    self.assertEqual( report("09010GMKT").wind_gust, None )
    self.assertEqual( report("09010GMMKT").wind_gust, None )
    self.assertEqual( report("09010G7KT").wind_gust.value(), 7 )

    self.assertEqual( report("MMM00KT").wind(), "calm" )
    self.assertEqual( report("MMMMMKT").wind(), "missing" )
    self.assertEqual( report("000MMKT").wind(), "missing" )
    self.assertEqual( report("MMMMM").wind(), "missing" )
    self.assertEqual( report("MMMMMGMMKT").wind(), "missing" )
    self.assertEqual( report("MMMMMG01KT").wind(), "missing" )

  def test_142_parseWind_illegal(self):
    """Check rejection of illegal wind groups."""
    self.raisesParserError( sta_time+"90010KT" )
    self.raisesParserError( sta_time+"9010KT" )
    self.raisesParserError( sta_time+"09010 KT" )
    self.raisesParserError( sta_time+"09010FPS" )
    self.raisesParserError( sta_time+"09010MPH" )
    self.raisesParserError( sta_time+"00///KT" )
    self.raisesParserError( sta_time+"VAR10KT" )
    self.raisesParserError( sta_time+"21010KT 180-240" )
    self.raisesParserError( sta_time+"123UnME" )

  def test_150_parseVisibility(self):
    """Check parsing of visibility groups."""

    def report(vis_group):
      """(Macro) Return Metar object for a report containing the given visibility group."""
      return Metar.Metar(sta_time+"09010KT "+vis_group)

    self.assertEqual( report("10SM").vis.value(), 10 )
    self.assertEqual( report("10SM").vis_dir, None )
    self.assertEqual( report("10SM").max_vis, None )
    self.assertEqual( report("10SM").max_vis_dir, None )
    self.assertEqual( report("10SM").visibility(), "10 miles" )

    self.assertEqual( report("3/8SM").vis.value(), 0.375 )
    self.assertEqual( report("3/8SM").vis_dir, None )
    self.assertEqual( report("3/8SM").max_vis, None )
    self.assertEqual( report("3/8SM").max_vis_dir, None )
    self.assertEqual( report("3/8SM").visibility(), "3/8 miles" )

    self.assertEqual( report("1 3/4SM").vis.value(), 1.75 )
    self.assertEqual( report("1 3/4SM").vis_dir, None )
    self.assertEqual( report("1 3/4SM").max_vis, None )
    self.assertEqual( report("1 3/4SM").max_vis_dir, None )
    self.assertEqual( report("1 3/4SM").visibility(), "1 3/4 miles" )

    self.assertEqual( report("5000").vis.value(), 5000 )
    self.assertEqual( report("5000").vis_dir, None )
    self.assertEqual( report("5000").visibility(), "5000 meters" )
    self.assertEqual( report("5000M").visibility(), "5000 meters" )

    self.assertEqual( report("CAVOK").vis.value(), 10000 )
    self.assertEqual( report("CAVOK").vis_dir, None )
    self.assertEqual( report("CAVOK").max_vis, None )
    self.assertEqual( report("CAVOK").max_vis_dir, None )
    self.assertEqual( report("CAVOK").visibility(), "10000 meters" )

    self.assertEqual( report("1000W 3000").vis.value(), 1000 )
    self.assertEqual( report("1000W 3000").vis_dir.value(), 270 )
    self.assertEqual( report("1000W 3000").max_vis.value(), 3000 )
    self.assertEqual( report("1000W 3000").max_vis_dir, None )
    self.assertEqual( report("1000W 3000").visibility(), "1000 meters to W; 3000 meters" )

    self.assertEqual( report("1000 3000NE").vis.value(), 1000 )
    self.assertEqual( report("1000 3000NE").vis_dir, None )
    self.assertEqual( report("1000 3000NE").max_vis.value(), 3000 )
    self.assertEqual( report("1000 3000NE").max_vis_dir.value(), 45 )
    self.assertEqual( report("1000 3000NE").visibility(), "1000 meters; 3000 meters to NE" )

    self.assertEqual( report("5KM").vis.value(), 5 )
    self.assertEqual( report("5KM").vis_dir, None )
    self.assertEqual( report("5KM").visibility(), "5.0 km" )

    self.assertEqual( report("5000E").vis.value(), 5000 )
    self.assertEqual( report("5000E").visibility(), "5000 meters to E" )

    self.assertEqual( report("7000NDV").vis.value(), 7000 )
    self.assertEqual( report("7000NDV").vis_dir, None )
    self.assertEqual( report("7000NDV").visibility(), "7000 meters" )

    self.assertEqual( report("M1000").vis.value(), 1000 )
    self.assertEqual( report("M1000").visibility(), "less than 1000 meters" )

    self.assertEqual( report("P6000").vis.value(), 6000 )
    self.assertEqual( report("P6000").visibility(), "greater than 6000 meters" )

  def test_151_parseVisibility_direction(self):
    """Check parsing of compass headings visibility groups."""

    def report(vis_group):
      """(Macro) Return Metar object for a report containing the given visibility group."""
      return Metar.Metar(sta_time+"09010KT "+vis_group)

    self.assertEqual( report("5000N").vis_dir.compass(), "N" )
    self.assertEqual( report("5000N").vis_dir.value(), 0 )
    self.assertEqual( report("5000NE").vis_dir.compass(), "NE" )
    self.assertEqual( report("5000NE").vis_dir.value(), 45 )
    self.assertEqual( report("5000E").vis_dir.compass(), "E" )
    self.assertEqual( report("5000E").vis_dir.value(), 90 )
    self.assertEqual( report("5000SE").vis_dir.compass(), "SE" )
    self.assertEqual( report("5000SE").vis_dir.value(), 135 )
    self.assertEqual( report("5000S").vis_dir.compass(), "S" )
    self.assertEqual( report("5000S").vis_dir.value(), 180 )
    self.assertEqual( report("5000SW").vis_dir.compass(), "SW" )
    self.assertEqual( report("5000SW").vis_dir.value(), 225 )
    self.assertEqual( report("5000W").vis_dir.compass(), "W" )
    self.assertEqual( report("5000W").vis_dir.value(), 270 )
    self.assertEqual( report("5000NW").vis_dir.compass(), "NW" )
    self.assertEqual( report("5000NW").vis_dir.value(), 315 )

  def test_152_parseVisibility_with_following_temperature(self):
    """Check parsing of visibility groups followed immediately by a temperature group."""

    def report(vis_group):
      """(Macro) Return Metar object for a report containing the given visibility group."""
      return Metar.Metar(sta_time+"09010KT "+vis_group)

    self.assertEqual( report("CAVOK 02/01").vis.value(), 10000 )
    self.assertEqual( report("CAVOK 02/01").vis_dir, None )
    self.assertEqual( report("CAVOK 02/01").max_vis, None )
    self.assertEqual( report("CAVOK 02/01").temp.value(), 2.0 )
    self.assertEqual( report("CAVOK 02/01").dewpt.value(), 1.0 )

    self.assertEqual( report("5000 02/01").vis.value(), 5000 )
    self.assertEqual( report("5000 02/01").vis_dir, None )
    self.assertEqual( report("5000 02/01").max_vis, None )
    self.assertEqual( report("5000 02/01").temp.value(), 2.0 )
    self.assertEqual( report("5000 02/01").dewpt.value(), 1.0 )

  def test_290_ranway_state(self):
    """Check parsing of runway state groups."""

    def report(runway_state):
      """(Macro) Return Metar object for a report containing the given runway state group"""
      sample_metar = 'EGNX 191250Z VRB03KT 9999 -RASN FEW008 SCT024 BKN046 M01/M03 Q0989 '
      return Metar.Metar(sample_metar+' '+runway_state)

    self.assertEqual( report('09690692 27550591').temp.value(), -1.0 )
    self.assertEqual( report('09690692 27550591').remarks(), "" )

    self.assertEqual( report('09SNOCLO').remarks(), "" )
    self.assertEqual( report('09CLRD//').remarks(), "" )

  def test_300_parseTrend(self):
    """Check parsing of trend forecasts."""

    def report(trend_group, remarks=""):
      """(Macro)
      Return Metar object for a report containing the given trend
      forecast and remarks.
      """
      sample_metar = sta_time+"09010KT 10SM -SN OVC020 23/05 Q1001"
      return Metar.Metar(sample_metar+' '+trend_group+' '+remarks)

    self.assertEqual( report('TEMPO FM0306 BKN030CU').trend(), 'TEMPO FM0306 BKN030CU' )
    self.assertEqual( report('TEMPO FM0306 BKN030CU').temp.value(), 23.0 )
    self.assertEqual( report('TEMPO FM0306 BKN030CU').remarks(), "" )

    self.assertEqual( report('BECMG 0306 VRB06KT').trend(), 'BECMG 0306 VRB06KT' )
    self.assertEqual( report('FCST AT0327 +FC').trend(), 'FCST AT0327 +FC' )

    self.assertEqual( report('TEMPO 0306 1/2SM').trend(), 'TEMPO 0306 1/2SM' )
    self.assertEqual( report('TEMPO FM0306 TL0345 01030G50KT').trend(),
                      'TEMPO FM0306 TL0345 01030G50KT')

    self.assertEqual( report('TEMPO 0306 RMK 402500072').trend(), 'TEMPO 0306' )
    self.assertEqual( report('TEMPO 0306 RMK 402500072').max_temp_24hr.value(), 25.0 )

if __name__=='__main__':
  unittest.main( )

