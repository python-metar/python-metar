import unittest
from metar.Datatypes import direction

def suite():
  return unittest.makeSuite(DirectionTest)

class DirectionTest(unittest.TestCase):
  
  def testUsage(self):
    self.assertEqual( direction("90").value(), 90.0 )
    self.assertEqual( direction(90).value(), 90.0 )
    self.assertEqual( direction(90.0).value(), 90.0 )
    self.assertEqual( direction("90").string(), "90 degrees" )
    self.assertEqual( direction("E").compass(), "E" )
   
  def testErrorChecking(self):
    self.assertRaises( ValueError, direction, "North" )
    self.assertRaises( ValueError, direction, -10 )
    self.assertRaises( ValueError, direction, "361" )
  
  def testConversion(self):
    self.assertEqual( direction("N").value(),     0.0 )
    self.assertEqual( direction("NNE").value(),  22.5 )
    self.assertEqual( direction("NE").value(),   45.0 )
    self.assertEqual( direction("ENE").value(),  67.5 )
    self.assertEqual( direction("E").value(),    90.0 )
    self.assertEqual( direction("ESE").value(), 112.5 )
    self.assertEqual( direction("SE").value(),  135.0 )
    self.assertEqual( direction("SSE").value(), 157.5 )
    self.assertEqual( direction("S").value(),   180.0 )
    self.assertEqual( direction("SSW").value(), 202.5 )
    self.assertEqual( direction("SW").value(),  225.0 )
    self.assertEqual( direction("WSW").value(), 247.5 )
    self.assertEqual( direction("W").value(),   270.0 )
    self.assertEqual( direction("WNW").value(), 292.5 )
    self.assertEqual( direction("NW").value(),  315.0 )
    self.assertEqual( direction("NNW").value(), 337.5 )
    
    self.assertEqual( direction("0").compass(), "N" )
    self.assertEqual( direction("5").compass(), "N" )
    self.assertEqual( direction("355").compass(), "N" )
    self.assertEqual( direction("20").compass(), "NNE" )
    self.assertEqual( direction("60").compass(), "ENE" )
    self.assertEqual( direction("247.5").compass(), "WSW" )
      
if __name__=='__main__':
  unittest.main()
  
