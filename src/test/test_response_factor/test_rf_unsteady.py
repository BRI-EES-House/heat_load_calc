import unittest
import numpy as np

from heat_load_calc import response_factor as rf
from heat_load_calc.response_factor import ResponseFactor


class MyTestCase(unittest.TestCase):

    def test_rf_genera_part(self):
        """
        一般部位の応答係数初項、指数項別応答係数のテスト
        """

        print('\n testing response factor general part')

        # 壁体構成
        # 石こうボード 9mm
        # 非密閉中空層
        # コンクリート 90mm
        # 押出法ポリスチレンフォーム保温板2種 100mm
        # モルタル 30mm
        # 室外側熱伝達率

        # 単位面積あたりの熱容量, kJ / m2 K
        cs = np.array([7.47, 0.0, 180.0, 3.6, 48.0])
        # 熱抵抗, m2 K/W
        rs = np.array([0.0409090909, 0.070000, 0.0562500000, 2.9411764706, 0.020000])

        # 応答係数の計算
        rft: rf.ResponseFactor = ResponseFactor.create_for_unsteady_not_ground(cs=cs, rs=rs, r_o=0.04)

        # RFA0の確認
        self.assertAlmostEqual(0.05936024851637489, rft.rfa0)

        # RFT0の確認
        self.assertAlmostEqual(6.249040344452617e-05, rft.rft0)

        print(rft.rfa1)
        print(rft.rft1)

        # 指数項別吸熱応答係数の確認
        self.assertAlmostEqual(-1.13989133e-05, rft.rfa1[0])
        self.assertAlmostEqual(1.02748351e-04, rft.rfa1[1])
        self.assertAlmostEqual(-4.81002013e-04, rft.rfa1[2])
        self.assertAlmostEqual(3.49960611e-03, rft.rfa1[3])
        self.assertAlmostEqual(2.47517060e-03, rft.rfa1[4])
        self.assertAlmostEqual(-1.44373441e-03, rft.rfa1[5])
        self.assertAlmostEqual(1.48281651e-03, rft.rfa1[6])
        self.assertAlmostEqual(-2.47943318e-03, rft.rfa1[7])
        self.assertAlmostEqual(1.09630293e-02, rft.rfa1[8])
        self.assertAlmostEqual(3.29667340e-02, rft.rfa1[9])

        # 指数項別貫流応答係数の確認
        self.assertAlmostEqual(-2.66672824e-06, rft.rft1[0])
        self.assertAlmostEqual(2.51698857e-05, rft.rft1[1])
        self.assertAlmostEqual(-1.28979158e-04, rft.rft1[2])
        self.assertAlmostEqual(1.09059713e-03, rft.rft1[3])
        self.assertAlmostEqual(9.62571633e-04, rft.rft1[4])
        self.assertAlmostEqual(-7.51043238e-04, rft.rft1[5])
        self.assertAlmostEqual(1.08244908e-03, rft.rft1[6])
        self.assertAlmostEqual(-2.63156034e-03, rft.rft1[7])
        self.assertAlmostEqual(-4.52005140e-04, rft.rft1[8])
        self.assertAlmostEqual(7.84699977e-04, rft.rft1[9])

    def test_rf_ground_part(self):
        """
        土壌の応答係数初項、指数項別応答係数のテスト
        """

        print('\n testing response factor ground part')

        # 壁体構成
        # 押出法ポリスチレンフォーム保温板2種 30mm
        # コンクリート 120mm
        # 土壌 3000mm

        # 単位面積あたりの熱容量, kJ / m2 K
        cs = np.array([1.080000, 240.000000])
        # 熱抵抗, m2 K / W
        rs = np.array([0.8823529412, 0.0750000000])

        # 応答係数の計算
        rft = ResponseFactor.create_for_unsteady_ground(cs=cs, rs=rs)

        # RFA0の確認
        self.assertAlmostEqual(0.7153374350138639, rft.rfa0)

        # RFT0の確認
        self.assertAlmostEqual(1.0, rft.rft0)

        # 指数項別吸熱応答係数の確認
        self.assertAlmostEqual(-4.932291953561631e-07, rft.rfa1[0])
        self.assertAlmostEqual(1.1848402120231172e-05, rft.rfa1[1])
        self.assertAlmostEqual(0.00022864847810913559, rft.rfa1[2])
        self.assertAlmostEqual(-0.00014609989062409255, rft.rfa1[3])
        self.assertAlmostEqual(0.0005463330720022236, rft.rfa1[4])
        self.assertAlmostEqual(-0.00032414830484532136, rft.rfa1[5])
        self.assertAlmostEqual(0.0013791568569407097, rft.rfa1[6])
        self.assertAlmostEqual(0.0019867700951619544, rft.rfa1[7])
        self.assertAlmostEqual(-0.014622509832519151, rft.rfa1[8])
        self.assertAlmostEqual(0.07659670581003312, rft.rfa1[9])

        # 指数項別貫流応答係数の確認
        self.assertAlmostEqual(0.0, rft.rft1[0])
        self.assertAlmostEqual(0.0, rft.rft1[1])
        self.assertAlmostEqual(0.0, rft.rft1[2])
        self.assertAlmostEqual(0.0, rft.rft1[3])
        self.assertAlmostEqual(0.0, rft.rft1[4])
        self.assertAlmostEqual(0.0, rft.rft1[5])
        self.assertAlmostEqual(0.0, rft.rft1[6])
        self.assertAlmostEqual(0.0, rft.rft1[7])
        self.assertAlmostEqual(0.0, rft.rft1[8])
        self.assertAlmostEqual(0.0, rft.rft1[9])


if __name__ == '__main__':
    unittest.main()
