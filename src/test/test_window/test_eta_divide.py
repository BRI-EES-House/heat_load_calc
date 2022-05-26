import unittest

from heat_load_calc.core import window


class MyTestCase(unittest.TestCase):

    def test_eta_divide(self):
        """
        日射熱取得率から透過率と吸収日射取得率を分離するモデルのテスト

        """

        print('testing dividing tau and ashgc from eta')

        tau_w, ashgc_w, rho_w, a_w = window.get_tau_and_ashgc_rho_a(eta_w=0.7, glazing_type_j='multiple', glass_area_ratio_j=0.8)
        self.assertAlmostEqual(tau_w, 0.63590625)
        self.assertAlmostEqual(ashgc_w, 0.06409375)
        self.assertAlmostEqual(a_w, 0.16409375)
        self.assertAlmostEqual(rho_w, 0.00000000)

        tau_w, ashgc_w, rho_w, a_w = window.get_tau_and_ashgc_rho_a(eta_w=0.2, glazing_type_j='multiple', glass_area_ratio_j=0.8)
        self.assertAlmostEqual(tau_w, 0.12825)
        self.assertAlmostEqual(ashgc_w, 0.07175)
        self.assertAlmostEqual(a_w, 0.26978000)
        self.assertAlmostEqual(rho_w, 0.40197000)

        tau_w, ashgc_w, rho_w, a_w = window.get_tau_and_ashgc_rho_a(eta_w=0.6, glazing_type_j='single', glass_area_ratio_j=0.8)
        self.assertAlmostEqual(tau_w, 0.52275)
        self.assertAlmostEqual(ashgc_w, 0.07725)
        self.assertAlmostEqual(a_w, 0.23252250)
        self.assertAlmostEqual(rho_w, 0.04472750)

        tau_w, ashgc_w, rho_w, a_w = window.get_tau_and_ashgc_rho_a(eta_w=0.2, glazing_type_j='single', glass_area_ratio_j=0.8)
        self.assertAlmostEqual(tau_w, 0.05025)
        self.assertAlmostEqual(ashgc_w, 0.14975)
        self.assertAlmostEqual(a_w, 0.45074750)
        self.assertAlmostEqual(rho_w, 0.29900250)

        tau_w, ashgc_w, rho_w, a_w = window.get_tau_and_ashgc_rho_a(eta_w=0.792, glazing_type_j='multiple', glass_area_ratio_j=0.8)
        self.assertAlmostEqual(tau_w, 0.73550347)
        self.assertAlmostEqual(ashgc_w, 0.05649653)
        self.assertAlmostEqual(a_w, 0.06449653)
        self.assertAlmostEqual(rho_w, 0.00000000)


if __name__ == '__main__':
    unittest.main()
