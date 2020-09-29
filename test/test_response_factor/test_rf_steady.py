import unittest

from heat_load_calc.initializer import response_factor


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        print('\n testing response factor')

    def test_rf_steady(self):

        # NOTE: n_root は将来的に破棄する予定のためテストはしない。

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

                # 応答係数を作成する工場を作成
                rff = response_factor.ResponseFactorFactorySteady(u_w=u_w, r_i=r_i)

                # 応答係数の作成
                rf: response_factor.ResponseFactor = rff.get_response_factors()

                # RFA0 の確認
                self.assertAlmostEqual(rf.rfa0, expected_rfa0)

                # RFA1 の確認　（12個）
                for i in range(12):
                    self.assertAlmostEqual(rf.rfa1[i], expected_rfa1[i])

                # RFT0 の確認
                self.assertAlmostEqual(rf.rft0, expected_rft0)

                # RFT1 の確認　（12個）
                for i in range(12):
                    self.assertAlmostEqual(rf.rfa1[i], expected_rft1[i])


if __name__ == '__main__':
    unittest.main()
