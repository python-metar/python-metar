import unittest
import metar

class MetarTest(unittest.TestCase):
  
  def testErrorChecking(self):
    pass
      
  def test_parseType(self):
    self.assertEqual(metar.metar("METAR").type, "METAR")
    self.assertEqual(metar.metar("SPECI").type, "SPECI")
    self.assertEqual(metar.metar("KEWR").type, None)
    self.assertRaises(metar.ParserError, metar.metar, "TAF")
      
  def test_parseStation(self):
    self.assertEqual(metar.metar("KEWR").station_id, "KEWR")
    self.assertEqual(metar.metar("BIX1").station_id, "BIX1")
    self.assertEqual(metar.metar("K2G6").station_id, "K2G6")
    self.assertRaises(metar.ParserError, metar.metar, "1ABC")
    self.assertRaises(metar.ParserError, metar.metar, "kewr")
      
  def test_parseModifier(self):
    self.assertEqual(metar.metar("KEWR").mod, "AUTO")
    self.assertEqual(metar.metar("KEWR 101651Z AUTO").mod, "AUTO")
    self.assertEqual(metar.metar("KEWR 101651Z COR").mod, "COR")
    self.assertRaises(metar.ParserError, metar.metar, "KEWR 101651Z MAN")
    
if __name__=='__main__':
  unittest.main()
  