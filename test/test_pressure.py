import unittest
import metar

class PressureTest(unittest.TestCase):
  
  def testDefaults(self):
    self.assertEqual( metar.pressure("1000").value(), 1000.0 )
    self.assertEqual( metar.pressure("1000","HPA").value(), 1000.0 )
    self.assertEqual( metar.pressure("30","in").value(), 30.0 )
    self.assertEqual( metar.pressure("30","in").string(), "30.00 inches" )
    self.assertEqual( metar.pressure("1000").value("MB"), 1000 )
    self.assertEqual( metar.pressure("1000").string(), "1000.0 mb" )
    self.assertEqual( metar.pressure("1000","HPA").string(), "1000.0 hPa" )
  
  def testInputs(self):
    self.assertEqual( metar.pressure("1000").value(), 1000.0 )
    self.assertEqual( metar.pressure("1000.0").value(), 1000.0 )
    self.assertEqual( metar.pressure(1000).value(), 1000.0 )
    self.assertEqual( metar.pressure(1000.0).value(), 1000.0 )
    
    self.assertEqual( metar.pressure("1000", "mb").value(), 1000.0 )
    self.assertEqual( metar.pressure("1000", "hPa").value(), 1000.0 )
    self.assertEqual( metar.pressure("30.00", "in").value(), 30.0 )
    
    self.assertEqual( metar.pressure("1000", "MB").value("MB"), 1000.0 )
    self.assertEqual( metar.pressure("1000", "MB").value("HPA"), 1000.0 )
    self.assertEqual( metar.pressure("1000", "HPA").value("mb"), 1000.0 )
  
  def testErrorChecking(self):
    self.assertRaises( ValueError, metar.pressure, "A2995" )
    self.assertRaises( metar.UnitsError, metar.pressure, "1000", "bars" )
    self.assertRaises( metar.UnitsError, metar.pressure("30.00").value, "psi" )
    self.assertRaises( metar.UnitsError, metar.pressure("32.00").string, "atm" )
  
  def testConversions(self):
    self.assertEqual( metar.pressure("30","in").value("in"), 30.0 )
    self.assertAlmostEqual( metar.pressure("30","in").value("mb"), 1015.92, 2 )
    self.assertAlmostEqual( metar.pressure("30","in").value("hPa"), 1015.92, 2 )

    self.assertEqual( metar.pressure("30","in").string("in"), "30.00 inches" )
    self.assertEqual( metar.pressure("30","in").string("mb"), "1015.9 mb" )
    self.assertEqual( metar.pressure("30","in").string("hPa"), "1015.9 hPa" )
    
    self.assertEqual( metar.pressure("1000","mb").value("mb"), 1000.0 )
    self.assertEqual( metar.pressure("1000","mb").value("hPa"), 1000.0 )
    self.assertAlmostEqual( metar.pressure("1000","mb").value("in"), 29.5299, 4 )
    self.assertAlmostEqual( metar.pressure("1000","hPa").value("in"), 29.5299, 4 )
    
if __name__=='__main__':
  unittest.main()
  