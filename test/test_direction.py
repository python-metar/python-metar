import unittest
import metar

class DirectionTest(unittest.TestCase):
  
  def testUsage(self):
    self.assertEqual( metar.direction("90").value(), 90.0 )
    self.assertEqual( metar.direction(90).value(), 90.0 )
    self.assertEqual( metar.direction(90.0).value(), 90.0 )
    self.assertEqual( metar.direction("90").string(), "90 degrees" )
    self.assertEqual( metar.direction("E").compass(), "E" )
   
  def testErrorChecking(self):
    self.assertRaises( ValueError, metar.direction, "North" )
    self.assertRaises( ValueError, metar.direction, -10 )
    self.assertRaises( ValueError, metar.direction, "361" )
  
  def testConversion(self):
    self.assertEqual( metar.direction("N").value(),     0.0 )
    self.assertEqual( metar.direction("NNE").value(),  22.5 )
    self.assertEqual( metar.direction("NE").value(),   45.0 )
    self.assertEqual( metar.direction("ENE").value(),  67.5 )
    self.assertEqual( metar.direction("E").value(),    90.0 )
    self.assertEqual( metar.direction("ESE").value(), 112.5 )
    self.assertEqual( metar.direction("SE").value(),  135.0 )
    self.assertEqual( metar.direction("SSE").value(), 157.5 )
    self.assertEqual( metar.direction("S").value(),   180.0 )
    self.assertEqual( metar.direction("SSW").value(), 202.5 )
    self.assertEqual( metar.direction("SW").value(),  225.0 )
    self.assertEqual( metar.direction("WSW").value(), 247.5 )
    self.assertEqual( metar.direction("W").value(),   270.0 )
    self.assertEqual( metar.direction("WNW").value(), 292.5 )
    self.assertEqual( metar.direction("NW").value(),  315.0 )
    self.assertEqual( metar.direction("NNW").value(), 337.5 )
    
    self.assertEqual( metar.direction("0").compass(), "N" )
    self.assertEqual( metar.direction("5").compass(), "N" )
    self.assertEqual( metar.direction("355").compass(), "N" )
    self.assertEqual( metar.direction("20").compass(), "NNE" )
    self.assertEqual( metar.direction("60").compass(), "ENE" )
    self.assertEqual( metar.direction("247.5").compass(), "WSW" )
      
if __name__=='__main__':
  unittest.main()
  