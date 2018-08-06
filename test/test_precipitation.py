import unittest
from metar.Datatypes import precipitation

class PrecipitationTest(unittest.TestCase):

  def test_trace(self):
    """How do we handle trace reports"""
    self.assertEqual( precipitation("0000", "IN").string(), "Trace" )
    self.assertTrue( precipitation("0000", "IN").istrace() )
    self.assertFalse( precipitation("0010", "IN").istrace() )
    
if __name__=='__main__':
  unittest.main()
  
