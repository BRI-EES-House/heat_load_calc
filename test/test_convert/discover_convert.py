import unittest

from test.test_convert import test_convert_lv2_to_lv3
from test.test_convert import test_convert_lv3_to_lv4
from test.test_convert import test_general_functions
from test.test_convert import test_convert_model_house_to_house_dict
from test.test_convert import test_model_house


def suite():

    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(test_convert_lv2_to_lv3.TestConvertLv2toLv3),
        unittest.TestLoader().loadTestsFromTestCase(test_convert_lv3_to_lv4.TestLV3toLV4),
        unittest.TestLoader().loadTestsFromTestCase(test_general_functions.TestRoundNumber),
        unittest.TestLoader().loadTestsFromTestCase(test_convert_model_house_to_house_dict.ConvertModelHouseToHouseDict),
        unittest.TestLoader().loadTestsFromTestCase(test_model_house.TestModelHouseResults),
        unittest.TestLoader().loadTestsFromTestCase(test_model_house.TestModelHouseShapeFactor)
    ])


if __name__ == "__main__":

    suites = suite()

    unittest.TextTestRunner(verbosity=3).run(suites)
