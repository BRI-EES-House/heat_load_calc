import unittest
import numpy as np

from heat_load_calc import earthen_floor


class TestEarthenFloorRF(unittest.TestCase):

    def test_rf_earthen_floor(self):
        """
        一般部位の応答係数初項、指数項別応答係数のテスト
        """

        print('\n testing response factor earthen floor')

        erf = earthen_floor.EarthenFloorRF(psi=0.5)

        # 線熱貫流率の確認
        self.assertAlmostEqual(erf.psi, 0.5)

        # 応答係数初項の確認
        self.assertAlmostEqual(erf.rfa0, -1.5846128580281293)
        self.assertAlmostEqual(erf.rft0, 0.2771039856689038)

        # 指数項別応答係数の確認
        rfa1 = np.array([ 1.78571394e-09, -8.62988324e-08, 2.48980922e-06, 8.67257037e-05,
                          -9.30606531e-05, 1.24816550e-03, -3.29774507e-03, 1.60700261e-02,
                          -4.71514659e-02, 3.92900385e-01])
        rft1 = np.array([ 1.77990057e-07, -1.38684354e-06, 6.24727535e-06, 6.98122337e-05,
                            -2.36870525e-05, 5.62622826e-04, -8.26723710e-04, 1.25294645e-02,
                            -6.00793753e-02, 3.13682117e-02])
        np.testing.assert_array_almost_equal(erf.rfa1, rfa1)
        np.testing.assert_array_almost_equal(erf.rft1, rft1)


if __name__ == '__main__':
    unittest.main()
