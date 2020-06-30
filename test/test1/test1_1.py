import unittest

from heat_load_calc.core import core

def add_test(a,b):
    return a*b

class MyTestCase(unittest.TestCase):
    def test_something1(self):
        #core.calc(input_data_dir='data', output_data_dir='data')
        assert False

    def test_something2(self):
        real_value=add_test(a=1, b=3)
        expected_value=4

        assert real_value==expected_value

    def test_something3(self):
        print('test_something3')
        assert False

if __name__ == '__main__':
    unittest.main()
