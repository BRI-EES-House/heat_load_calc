import unittest

from heat_load_calc.core import response_factor as rf


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

        # 熱容量[kJ/m2 K]
        cs = [7.47, 0.0, 180.0, 3.6, 48.0]
        # 熱抵抗[m2 K/W]
        rs = [0.0409090909, 0.070000, 0.0562500000, 2.9411764706, 0.020000]

        # 応答係数を計算する工場を作成
        rff = rf.ResponseFactorFactoryTransientEnvelope(cs=cs, rs=rs, r_o=0.04)

        # 応答係数の計算
        rft: rf.ResponseFactor = rff.get_response_factors()

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

        # 熱容量[kJ/m2 K]
        cs = [1.080000, 240.000000]
        # 熱抵抗[m2 K/W]
        rs = [0.8823529412, 0.0750000000]

        # 応答係数を計算する工場を作成
        rff = rf.ResponseFactorFactoryTransientGround(cs=cs, rs=rs)

        # 応答係数の計算
        rft: rf.ResponseFactor = rff.get_response_factors()

        # RFA0の確認
        self.assertAlmostEqual(0.724907397092839, rft.rfa0)

        # RFT0の確認
        self.assertAlmostEqual(1.0, rft.rft0)

        # 指数項別吸熱応答係数の確認
        self.assertAlmostEqual(-1.07167494987018E-08, rft.rfa1[0])
        self.assertAlmostEqual(2.08189010050113E-07, rft.rfa1[1])
        self.assertAlmostEqual(-2.75932440530367E-06, rft.rfa1[2])
        self.assertAlmostEqual(0.000145439349961729, rft.rfa1[3])
        self.assertAlmostEqual(0.0000965074343781571, rft.rfa1[4])
        self.assertAlmostEqual(0.000174519738283692, rft.rfa1[5])
        self.assertAlmostEqual(0.000524125506538959, rft.rfa1[6])
        self.assertAlmostEqual(0.00153299929341512, rft.rfa1[7])
        self.assertAlmostEqual(-0.00624720902369905, rft.rfa1[8])
        self.assertAlmostEqual(0.0624448755908967, rft.rfa1[9])

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
