#
# Run all metar tests
#
import unittest

def suite():
    modules = ( "test_metar", "test_pressure", "test_speed", 
                "test_temperature", "test_direction", "test_distance")
    alltests = unittest.TestSuite()
    for module in map(__import__, modules):
        alltests.addTest(unittest.findTestCases(module))
    return alltests

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

