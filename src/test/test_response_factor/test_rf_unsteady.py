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
        self.assertAlmostEqual(0.0582434301679216, rft.rfa0)

        # RFT0の確認
        self.assertAlmostEqual(-0.000370513942617035, rft.rft0)

        # 指数項別吸熱応答係数の確認
        self.assertAlmostEqual(0.00633284295989542, rft.rfa1[0])
        self.assertAlmostEqual(-0.00601108276357943, rft.rfa1[1])
        self.assertAlmostEqual(0.0183092470135399, rft.rfa1[2])
        self.assertAlmostEqual(-0.0523796496995946, rft.rfa1[3])
        self.assertAlmostEqual(0.12388159077215, rft.rfa1[4])
        self.assertAlmostEqual(-0.0820982480729517, rft.rfa1[5])
        self.assertAlmostEqual(0.02917993935613, rft.rfa1[6])
        self.assertAlmostEqual(-0.00372706369200161, rft.rfa1[7])

        # 指数項別貫流応答係数の確認
        self.assertAlmostEqual(0.00210303652017771, rft.rft1[0])
        self.assertAlmostEqual(-0.00199999627139724, rft.rft1[1])
        self.assertAlmostEqual(0.00612364415542993, rft.rft1[2])
        self.assertAlmostEqual(-0.0178740679525698, rft.rft1[3])
        self.assertAlmostEqual(0.0344846506858456, rft.rft1[4])
        self.assertAlmostEqual(-0.0355689007204028, rft.rft1[5])
        self.assertAlmostEqual(0.00974082074984926, rft.rft1[6])
        self.assertAlmostEqual(-0.00134313966906979, rft.rft1[7])

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
        cs = [1.080000, 240.000000]
        # 熱抵抗, m2 K / W
        rs = [0.8823529412, 0.0750000000]

        # 応答係数を計算する工場を作成
        rff = rf.ResponseFactorFactoryTransientGround(cs=cs, rs=rs)

        # 応答係数の計算
        rft: rf.ResponseFactor = rff.get_response_factors()

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
