import unittest
from metar import Metar

class MetarTest(unittest.TestCase):
  
  def testErrorChecking(self):
    pass
      
  def test_parseType(self):
    self.assertEqual(Metar.Metar("METAR").type, "METAR")
    self.assertEqual(Metar.Metar("SPECI").type, "SPECI")
    self.assertEqual(Metar.Metar("KEWR").type, None)
    self.assertRaises(Metar.ParserError, Metar.Metar, "TAF")
      
  def test_parseStation(self):
    self.assertEqual(Metar.Metar("KEWR").station_id, "KEWR")
    self.assertEqual(Metar.Metar("BIX1").station_id, "BIX1")
    self.assertEqual(Metar.Metar("K2G6").station_id, "K2G6")
    self.assertRaises(Metar.ParserError, Metar.Metar, "1ABC")
    self.assertRaises(Metar.ParserError, Metar.Metar, "kewr")
      
  def test_parseModifier(self):
    self.assertEqual(Metar.Metar("KEWR").mod, "AUTO")
    self.assertEqual(Metar.Metar("KEWR 101651Z AUTO").mod, "AUTO")
    self.assertEqual(Metar.Metar("KEWR 101651Z COR").mod, "COR")
    self.assertRaises(Metar.ParserError, Metar.Metar, "KEWR 101651Z MAN")

if __name__=='__main__':
  unittest.main()
  
