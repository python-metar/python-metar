import unittest
from metar import Metar

# METAR fragments used in tests, below
sta_time = "KEWR 101651Z "
sta_time_mod = "KEWR 101651Z AUTO "
sta_time_wind = "KEWR 101651Z 00000KT "

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
      
  def test_030_parseModifier_default(self):
    """Check default 'modifier' value."""
    self.assertEqual( Metar.Metar("KEWR").mod, "AUTO" )
      
  def test_031_parseModifier(self):
    """Check parsing of 'modifier' groups."""
    self.assertEqual( Metar.Metar(sta_time+"AUTO").mod, "AUTO" )
    self.assertEqual( Metar.Metar(sta_time+"COR").mod, "COR" )
      
  def test_032_parseModifier_nonstd(self):
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
      
  def test_033_parseModifier_illegal(self):
    """Check rejection of illegal 'modifier' groups."""
#    self.raisesParserError( "KEWR AUTO" )
    self.raisesParserError( sta_time+"auto" )
    self.raisesParserError( sta_time+"CCH" )
    self.raisesParserError( sta_time+"MAN" )
      
  def test_040_parseWind(self):
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
      
  def test_041_parseWind_nonstd(self):
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
      
  def test_042_parseWind_illegal(self):
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

if __name__=='__main__':
  unittest.main( )
  
