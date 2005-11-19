import unittest
from metar.Datatypes import speed, UnitsError

class SpeedTest(unittest.TestCase):
  
  def testDefaults(self):
    self.assertEqual( speed("10").value(), 10.0 )
    self.assertEqual( speed("5").string(), "5 mps" )
    self.assertEqual( speed("10", "KT").value(), 10.0 )
    self.assertEqual( speed("5", "KT").string(), "5 knots" )
    self.assertEqual( speed("5", "KMH").string(), "5 km/h" )
    self.assertEqual( speed("5", "MPH").string(), "5 mph" )
    self.assertEqual( speed("5",None).string(), "5 mps" )
  
  def testInputs(self):
    self.assertEqual( speed("10").value(), 10.0 )
    self.assertEqual( speed(10).value(), 10.0 )
    self.assertEqual( speed(10.0).value(), 10.0 )
    self.assertEqual( speed(10.0, None).value(), 10.0 )
    self.assertEqual( speed("10", gtlt=">").value(), 10.0 )
    self.assertEqual( speed("10", None, "<").value(), 10.0 )
  
  def testErrorChecking(self):
    self.assertRaises( ValueError, speed, "10KT" )
    self.assertRaises( ValueError, speed, "10", "MPS", "=" )
    self.assertRaises( ValueError, speed, "60", "KT", "gt" )
    self.assertRaises( UnitsError, speed, "10", "NM" )
    self.assertRaises( UnitsError, speed("10").value, "furlongs per fortnight" )
    self.assertRaises( UnitsError, speed("5").string, "fps" )
  
  def testConversions(self):
    self.assertEqual( speed("10", "MPS").value("MPS"), 10.0 )
    self.assertEqual( speed("10", "MPS").value("KMH"), 36.0 )
    self.assertAlmostEqual( speed("10", "MPS").value("MPH"), 22.4, 1 )
    self.assertAlmostEqual( speed("10", "MPS").value("KT"), 19.4, 1 )
    
    self.assertEqual( speed("10", "KT").value("KT"), 10.0 )
    self.assertAlmostEqual( speed("10", "KT").value("MPH"), 11.5, 1 )
    self.assertAlmostEqual( speed("10", "KT").value("MPS"), 5.1, 1 )
    self.assertAlmostEqual( speed("10", "KT").value("KMH"), 18.5, 1 )
    
    self.assertEqual( speed("10", "MPH").value("MPH"), 10.0 )
    self.assertAlmostEqual( speed("10", "MPH").value("KT"), 8.7, 1 )
    self.assertAlmostEqual( speed("10", "MPH").value("MPS"), 4.5, 1 )
    self.assertAlmostEqual( speed("10", "MPH").value("KMH"), 16.1, 1 )
    
    self.assertEqual( speed("10", "KMH").value("KMH"), 10.0 )
    self.assertAlmostEqual( speed("10", "KMH").value("KT"), 5.4, 1 )
    self.assertAlmostEqual( speed("10", "KMH").value("MPS"), 2.8, 1 )
    self.assertAlmostEqual( speed("10", "KMH").value("MPH"), 6.2, 1 )
    
if __name__=='__main__':
  unittest.main()
  
