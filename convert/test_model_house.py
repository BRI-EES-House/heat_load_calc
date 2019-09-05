import unittest
import model_house as mh


class TestModelHouseShapeFactor(unittest.TestCase):

    def setUp(self):
        self.dfb = mh.calc_area(
            house_type='detached', a_f_total=90.0, r_open=0.14, floor_ins_type='floor', bath_ins_type='base',
            a_env_input=266.10)
        self.dff = mh.calc_area(
            house_type='detached', a_f_total=90.0, r_open=0.14, floor_ins_type='floor', bath_ins_type='floor',
            a_env_input=262.46)
        self.dfn = mh.calc_area(
            house_type='detached', a_f_total=90.0, r_open=0.14, floor_ins_type='floor', bath_ins_type='not_exist',
            a_env_input=262.46)
        self.db = mh.calc_area(
            house_type='detached', a_f_total=90.0, r_open=0.14, floor_ins_type='base', a_env_input=275.69)
        self.a = mh.calc_area(
            house_type='attached', a_f_total=70.0, r_open=0.05885, a_env_input=238.22)

    def test_f_s(self):

        self.assertAlmostEqual(self.dfb['f_s'][0], 1.08, delta=0.01)
        self.assertAlmostEqual(self.dfb['f_s'][1], 1.04, delta=0.01)
        self.assertAlmostEqual(self.dff['f_s'][0], 1.08, delta=0.01)
        self.assertAlmostEqual(self.dff['f_s'][1], 1.04, delta=0.01)
        self.assertAlmostEqual(self.dfn['f_s'][0], 1.08, delta=0.01)
        self.assertAlmostEqual(self.dfn['f_s'][1], 1.04, delta=0.01)
        self.assertAlmostEqual(self.db['f_s'][0], 1.08, delta=0.01)
        self.assertAlmostEqual(self.db['f_s'][1], 1.04, delta=0.01)
        self.assertAlmostEqual(self.a['f_s'][0], 1.05, delta=0.01)


class TestModelHouseResults(unittest.TestCase):

    def setUp(self):

        self.dfb = mh.calc_area(
            house_type='detached', a_f_total=90.0, r_open=0.14, floor_ins_type='floor', bath_ins_type='base')
        self.dff = mh.calc_area(
            house_type='detached', a_f_total=90.0, r_open=0.14, floor_ins_type='floor', bath_ins_type='floor')
        self.dfn = mh.calc_area(
            house_type='detached', a_f_total=90.0, r_open=0.14, floor_ins_type='floor', bath_ins_type='not_exist')
        self.db = mh.calc_area(
            house_type='detached', a_f_total=90.0, r_open=0.14, floor_ins_type='base')
        self.a = mh.calc_area(
            house_type='attached', a_f_total=70.0, r_open=0.05885)

    def test_a_f(self):

        self.assertAlmostEqual(self.dfb['a_f'][0], 50.85, 2)
        self.assertAlmostEqual(self.dfb['a_f'][1], 39.15, 2)
        self.assertAlmostEqual(self.dff['a_f'][0], 50.85, 2)
        self.assertAlmostEqual(self.dff['a_f'][1], 39.15, 2)
        self.assertAlmostEqual(self.dfn['a_f'][0], 50.85, 2)
        self.assertAlmostEqual(self.dfn['a_f'][1], 39.15, 2)
        self.assertAlmostEqual(self.db['a_f'][0], 50.85, 2)
        self.assertAlmostEqual(self.db['a_f'][1], 39.15, 2)
        self.assertAlmostEqual(self.a['a_f'][0], 70.0, 2)

    def test_a_evp_ef_etrc(self):

        self.assertAlmostEqual(self.dfb['a_evp_ef_etrc'], 2.48, 2)
        self.assertAlmostEqual(self.dff['a_evp_ef_etrc'], 2.48, 2)
        self.assertAlmostEqual(self.dfn['a_evp_ef_etrc'], 2.48, 2)
        self.assertAlmostEqual(self.db['a_evp_ef_etrc'], 2.48, 2)
        self.assertAlmostEqual(self.a['a_evp_ef_etrc'], 0.0, 2)

    def test_a_evp_f_etrc(self):

        self.assertAlmostEqual(self.dfb['a_evp_f_etrc'], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_f_etrc'], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_f_etrc'], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_f_etrc'], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_f_etrc'], 1.0, 2)

    def test_l_base_etrc_outside(self):

        self.assertAlmostEqual(self.dfb['l_base_etrc_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfb['l_base_etrc_outside'][1], 1.82, 2)
        self.assertAlmostEqual(self.dfb['l_base_etrc_outside'][2], 1.365, 2)
        self.assertAlmostEqual(self.dfb['l_base_etrc_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_etrc_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_etrc_outside'][1], 1.82, 2)
        self.assertAlmostEqual(self.dff['l_base_etrc_outside'][2], 1.365, 2)
        self.assertAlmostEqual(self.dff['l_base_etrc_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_etrc_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_etrc_outside'][1], 1.82, 2)
        self.assertAlmostEqual(self.dfn['l_base_etrc_outside'][2], 1.365, 2)
        self.assertAlmostEqual(self.dfn['l_base_etrc_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.db['l_base_etrc_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.db['l_base_etrc_outside'][1], 1.82, 2)
        self.assertAlmostEqual(self.db['l_base_etrc_outside'][2], 1.365, 2)
        self.assertAlmostEqual(self.db['l_base_etrc_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_etrc_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_etrc_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_etrc_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_etrc_outside'][3], 0.0, 2)

    def test_a_evp_ef_bath(self):

        self.assertAlmostEqual(self.dfb['a_evp_ef_bath'], 3.31, 2)
        self.assertAlmostEqual(self.dff['a_evp_ef_bath'], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_ef_bath'], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_ef_bath'], 3.31, 2)
        self.assertAlmostEqual(self.a['a_evp_ef_bath'], 0.0, 2)

    def test_a_evp_f_bath(self):

        self.assertAlmostEqual(self.dfb['a_evp_f_bath'], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_f_bath'], 3.31, 2)
        self.assertAlmostEqual(self.dfn['a_evp_f_bath'], 3.31, 2)
        self.assertAlmostEqual(self.db['a_evp_f_bath'], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_f_bath'], 2.87, 2)

    def test_l_base_bath_outside(self):

        self.assertAlmostEqual(self.dfb['l_base_bath_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfb['l_base_bath_outside'][1], 1.82, 2)
        self.assertAlmostEqual(self.dfb['l_base_bath_outside'][2], 1.82, 2)
        self.assertAlmostEqual(self.dfb['l_base_bath_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_bath_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_bath_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_bath_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_bath_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_bath_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_bath_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_bath_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_bath_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.db['l_base_bath_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.db['l_base_bath_outside'][1], 1.82, 2)
        self.assertAlmostEqual(self.db['l_base_bath_outside'][2], 1.82, 2)
        self.assertAlmostEqual(self.db['l_base_bath_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_bath_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_bath_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_bath_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_bath_outside'][3], 0.0, 2)

    def test_l_base_bath_inside(self):

        self.assertAlmostEqual(self.dfb['l_base_bath_inside'], 3.64, 2)
        self.assertAlmostEqual(self.dff['l_base_bath_inside'], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_bath_inside'], 0.0, 2)
        self.assertAlmostEqual(self.db['l_base_bath_inside'], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_bath_inside'], 0.0, 2)

    def test_f_s(self):

        self.assertAlmostEqual(self.dfb['f_s'][0], 1.08, 2)
        self.assertAlmostEqual(self.dfb['f_s'][1], 1.04, 2)
        self.assertAlmostEqual(self.dff['f_s'][0], 1.08, 2)
        self.assertAlmostEqual(self.dff['f_s'][1], 1.04, 2)
        self.assertAlmostEqual(self.dfn['f_s'][0], 1.08, 2)
        self.assertAlmostEqual(self.dfn['f_s'][1], 1.04, 2)
        self.assertAlmostEqual(self.db['f_s'][0], 1.08, 2)
        self.assertAlmostEqual(self.db['f_s'][1], 1.04, 2)
        self.assertAlmostEqual(self.a['f_s'][0], 1.05, 2)

    def test_l_prm(self):

        self.assertAlmostEqual(self.dfb['l_prm'][0], 30.80, 2)
        self.assertAlmostEqual(self.dfb['l_prm'][1], 26.03, 2)
        self.assertAlmostEqual(self.dff['l_prm'][0], 30.80, 2)
        self.assertAlmostEqual(self.dff['l_prm'][1], 26.03, 2)
        self.assertAlmostEqual(self.dfn['l_prm'][0], 30.80, 2)
        self.assertAlmostEqual(self.dfn['l_prm'][1], 26.03, 2)
        self.assertAlmostEqual(self.db['l_prm'][0], 30.80, 2)
        self.assertAlmostEqual(self.db['l_prm'][1], 26.03, 2)
        self.assertAlmostEqual(self.a['l_prm'][0], 35.08, 2)

    def test_l_ms(self):

        self.assertAlmostEqual(self.dfb['l_ms'][0], 10.61, 2)
        self.assertAlmostEqual(self.dfb['l_ms'][1], 8.29, 2)
        self.assertAlmostEqual(self.dff['l_ms'][0], 10.61, 2)
        self.assertAlmostEqual(self.dff['l_ms'][1], 8.29, 2)
        self.assertAlmostEqual(self.dfn['l_ms'][0], 10.61, 2)
        self.assertAlmostEqual(self.dfn['l_ms'][1], 8.29, 2)
        self.assertAlmostEqual(self.db['l_ms'][0], 10.61, 2)
        self.assertAlmostEqual(self.db['l_ms'][1], 8.29, 2)
        self.assertAlmostEqual(self.a['l_ms'][0], 6.14, 2)

    def test_l_os(self):

        self.assertAlmostEqual(self.dfb['l_os'][0], 4.79, 2)
        self.assertAlmostEqual(self.dfb['l_os'][1], 4.72, 2)
        self.assertAlmostEqual(self.dff['l_os'][0], 4.79, 2)
        self.assertAlmostEqual(self.dff['l_os'][1], 4.72, 2)
        self.assertAlmostEqual(self.dfn['l_os'][0], 4.79, 2)
        self.assertAlmostEqual(self.dfn['l_os'][1], 4.72, 2)
        self.assertAlmostEqual(self.db['l_os'][0], 4.79, 2)
        self.assertAlmostEqual(self.db['l_os'][1], 4.72, 2)
        self.assertAlmostEqual(self.a['l_os'][0], 11.4, 2)

    def test_a_evp_other(self):

        self.assertAlmostEqual(self.dfb['a_evp_ef_other'], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_ef_other'], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_ef_other'], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_ef_other'], 45.05, 2)
        self.assertAlmostEqual(self.a['a_evp_ef_other'], 0.0, 2)

    def test_a_evp_ef_total(self):

        self.assertAlmostEqual(self.dfb['a_evp_ef_total'], 5.80, 2)
        self.assertAlmostEqual(self.dff['a_evp_ef_total'], 2.48, 2)
        self.assertAlmostEqual(self.dfn['a_evp_ef_total'], 2.48, 2)
        self.assertAlmostEqual(self.db['a_evp_ef_total'], 50.85, 2)
        self.assertAlmostEqual(self.a['a_evp_ef_total'], 0.0, 2)

    def test_a_evp_f_other(self):

        self.assertAlmostEqual(self.dfb['a_evp_f_other'], 45.05, 2)
        self.assertAlmostEqual(self.dff['a_evp_f_other'], 45.05, 2)
        self.assertAlmostEqual(self.dfn['a_evp_f_other'], 45.05, 2)
        self.assertAlmostEqual(self.db['a_evp_f_other'], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_f_other'], 66.13, 2)

    def test_a_evp_f_total(self):

        self.assertAlmostEqual(self.dfb['a_evp_f_total'], 45.05, 2)
        self.assertAlmostEqual(self.dff['a_evp_f_total'], 48.36, 2)
        self.assertAlmostEqual(self.dfn['a_evp_f_total'], 48.36, 2)
        self.assertAlmostEqual(self.db['a_evp_f_total'], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_f_total'], 70.0, 2)

    def test_l_base_other_outside(self):

        self.assertAlmostEqual(self.dfb['l_base_other_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfb['l_base_other_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.dfb['l_base_other_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.dfb['l_base_other_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_other_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_other_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_other_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_other_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_other_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_other_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_other_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_other_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.db['l_base_other_outside'][0], 10.61, 2)
        self.assertAlmostEqual(self.db['l_base_other_outside'][1], 1.15, 2)
        self.assertAlmostEqual(self.db['l_base_other_outside'][2], 7.425, 2)
        self.assertAlmostEqual(self.db['l_base_other_outside'][3], 4.79, 2)
        self.assertAlmostEqual(self.a['l_base_other_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_other_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_other_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_other_outside'][3], 0.0, 2)

    def test_l_base_other_inside(self):

        self.assertAlmostEqual(self.dfb['l_base_other_inside'], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_other_inside'], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_other_inside'], 0.0, 2)
        self.assertAlmostEqual(self.db['l_base_other_inside'], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_other_inside'], 0.0, 2)

    def test_l_base_total_outside(self):

        self.assertAlmostEqual(self.dfb['l_base_total_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfb['l_base_total_outside'][1], 3.64, 2)
        self.assertAlmostEqual(self.dfb['l_base_total_outside'][2], 3.185, 2)
        self.assertAlmostEqual(self.dfb['l_base_total_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_total_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dff['l_base_total_outside'][1], 1.82, 2)
        self.assertAlmostEqual(self.dff['l_base_total_outside'][2], 1.365, 2)
        self.assertAlmostEqual(self.dff['l_base_total_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_total_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfn['l_base_total_outside'][1], 1.82, 2)
        self.assertAlmostEqual(self.dfn['l_base_total_outside'][2], 1.365, 2)
        self.assertAlmostEqual(self.dfn['l_base_total_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.db['l_base_total_outside'][0], 10.61, 2)
        self.assertAlmostEqual(self.db['l_base_total_outside'][1], 4.79, 2)
        self.assertAlmostEqual(self.db['l_base_total_outside'][2], 10.61, 2)
        self.assertAlmostEqual(self.db['l_base_total_outside'][3], 4.79, 2)
        self.assertAlmostEqual(self.a['l_base_total_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_total_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_total_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_total_outside'][3], 0.0, 2)

    def test_l_base_total_inside(self):

        self.assertAlmostEqual(self.dfb['l_base_total_inside'], 6.825, 2)
        self.assertAlmostEqual(self.dff['l_base_total_inside'], 3.185, 2)
        self.assertAlmostEqual(self.dfn['l_base_total_inside'], 3.185, 2)
        self.assertAlmostEqual(self.db['l_base_total_inside'], 0.0, 2)
        self.assertAlmostEqual(self.a['l_base_total_inside'], 0.0, 2)

    def test_a_evp_roof(self):

        self.assertAlmostEqual(self.dfb['a_evp_roof'], 50.85, 2)
        self.assertAlmostEqual(self.dff['a_evp_roof'], 50.85, 2)
        self.assertAlmostEqual(self.dfn['a_evp_roof'], 50.85, 2)
        self.assertAlmostEqual(self.db['a_evp_roof'], 50.85, 2)
        self.assertAlmostEqual(self.a['a_evp_roof'], 70.0, 2)

    def test_a_evp_base_etrc_outside(self):

        self.assertAlmostEqual(self.dfb['a_evp_base_etrc_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_etrc_outside'][1], 0.33, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_etrc_outside'][2], 0.25, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_etrc_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_etrc_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_etrc_outside'][1], 0.33, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_etrc_outside'][2], 0.25, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_etrc_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_etrc_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_etrc_outside'][1], 0.33, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_etrc_outside'][2], 0.25, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_etrc_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_base_etrc_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_base_etrc_outside'][1], 0.33, 2)
        self.assertAlmostEqual(self.db['a_evp_base_etrc_outside'][2], 0.25, 2)
        self.assertAlmostEqual(self.db['a_evp_base_etrc_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_etrc_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_etrc_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_etrc_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_etrc_outside'][3], 0.0, 2)

    def test_a_evp_base_etrc_inside(self):

        self.assertAlmostEqual(self.dfb['a_evp_base_etrc_inside'], 0.57, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_etrc_inside'], 0.57, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_etrc_inside'], 0.57, 2)
        self.assertAlmostEqual(self.db['a_evp_base_etrc_inside'], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_etrc_inside'], 0.0, 2)

    def test_a_evp_base_bath_outside(self):

        self.assertAlmostEqual(self.dfb['a_evp_base_bath_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_bath_outside'][1], 0.91, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_bath_outside'][2], 0.91, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_bath_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_bath_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_bath_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_bath_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_bath_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_bath_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_bath_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_bath_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_bath_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_base_bath_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_base_bath_outside'][1], 0.91, 2)
        self.assertAlmostEqual(self.db['a_evp_base_bath_outside'][2], 0.91, 2)
        self.assertAlmostEqual(self.db['a_evp_base_bath_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_bath_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_bath_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_bath_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_bath_outside'][3], 0.0, 2)

    def test_a_evp_base_bath_inside(self):

        self.assertAlmostEqual(self.dfb['a_evp_base_bath_inside'], 1.82, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_bath_inside'], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_bath_inside'], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_base_bath_inside'], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_bath_inside'], 0.0, 2)

    def test_a_evp_base_other_outside(self):

        self.assertAlmostEqual(self.dfb['a_evp_base_other_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_other_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_other_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_other_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_other_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_other_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_other_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_other_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_other_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_other_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_other_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_other_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_base_other_outside'][0], 5.3, 2)
        self.assertAlmostEqual(self.db['a_evp_base_other_outside'][1], 0.58, 2)
        self.assertAlmostEqual(self.db['a_evp_base_other_outside'][2], 3.71 , 2)
        self.assertAlmostEqual(self.db['a_evp_base_other_outside'][3], 2.4, 2)
        self.assertAlmostEqual(self.a['a_evp_base_other_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_other_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_other_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_other_outside'][3], 0.0, 2)

    def test_a_evp_base_other_inside(self):

        self.assertAlmostEqual(self.dfb['a_evp_base_other_inside'], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_other_inside'], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_other_inside'], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_base_other_inside'], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_other_inside'], 0.0, 2)

    def test_a_evp_base_total_outside(self):

        self.assertAlmostEqual(self.dfb['a_evp_base_total_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_total_outside'][1], 1.24, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_total_outside'][2], 1.16, 2)
        self.assertAlmostEqual(self.dfb['a_evp_base_total_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_total_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_total_outside'][1], 0.33, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_total_outside'][2], 0.25, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_total_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_total_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_total_outside'][1], 0.33, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_total_outside'][2], 0.25, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_total_outside'][3], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_base_total_outside'][0], 5.3, 2)
        self.assertAlmostEqual(self.db['a_evp_base_total_outside'][1], 1.81, 2)
        self.assertAlmostEqual(self.db['a_evp_base_total_outside'][2], 4.87, 2)
        self.assertAlmostEqual(self.db['a_evp_base_total_outside'][3], 2.4, 2)
        self.assertAlmostEqual(self.a['a_evp_base_total_outside'][0], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_total_outside'][1], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_total_outside'][2], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_total_outside'][3], 0.0, 2)

    def test_a_evp_base_total_inside(self):

        self.assertAlmostEqual(self.dfb['a_evp_base_total_inside'], 2.39, 2)
        self.assertAlmostEqual(self.dff['a_evp_base_total_inside'], 0.57, 2)
        self.assertAlmostEqual(self.dfn['a_evp_base_total_inside'], 0.57, 2)
        self.assertAlmostEqual(self.db['a_evp_base_total_inside'], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_base_total_inside'], 0.0, 2)

    def test_a_evp_srf(self):

        self.assertAlmostEqual(self.dfb['a_evp_srf'][0][0], 30.77, 2)
        self.assertAlmostEqual(self.dfb['a_evp_srf'][0][1], 22.40, 2)
        self.assertAlmostEqual(self.dfb['a_evp_srf'][1][0], 13.90, 2)
        self.assertAlmostEqual(self.dfb['a_evp_srf'][1][1], 12.74, 2)
        self.assertAlmostEqual(self.dfb['a_evp_srf'][2][0], 30.77, 2)
        self.assertAlmostEqual(self.dfb['a_evp_srf'][2][1], 22.40, 2)
        self.assertAlmostEqual(self.dfb['a_evp_srf'][3][0], 13.90, 2)
        self.assertAlmostEqual(self.dfb['a_evp_srf'][3][1], 12.74, 2)
        self.assertAlmostEqual(self.dff['a_evp_srf'][0][0], 30.77, 2)
        self.assertAlmostEqual(self.dff['a_evp_srf'][0][1], 22.40, 2)
        self.assertAlmostEqual(self.dff['a_evp_srf'][1][0], 13.90, 2)
        self.assertAlmostEqual(self.dff['a_evp_srf'][1][1], 12.74, 2)
        self.assertAlmostEqual(self.dff['a_evp_srf'][2][0], 30.77, 2)
        self.assertAlmostEqual(self.dff['a_evp_srf'][2][1], 22.40, 2)
        self.assertAlmostEqual(self.dff['a_evp_srf'][3][0], 13.90, 2)
        self.assertAlmostEqual(self.dff['a_evp_srf'][3][1], 12.74, 2)
        self.assertAlmostEqual(self.dfn['a_evp_srf'][0][0], 30.77, 2)
        self.assertAlmostEqual(self.dfn['a_evp_srf'][0][1], 22.40, 2)
        self.assertAlmostEqual(self.dfn['a_evp_srf'][1][0], 13.90, 2)
        self.assertAlmostEqual(self.dfn['a_evp_srf'][1][1], 12.74, 2)
        self.assertAlmostEqual(self.dfn['a_evp_srf'][2][0], 30.77, 2)
        self.assertAlmostEqual(self.dfn['a_evp_srf'][2][1], 22.40, 2)
        self.assertAlmostEqual(self.dfn['a_evp_srf'][3][0], 13.90, 2)
        self.assertAlmostEqual(self.dfn['a_evp_srf'][3][1], 12.74, 2)
        self.assertAlmostEqual(self.db['a_evp_srf'][0][0], 30.77, 2)
        self.assertAlmostEqual(self.db['a_evp_srf'][0][1], 22.40, 2)
        self.assertAlmostEqual(self.db['a_evp_srf'][1][0], 13.90, 2)
        self.assertAlmostEqual(self.db['a_evp_srf'][1][1], 12.74, 2)
        self.assertAlmostEqual(self.db['a_evp_srf'][2][0], 30.77, 2)
        self.assertAlmostEqual(self.db['a_evp_srf'][2][1], 22.40, 2)
        self.assertAlmostEqual(self.db['a_evp_srf'][3][0], 13.90, 2)
        self.assertAlmostEqual(self.db['a_evp_srf'][3][1], 12.74, 2)
        self.assertAlmostEqual(self.a['a_evp_srf'][0][0], 17.19, 2)
        self.assertAlmostEqual(self.a['a_evp_srf'][1][0], 31.92, 2)
        self.assertAlmostEqual(self.a['a_evp_srf'][2][0], 17.19, 2)
        self.assertAlmostEqual(self.a['a_evp_srf'][3][0], 31.92, 2)

    def test_a_evp_total_not_base(self):

        self.assertAlmostEqual(self.dfb['a_evp_total_not_base'], 261.31, 2)
        self.assertAlmostEqual(self.dff['a_evp_total_not_base'], 261.31, 2)
        self.assertAlmostEqual(self.dfn['a_evp_total_not_base'], 261.31, 2)
        self.assertAlmostEqual(self.db['a_evp_total_not_base'], 261.31, 2)
        self.assertAlmostEqual(self.a['a_evp_total_not_base'], 238.22, 2)

    def test_a_evp_total(self):

        self.assertAlmostEqual(self.dfb['a_evp_total'], 266.10, 2)
        self.assertAlmostEqual(self.dff['a_evp_total'], 262.46, 2)
        self.assertAlmostEqual(self.dfn['a_evp_total'], 262.46, 2)
        self.assertAlmostEqual(self.db['a_evp_total'], 275.69, 2)
        self.assertAlmostEqual(self.a['a_evp_total'], 238.22, 2)

    def test_a_evp_open_total(self):

        self.assertAlmostEqual(self.dfb['a_evp_open_total'], 36.58, 2)
        self.assertAlmostEqual(self.dff['a_evp_open_total'], 36.58, 2)
        self.assertAlmostEqual(self.dfn['a_evp_open_total'], 36.58, 2)
        self.assertAlmostEqual(self.db['a_evp_open_total'], 36.58, 2)
        self.assertAlmostEqual(self.a['a_evp_open_total'], 14.02, 2)

    def test_a_evp_window_total(self):

        self.assertAlmostEqual(self.dfb['a_evp_window_total'], 33.07, 2)
        self.assertAlmostEqual(self.dff['a_evp_window_total'], 33.07, 2)
        self.assertAlmostEqual(self.dfn['a_evp_window_total'], 33.07, 2)
        self.assertAlmostEqual(self.db['a_evp_window_total'], 33.07, 2)
        self.assertAlmostEqual(self.a['a_evp_window_total'], 12.26, 2)

    def test_a_evp_window(self):

        self.assertAlmostEqual(self.dfb['a_evp_window'][0], 22.69, 2)
        self.assertAlmostEqual(self.dfb['a_evp_window'][1], 2.38, 2)
        self.assertAlmostEqual(self.dfb['a_evp_window'][2], 3.63, 2)
        self.assertAlmostEqual(self.dfb['a_evp_window'][3], 4.37, 2)
        self.assertAlmostEqual(self.dff['a_evp_window'][0], 22.69, 2)
        self.assertAlmostEqual(self.dff['a_evp_window'][1], 2.38, 2)
        self.assertAlmostEqual(self.dff['a_evp_window'][2], 3.63, 2)
        self.assertAlmostEqual(self.dff['a_evp_window'][3], 4.37, 2)
        self.assertAlmostEqual(self.dfn['a_evp_window'][0], 22.69, 2)
        self.assertAlmostEqual(self.dfn['a_evp_window'][1], 2.38, 2)
        self.assertAlmostEqual(self.dfn['a_evp_window'][2], 3.63, 2)
        self.assertAlmostEqual(self.dfn['a_evp_window'][3], 4.37, 2)
        self.assertAlmostEqual(self.db['a_evp_window'][0], 22.69, 2)
        self.assertAlmostEqual(self.db['a_evp_window'][1], 2.38, 2)
        self.assertAlmostEqual(self.db['a_evp_window'][2], 3.63, 2)
        self.assertAlmostEqual(self.db['a_evp_window'][3], 4.37, 2)
        self.assertAlmostEqual(self.a['a_evp_window'][0], 7.76, 2)
        self.assertAlmostEqual(self.a['a_evp_window'][1], 1.86, 2)
        self.assertAlmostEqual(self.a['a_evp_window'][2], 2.64, 2)
        self.assertAlmostEqual(self.a['a_evp_window'][3], 0.0, 2)

    def test_a_evp_door_total(self):

        self.assertAlmostEqual(self.dfb['a_evp_door'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfb['a_evp_door'][1], 1.89, 2)
        self.assertAlmostEqual(self.dfb['a_evp_door'][2], 1.62, 2)
        self.assertAlmostEqual(self.dfb['a_evp_door'][3], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_door'][0], 0.0, 2)
        self.assertAlmostEqual(self.dff['a_evp_door'][1], 1.89, 2)
        self.assertAlmostEqual(self.dff['a_evp_door'][2], 1.62, 2)
        self.assertAlmostEqual(self.dff['a_evp_door'][3], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_door'][0], 0.0, 2)
        self.assertAlmostEqual(self.dfn['a_evp_door'][1], 1.89, 2)
        self.assertAlmostEqual(self.dfn['a_evp_door'][2], 1.62, 2)
        self.assertAlmostEqual(self.dfn['a_evp_door'][3], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_door'][0], 0.0, 2)
        self.assertAlmostEqual(self.db['a_evp_door'][1], 1.89, 2)
        self.assertAlmostEqual(self.db['a_evp_door'][2], 1.62, 2)
        self.assertAlmostEqual(self.db['a_evp_door'][3], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_door'][0], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_door'][1], 0.0, 2)
        self.assertAlmostEqual(self.a['a_evp_door'][2], 1.755, 2)
        self.assertAlmostEqual(self.a['a_evp_door'][3], 0.0, 2)

    def test_a_evp_wall(self):

        self.assertAlmostEqual(self.dfb['a_evp_wall'][0], 30.47, 2)
        self.assertAlmostEqual(self.dfb['a_evp_wall'][1], 22.37, 2)
        self.assertAlmostEqual(self.dfb['a_evp_wall'][2], 47.92, 2)
        self.assertAlmostEqual(self.dfb['a_evp_wall'][3], 22.28, 2)
        self.assertAlmostEqual(self.dff['a_evp_wall'][0], 30.47, 2)
        self.assertAlmostEqual(self.dff['a_evp_wall'][1], 22.37, 2)
        self.assertAlmostEqual(self.dff['a_evp_wall'][2], 47.92, 2)
        self.assertAlmostEqual(self.dff['a_evp_wall'][3], 22.28, 2)
        self.assertAlmostEqual(self.dfn['a_evp_wall'][0], 30.47, 2)
        self.assertAlmostEqual(self.dfn['a_evp_wall'][1], 22.37, 2)
        self.assertAlmostEqual(self.dfn['a_evp_wall'][2], 47.92, 2)
        self.assertAlmostEqual(self.dfn['a_evp_wall'][3], 22.28, 2)
        self.assertAlmostEqual(self.db['a_evp_wall'][0], 30.47, 2)
        self.assertAlmostEqual(self.db['a_evp_wall'][1], 22.37, 2)
        self.assertAlmostEqual(self.db['a_evp_wall'][2], 47.92, 2)
        self.assertAlmostEqual(self.db['a_evp_wall'][3], 22.28, 2)
        self.assertAlmostEqual(self.a['a_evp_wall'][0], 9.43, 2)
        self.assertAlmostEqual(self.a['a_evp_wall'][1], 30.06, 2)
        self.assertAlmostEqual(self.a['a_evp_wall'][2], 12.80, 2)
        self.assertAlmostEqual(self.a['a_evp_wall'][3], 31.92, 2)


if __name__ == '__main__':
    unittest.main()
