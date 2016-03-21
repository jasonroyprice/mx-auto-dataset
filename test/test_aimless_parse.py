from custom_parser import get_summary
import unittest

class TestCustomParserDoesNotReturnNan(unittest.TestCase):
    def test1(self):
        summary = get_summary('aimless_10587c_nan.log')

        for key in summary.keys():
            value = summary[key]
            hasnan = False
            if type(value) is list:
                for val in value:
                    import math
                    if val is float:
                        self.assertFalse(math.isnan(val))
            else:
                if value is float:
                    self.assertFalse(math.isnan(val))

if __name__ == '__main__':
    unittest.main()