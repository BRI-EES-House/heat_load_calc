import unittest

from heat_load_calc.initializer import window


class MyTestCase(unittest.TestCase):

    def test_eta_devide(self):
        '''
        日射熱取得率から透過率と吸収日射取得率を分離するモデルのテスト
        :return:
        '''

        print('devide tau and ashgc from eta')

        tau_w, ashgc_w = window.get_tau_and_ashgc(eta_w=0.7, glazing_type_j='multiple', glass_area_ratio_j=0.8)
        self.assertAlmostEqual(tau_w, 0.63590625)
        self.assertAlmostEqual(ashgc_w, 0.06409375)

        tau_w, ashgc_w = window.get_tau_and_ashgc(eta_w=0.2, glazing_type_j='multiple', glass_area_ratio_j=0.8)
        self.assertAlmostEqual(tau_w, 0.12825)
        self.assertAlmostEqual(ashgc_w, 0.07175)

        tau_w, ashgc_w = window.get_tau_and_ashgc(eta_w=0.6, glazing_type_j='single', glass_area_ratio_j=0.8)
        self.assertAlmostEqual(tau_w, 0.52275)
        self.assertAlmostEqual(ashgc_w, 0.07725)

        tau_w, ashgc_w = window.get_tau_and_ashgc(eta_w=0.2, glazing_type_j='single', glass_area_ratio_j=0.8)
        self.assertAlmostEqual(tau_w, 0.05025)
        self.assertAlmostEqual(ashgc_w, 0.14975)


if __name__ == '__main__':
    unittest.main()
