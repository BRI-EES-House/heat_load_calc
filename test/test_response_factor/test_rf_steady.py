import unittest

from heat_load_calc import response_factor
from heat_load_calc.response_factor import ResponseFactor


class MyTestCase(unittest.TestCase):

    def test_rf_steady(self):

        test_patterns = [
            (2.0, 0.11,
             0.39, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
             1.0, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            (2.5, 0.15,
             0.25, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
             1.0, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
        ]

        for u_w, r_i, expected_rfa0, expected_rfa1, expected_rft0, expected_rft1 in test_patterns:
            with self.subTest(u_w=u_w, r_i=r_i):

                # 応答係数の作成
                rf: ResponseFactor = ResponseFactor.create_for_steady(u_w=u_w, r_i=r_i)

                # RFA0 の確認
                self.assertAlmostEqual(rf.rfa0, expected_rfa0)

                # RFA1 の確認　（12個）
                for result, expected in zip(rf.rfa1, expected_rfa1):
                    self.assertAlmostEqual(result, expected)

                # RFT0 の確認
                self.assertAlmostEqual(rf.rft0, expected_rft0)

                # RFT1 の確認　（12個）
                for result, expected in zip(rf.rft1, expected_rft1):
                    self.assertAlmostEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
