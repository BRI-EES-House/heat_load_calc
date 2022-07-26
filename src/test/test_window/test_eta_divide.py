import unittest

from heat_load_calc.window import Window
from heat_load_calc.window import GlazingType


class MyTestCase(unittest.TestCase):

    def test_eta_divide(self):
        """
        日射熱取得率から透過率と吸収日射取得率を分離するモデルのテスト

        """

        w = Window(r_a_glass_j=0.8, eta_w_j=0.7, glazing_type_j=GlazingType.Multiple)
        self.assertAlmostEqual(w.tau_w_j, 0.63590625)
        self.assertAlmostEqual(w.b_w_j, 0.06409375)
        self.assertAlmostEqual(w.a_w_j, 0.16409375)
        self.assertAlmostEqual(w.rho_w_j, 0.00000000)

        w = Window(r_a_glass_j=0.8, eta_w_j=0.2, glazing_type_j=GlazingType.Multiple)
        self.assertAlmostEqual(w.tau_w_j, 0.12825)
        self.assertAlmostEqual(w.b_w_j, 0.07175)
        self.assertAlmostEqual(w.a_w_j, 0.26978000)
        self.assertAlmostEqual(w.rho_w_j, 0.40197000)

        w = Window(r_a_glass_j=0.8, eta_w_j=0.6, glazing_type_j=GlazingType.Single)
        self.assertAlmostEqual(w.tau_w_j, 0.52275)
        self.assertAlmostEqual(w.b_w_j, 0.07725)
        self.assertAlmostEqual(w.a_w_j, 0.23252250)
        self.assertAlmostEqual(w.rho_w_j, 0.04472750)

        w = Window(r_a_glass_j=0.8, eta_w_j=0.2, glazing_type_j=GlazingType.Single)
        self.assertAlmostEqual(w.tau_w_j, 0.05025)
        self.assertAlmostEqual(w.b_w_j, 0.14975)
        self.assertAlmostEqual(w.a_w_j, 0.45074750)
        self.assertAlmostEqual(w.rho_w_j, 0.29900250)

        w = Window(r_a_glass_j=0.8, eta_w_j=0.792, glazing_type_j=GlazingType.Multiple)
        self.assertAlmostEqual(w.tau_w_j, 0.73550347)
        self.assertAlmostEqual(w.b_w_j, 0.05649653)
        self.assertAlmostEqual(w.a_w_j, 0.06449653)
        self.assertAlmostEqual(w.rho_w_j, 0.00000000)


if __name__ == '__main__':
    unittest.main()
