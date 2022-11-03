import unittest
from math import radians

from heat_load_calc.window import Window


class TestWindow(unittest.TestCase):

    def test_u_w_f(self):
        
        self.assertEqual(Window(u_w_j=0.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE).u_w_f_j, 4.7)
        self.assertEqual(Window(u_w_j=0.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, flame_type=Window.FlameType.RESIN).u_w_f_j, 2.2)
        self.assertEqual(Window(u_w_j=0.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, flame_type=Window.FlameType.WOOD).u_w_f_j, 2.2)
        self.assertEqual(Window(u_w_j=0.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, flame_type=Window.FlameType.MIXED_WOOD).u_w_f_j, 4.7)
        self.assertEqual(Window(u_w_j=0.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, flame_type=Window.FlameType.MIXED_RESIN).u_w_f_j, 4.7)
        self.assertEqual(Window(u_w_j=0.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, flame_type=Window.FlameType.ALUMINUM).u_w_f_j, 6.6)

    def test_r_a_w_g_j(self):

        # r_a_w_g_j と flame_type どちらも指定しない場合
        self.assertEqual(Window(u_w_j=0.1, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE).r_a_w_g_j, 0.8)
        # flame_type のみ指定しない場合
        self.assertEqual(Window(u_w_j=0.1, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.55).r_a_w_g_j, 0.55)
        # r_a_w_g_j のみ指定しない場合
        self.assertEqual(Window(u_w_j=0.1, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, flame_type=Window.FlameType.RESIN).r_a_w_g_j, 0.72)
        self.assertEqual(Window(u_w_j=0.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, flame_type=Window.FlameType.WOOD).r_a_w_g_j, 0.72)
        self.assertEqual(Window(u_w_j=0.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, flame_type=Window.FlameType.MIXED_WOOD).r_a_w_g_j, 0.8)
        self.assertEqual(Window(u_w_j=0.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, flame_type=Window.FlameType.MIXED_RESIN).r_a_w_g_j, 0.8)
        self.assertEqual(Window(u_w_j=0.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, flame_type=Window.FlameType.ALUMINUM).r_a_w_g_j, 0.8)
        # どちらも指定する場合
        self.assertEqual(Window(u_w_j=0.1, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.55, flame_type=Window.FlameType.RESIN).r_a_w_g_j, 0.55)

    def test_u_w_g_j(self):

        # (3.0 - 2.2 * 0.28) / 0.72
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN).u_w_g_j, 3.3111111)

    def test_eta_w_g_j(self):
        
        # 0.5 / 0.72
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN).eta_w_g_j, 0.6944444)

    def test_u_w_g_s_j(self):
        # 1 / (1 / 3.3111111 - 0.0415 - 0.1228 + 0.0756 + 0.1317)
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._u_w_g_s_j, 2.89843795)

    def test_r_r_w_g_j(self):
        # ((1 / 2) * (1 / 3.3111111 - 0.0415 - 0.1228) + 0.0756) * 2.89843795
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._r_r_w_g_j, 0.4186988)
        # ((1 / 4) * (1 / 3.3111111 - 0.0415 - 0.1228 - 0.003) + 0.0756) * 2.89843795
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._r_r_w_g_j, 0.3167365)

    def test_rho_w_g_s1f_j(self):
        # t_j = (-1.846 * 0.4186988 + ((1.846 * 0.4186988)**2 + 4 * (1 - 1.846 * 0.4186988) * 0.6944444)**0.5) / (2 * (1 - 1.846 * 0.4186988))
        # 0.923 * (t_j ** 2) - 1.846 * t_j + 1
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._rho_w_g_s1f_j, 0.1402048)

        # t_j = (-1.846 * 0.3167365 + ((1.846 * 0.3167365)**2 + 4 * (1 - 1.846 * 0.3167365) * 0.6944444)**0.5) / (2 * (1 - 1.846 * 0.3167365))
        # 0.923 * (t_j ** 2) - 1.846 * t_j + 1
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._rho_w_g_s1f_j, 0.12652496)

    def test_rho_w_g_s2f_j(self):
        self.assertEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._rho_w_g_s2f_j, None)
        self.assertEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._rho_w_g_s2f_j, 0.077)

    def test_tau_w_g_j(self):
        # (0.6944444 - (1 - 0.1402048) * 0.4186988) / (1 - 0.4186988)
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN).tau_w_g_j, 0.57534585)
        # (0.6944444 - (1 - 0.12652496) * 0.3167365) / ((1 - 0.3167365) - 0.077 * 0.3167365)
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN).tau_w_g_j, 0.63408559)

    def test_tau_w_g_s1_j(self):
        # 0.57534585
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._tau_w_g_s1_j, 0.57534585)
        # (0.379 * 0.077 * 0.63408559 + ((0.379 * 0.077 * 0.63408559)**2 - 4 * (0.379 * 0.077 - 1) * 0.63408559)**0.5) / 2
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._tau_w_g_s1_j, 0.79389655)

    def test_tau_w_g_s2_j(self):
        # 定義なし
        self.assertEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._tau_w_g_s2_j, None)
        # 0.79389655
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._tau_w_g_s2_j, 0.79389655)

    def test_rho_w_g_s1b_j(self):
        # 定義なし
        self.assertEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._rho_w_g_s1b_j, None)
        # 0.379 * (1 - 0.79389655)
        self.assertAlmostEqual(Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)._rho_w_g_s1b_j, 0.07811320)

    def test_get_rho_n_function(self):
        self.assertAlmostEqual(Window._get_rho_n_phi(phi=radians(0.0)), 0.0)
        self.assertAlmostEqual(Window._get_rho_n_phi(phi=radians(30.0)), 0.00292295)
        self.assertAlmostEqual(Window._get_rho_n_phi(phi=radians(60.0)), 0.06190624)
        self.assertAlmostEqual(Window._get_rho_n_phi(phi=radians(90.0)), 1.0)

    def test_get_tau_n_function(self):
        self.assertAlmostEqual(Window._get_tau_n_phi(phi=radians(0.0)), 0.999)
        self.assertAlmostEqual(Window._get_tau_n_phi(phi=radians(30.0)), 0.98911757)
        self.assertAlmostEqual(Window._get_tau_n_phi(phi=radians(60.0)), 0.88375)
        self.assertAlmostEqual(Window._get_tau_n_phi(phi=radians(90.0)), 0.0)

    def test_get_rho_w_g_s2f_j_phi_function(self):
        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.077 + (1.0 - 0.077) * 0.0
        self.assertAlmostEqual(w_m._get_rho_w_g_s2f_j_phi(phi=radians(0.0)), 0.077)
        # 0.077 + (1.0 - 0.077) * 0.00292295
        self.assertAlmostEqual(w_m._get_rho_w_g_s2f_j_phi(phi=radians(30.0)), 0.07969788)
        # 0.077 + (1.0 - 0.077) * 0.06190624
        self.assertAlmostEqual(w_m._get_rho_w_g_s2f_j_phi(phi=radians(60.0)), 0.13413946)
        # 0.077 + (1.0 - 0.077) * 1.0
        self.assertAlmostEqual(w_m._get_rho_w_g_s2f_j_phi(phi=radians(90.0)), 1.0)

    def test_get_rho_w_g_s1b_j_phi_function(self):
        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.07811320 + (1.0 - 0.07811320) * 0.0
        self.assertAlmostEqual(w_m._get_rho_w_g_s1b_j_phi(phi=radians(0.0)), 0.0781132)
        # 0.07811320 + (1.0 - 0.07811320) * 0.00292295
        self.assertAlmostEqual(w_m._get_rho_w_g_s1b_j_phi(phi=radians(30.0)), 0.08080783)
        # 0.07811320 + (1.0 - 0.07811320) * 0.06190624
        self.assertAlmostEqual(w_m._get_rho_w_g_s1b_j_phi(phi=radians(60.0)), 0.13518375)
        # 0.07811320 + (1.0 - 0.07811320) * 1.0
        self.assertAlmostEqual(w_m._get_rho_w_g_s1b_j_phi(phi=radians(90.0)), 1.0)

    def test_get_rho_w_g_s1f_j_phi_function(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.1402048 + (1.0 - 0.1402048) * 0.0
        self.assertAlmostEqual(w_s._get_rho_w_g_s1f_j_phi(phi=radians(0.0)), 0.1402048)
        # 0.1402048 + (1.0 - 0.1402048) * 0.00292295
        self.assertAlmostEqual(w_s._get_rho_w_g_s1f_j_phi(phi=radians(30.0)), 0.14271797)
        # 0.1402048 + (1.0 - 0.1402048) * 0.06190624
        self.assertAlmostEqual(w_s._get_rho_w_g_s1f_j_phi(phi=radians(60.0)), 0.19343152)
        # 0.1402048 + (1.0 - 0.1402048) * 1.0
        self.assertAlmostEqual(w_s._get_rho_w_g_s1f_j_phi(phi=radians(90.0)), 0.99999999)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.12652496 + (1.0 - 0.12652496) * 0.0
        self.assertAlmostEqual(w_m._get_rho_w_g_s1f_j_phi(phi=radians(0.0)), 0.12652496)
        # 0.12652496 + (1.0 - 0.12652496) * 0.00292295
        self.assertAlmostEqual(w_m._get_rho_w_g_s1f_j_phi(phi=radians(30.0)), 0.12907808)
        # 0.12652496 + (1.0 - 0.12652496) * 0.06190624
        self.assertAlmostEqual(w_m._get_rho_w_g_s1f_j_phi(phi=radians(60.0)), 0.18059852)
        # 0.12652496 + (1.0 - 0.12652496) * 1.0
        self.assertAlmostEqual(w_m._get_rho_w_g_s1f_j_phi(phi=radians(90.0)), 0.99999999)

    def test_get_tau_w_g_s2_j_phi_function(self):
        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.79389655 * 0.999
        self.assertAlmostEqual(w_m._get_tau_w_g_s2_j_phi(phi=radians(0.0)), 0.79310266)
        # 0.79389655 * 0.98911757
        self.assertAlmostEqual(w_m._get_tau_w_g_s2_j_phi(phi=radians(30.0)), 0.78525703)
        # 0.79389655 * 0.88375
        self.assertAlmostEqual(w_m._get_tau_w_g_s2_j_phi(phi=radians(60.0)), 0.70160608)
        # 0.79389655 * 0.0
        self.assertAlmostEqual(w_m._get_tau_w_g_s2_j_phi(phi=radians(90.0)), 0.0)

    def test_get_tau_w_g_s1_j_phi_function(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.57534585 * 0.999
        self.assertAlmostEqual(w_s._get_tau_w_g_s1_j_phi(phi=radians(0.0)), 0.57477050)
        # 0.57534585 * 0.98911757
        self.assertAlmostEqual(w_s._get_tau_w_g_s1_j_phi(phi=radians(30.0)),0.56908469)
        # 0.57534585 * 0.88375
        self.assertAlmostEqual(w_s._get_tau_w_g_s1_j_phi(phi=radians(60.0)), 0.50846189)
        # 0.57534585 * 0.0
        self.assertAlmostEqual(w_s._get_tau_w_g_s1_j_phi(phi=radians(90.0)), 0.0)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.79389655 * 0.999
        self.assertAlmostEqual(w_m._get_tau_w_g_s1_j_phi(phi=radians(0.0)), 0.79310266)
        # 0.79389655 * 0.98911757
        self.assertAlmostEqual(w_m._get_tau_w_g_s1_j_phi(phi=radians(30.0)), 0.78525703)
        # 0.79389655 * 0.88375
        self.assertAlmostEqual(w_m._get_tau_w_g_s1_j_phi(phi=radians(60.0)), 0.70160608)
        # 0.79389655 * 0.0
        self.assertAlmostEqual(w_m._get_tau_w_g_s1_j_phi(phi=radians(90.0)), 0.0)

    def test_get_rho_w_g_j_phi_function(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.0
        self.assertAlmostEqual(w_s._get_rho_w_g_j_phi(phi=radians(0.0)), 0.1402048)
        # 0.14271797
        self.assertAlmostEqual(w_s._get_rho_w_g_j_phi(phi=radians(30.0)), 0.14271797)
        # 0.19343152
        self.assertAlmostEqual(w_s._get_rho_w_g_j_phi(phi=radians(60.0)), 0.19343152)
        #  0.99999999
        self.assertAlmostEqual(w_s._get_rho_w_g_j_phi(phi=radians(90.0)), 0.99999999)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.12652496 + 0.79310266 * 0.79310266 * 0.077 / (1 - 0.0781132 * 0.077)
        self.assertAlmostEqual(w_m._get_rho_w_g_j_phi(phi=radians(0.0)), 0.17525195)
        # 0.12907808 + 0.78525703 * 0.78525703 * 0.07969788 / (1 - 0.08080783 * 0.07969788)
        self.assertAlmostEqual(w_m._get_rho_w_g_j_phi(phi=radians(30.0)), 0.17854063)
        # 0.18059852 + 0.70160608 * 0.70160608 * 0.13413946 / (1 - 0.13518375 * 0.13413946)
        self.assertAlmostEqual(w_m._get_rho_w_g_j_phi(phi=radians(60.0)), 0.24784829)
        # 0.99999999 + 0.0 * 0.0 * 1.0 / (1 - 1.0 * 1.0)
        self.assertAlmostEqual(w_m._get_rho_w_g_j_phi(phi=radians(90.0)), 0.99999999)

    def test_get_tau_w_g_j_phi_function(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.57477050
        self.assertAlmostEqual(w_s._get_tau_w_g_j_phi(phi=radians(0.0)), 0.57477050)
        # 0.56908469
        self.assertAlmostEqual(w_s._get_tau_w_g_j_phi(phi=radians(30.0)), 0.56908469)
        # 0.50846189
        self.assertAlmostEqual(w_s._get_tau_w_g_j_phi(phi=radians(60.0)), 0.50846189)
        # 0.0
        self.assertAlmostEqual(w_s._get_tau_w_g_j_phi(phi=radians(90.0)), 0.0)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.79310266 * 0.79310266 / (1 - 0.0781132 * 0.077)
        self.assertAlmostEqual(w_m._get_tau_w_g_j_phi(phi=radians(0.0)), 0.63281805)
        # 0.78525703 * 0.78525703 / (1 - 0.08080783 * 0.07969788)
        self.assertAlmostEqual(w_m._get_tau_w_g_j_phi(phi=radians(30.0)), 0.62062557)
        # 0.70160608 * 0.70160608 / (1 - 0.13518375 * 0.13413946)
        self.assertAlmostEqual(w_m._get_tau_w_g_j_phi(phi=radians(60.0)), 0.50134217)
        # 0.0 * 0.0 / (1 - 1.0 * 1.0)
        self.assertAlmostEqual(w_m._get_tau_w_g_j_phi(phi=radians(90.0)), 0.0)

    def test_get_eta_w_g_j_phi_function(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.41869881
        self.assertAlmostEqual(w_s._r_r_w_g_j, 0.41869881)
        # 0.57477050 + (1 - 0.57477050 - 0.1402048) * 0.41869881
        self.assertAlmostEqual(w_s._get_eta_w_g_j_phi(phi=radians(0.0)), 0.69410999)
        # 0.56908469 + (1 - 0.56908469 - 0.14271797) * 0.41869881
        self.assertAlmostEqual(w_s._get_eta_w_g_j_phi(phi=radians(30.0)), 0.68975257)
        # 0.50846189 + (1 - 0.50846189 - 0.19343152) * 0.41869881
        self.assertAlmostEqual(w_s._get_eta_w_g_j_phi(phi=radians(60.0)), 0.63327876)
        # 0.0 + (1 - 0.0 - 0.99999999) * 0.41869881
        self.assertAlmostEqual(w_s._get_eta_w_g_j_phi(phi=radians(90.0)), 0.0)
        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.31673653
        self.assertAlmostEqual(w_m._r_r_w_g_j, 0.31673653)
        # 0.63281805 + (1 - 0.63281805 - 0.17525195) * 0.31673653
        self.assertAlmostEqual(w_m._get_eta_w_g_j_phi(phi=radians(0.0)), 0.69360929)
        # 0.62062557 + (1 - 0.62062557 - 0.17854063) * 0.31673653
        self.assertAlmostEqual(w_m._get_eta_w_g_j_phi(phi=radians(30.0)), 0.68423697)
        # 0.50134217 + (1 - 0.50134217 - 0.24784829) * 0.31673653
        self.assertAlmostEqual(w_m._get_eta_w_g_j_phi(phi=radians(60.0)), 0.58078271)
        # 0.0 + (1 - 0.0 - 0.99999999) * 0.31673653
        self.assertAlmostEqual(w_m._get_eta_w_g_j_phi(phi=radians(90.0)), 0.0)

    def test_get_tau_w_j_phi_function(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.57477050 * 0.72
        self.assertAlmostEqual(w_s._get_tau_w_j_phi(phi=radians(0.0)), 0.41383476)
        # 0.56908469 * 0.72
        self.assertAlmostEqual(w_s._get_tau_w_j_phi(phi=radians(30.0)), 0.40974097)
        # 0.50846189 * 0.72
        self.assertAlmostEqual(w_s._get_tau_w_j_phi(phi=radians(60.0)), 0.36609256)
        # 0.0 * 0.72
        self.assertAlmostEqual(w_s._get_tau_w_j_phi(phi=radians(90.0)), 0.0)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.63281805 * 0.72
        self.assertAlmostEqual(w_m._get_tau_w_j_phi(phi=radians(0.0)), 0.45562899)
        # 0.62062557 * 0.72
        self.assertAlmostEqual(w_m._get_tau_w_j_phi(phi=radians(30.0)), 0.44685041)
        # 0.50134217 * 0.72
        self.assertAlmostEqual(w_m._get_tau_w_j_phi(phi=radians(60.0)), 0.36096636)
        # 0.0 * 0.72
        self.assertAlmostEqual(w_m._get_tau_w_j_phi(phi=radians(90.0)), 0.0)

    def test_get_eta_w_j_phi_function(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.69410999 * 0.72
        self.assertAlmostEqual(w_s._get_eta_w_j_phi(phi=radians(0.0)), 0.49975919)
        # 0.68975257 * 0.72
        self.assertAlmostEqual(w_s._get_eta_w_j_phi(phi=radians(30.0)), 0.49662185)
        # 0.63327876 * 0.72
        self.assertAlmostEqual(w_s._get_eta_w_j_phi(phi=radians(60.0)), 0.45596071)
        # 0.0 * 0.72
        self.assertAlmostEqual(w_s._get_eta_w_j_phi(phi=radians(90.0)), 0.0)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.69360929 * 0.72
        self.assertAlmostEqual(w_m._get_eta_w_j_phi(phi=radians(0.0)), 0.49939869)
        # 0.68423697 * 0.72
        self.assertAlmostEqual(w_m._get_eta_w_j_phi(phi=radians(30.0)), 0.49265062)
        # 0.58078271 * 0.72
        self.assertAlmostEqual(w_m._get_eta_w_j_phi(phi=radians(60.0)), 0.41816355)
        # 0.0 * 0.72
        self.assertAlmostEqual(w_m._get_eta_w_j_phi(phi=radians(90.0)), 0.0)

    def test_get_tau_w_r_j(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        self.assertAlmostEqual(w_s.tau_w_r_j, 0.37151832)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        self.assertAlmostEqual(w_m.tau_w_r_j, 0.38164899)

    def test_get_tau_w_s_j(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        self.assertAlmostEqual(w_s.tau_w_s_j, 0.37151832)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        self.assertAlmostEqual(w_m.tau_w_s_j, 0.38164899)

    def test_get_eta_w_r_j(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        self.assertAlmostEqual(w_s.eta_w_r_j, 0.45936447)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        self.assertAlmostEqual(w_m.eta_w_r_j, 0.43478278)

    def test_get_eta_w_s_j(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        self.assertAlmostEqual(w_s.eta_w_s_j, 0.45936447)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        self.assertAlmostEqual(w_m.eta_w_s_j, 0.43478278)

    def test_get_tau_w_j_n_function(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.57477050 * 0.72
        self.assertAlmostEqual(w_s.get_tau_w_j_n(phi_n=radians(0.0)), 0.41383476)
        # 0.56908469 * 0.72
        self.assertAlmostEqual(w_s.get_tau_w_j_n(phi_n=radians(30.0)), 0.40974097)
        # 0.50846189 * 0.72
        self.assertAlmostEqual(w_s.get_tau_w_j_n(phi_n=radians(60.0)), 0.36609256)
        # 0.0 * 0.72
        self.assertAlmostEqual(w_s.get_tau_w_j_n(phi_n=radians(90.0)), 0.0)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.63281805 * 0.72
        self.assertAlmostEqual(w_m.get_tau_w_j_n(phi_n=radians(0.0)), 0.45562899)
        # 0.62062557 * 0.72
        self.assertAlmostEqual(w_m.get_tau_w_j_n(phi_n=radians(30.0)), 0.44685041)
        # 0.50134217 * 0.72
        self.assertAlmostEqual(w_m.get_tau_w_j_n(phi_n=radians(60.0)), 0.36096636)
        # 0.0 * 0.72
        self.assertAlmostEqual(w_m.get_tau_w_j_n(phi_n=radians(90.0)), 0.0)

    def test_get_eta_w_j_n_function(self):

        w_s = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.SINGLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.69410999 * 0.72
        self.assertAlmostEqual(w_s.get_eta_w_j_n(phi_n=radians(0.0)), 0.49975919)
        # 0.68975257 * 0.72
        self.assertAlmostEqual(w_s.get_eta_w_j_n(phi_n=radians(30.0)), 0.49662185)
        # 0.63327876 * 0.72
        self.assertAlmostEqual(w_s.get_eta_w_j_n(phi_n=radians(60.0)), 0.45596071)
        # 0.0 * 0.72
        self.assertAlmostEqual(w_s.get_eta_w_j_n(phi_n=radians(90.0)), 0.0)

        w_m = Window(u_w_j=3.0, eta_w_j=0.5, glass_type=Window.GlassType.MULTIPLE, r_a_w_g_j=0.72, flame_type=Window.FlameType.RESIN)
        # 0.69360929 * 0.72
        self.assertAlmostEqual(w_m.get_eta_w_j_n(phi_n=radians(0.0)), 0.49939869)
        # 0.68423697 * 0.72
        self.assertAlmostEqual(w_m.get_eta_w_j_n(phi_n=radians(30.0)), 0.49265062)
        # 0.58078271 * 0.72
        self.assertAlmostEqual(w_m.get_eta_w_j_n(phi_n=radians(60.0)), 0.41816355)
        # 0.0 * 0.72
        self.assertAlmostEqual(w_m.get_eta_w_j_n(phi_n=radians(90.0)), 0.0)
