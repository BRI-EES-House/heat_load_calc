import unittest
import model_house as mh


class TestModelHouseFunctions(unittest.TestCase):

    def test_get_base_entrance(self):
        """
        玄関の土間床等の面積・長さに関するテスト
        """

        a_ef, a_f, l_outside, l_000, l_090, l_180, l_270, l_inside = mh.get_entrance('detached', 'floor', 1.365, 1.82)
        l_000, l_090, l_180, l_270 = l_outside

        self.assertEqual(1.365 * 1.82, a_ef)
        self.assertEqual(0.0, a_f)
        self.assertEqual(0.0, l_000)
        self.assertEqual(1.82, l_090)
        self.assertEqual(1.365, l_180)
        self.assertEqual(0.0, l_270)
        self.assertEqual(1.365 + 1.82, l_inside)

        a_ef, a_f, l_outside, l_000, l_090, l_180, l_270, l_inside = mh.get_entrance('detached', 'base', 1.365, 1.82)
        l_000, l_090, l_180, l_270 = l_outside

        self.assertEqual(1.365 * 1.82, a_ef)
        self.assertEqual(0.0, a_f)
        self.assertEqual(0.0, l_000)
        self.assertEqual(1.82, l_090)
        self.assertEqual(1.365, l_180)
        self.assertEqual(0.0, l_270)
        self.assertEqual(0.0, l_inside)

        a_ef, a_f, l_outside, l_000, l_090, l_180, l_270, l_inside = mh.get_entrance('attached', None, 1.365, 1.82)
        l_000, l_090, l_180, l_270 = l_outside

        self.assertEqual(0.0, a_ef)
        self.assertEqual(1.365 * 1.82, a_f)
        self.assertEqual(0.0, l_000)
        self.assertEqual(0.0, l_090)
        self.assertEqual(0.0, l_180)
        self.assertEqual(0.0, l_270)
        self.assertEqual(0.0, l_inside)

    def test_get_base_bath(self):
        """
        浴室の土間床等の面積・長さに関するテスト
        """

        a_ef, a_f, l_000, l_090, l_180, l_270, l_inside = mh.get_bath('detached', 'floor', 'base', 1.82, 1.82)

        self.assertEqual(1.82 * 1.82, a_ef)
        self.assertEqual(0.0, a_f)
        self.assertEqual(0.0, l_000)
        self.assertEqual(1.82, l_090)
        self.assertEqual(1.82, l_180)
        self.assertEqual(0.0, l_270)
        self.assertEqual(1.82 + 1.82, l_inside)

        a_ef, a_f, l_000, l_090, l_180, l_270, l_inside = mh.get_bath('detached', 'floor', 'floor', 1.82, 1.82)

        self.assertEqual(0.0, a_ef)
        self.assertEqual(1.82 * 1.82, a_f)
        self.assertEqual(0.0, l_000)
        self.assertEqual(0.0, l_090)
        self.assertEqual(0.0, l_180)
        self.assertEqual(0.0, l_270)
        self.assertEqual(0.0, l_inside)

        a_ef, a_f, l_000, l_090, l_180, l_270, l_inside = mh.get_bath('detached', 'floor', 'not_exist', 1.82, 1.82)

        self.assertEqual(0.0, a_ef)
        self.assertEqual(1.82 * 1.82, a_f)
        self.assertEqual(0.0, l_000)
        self.assertEqual(0.0, l_090)
        self.assertEqual(0.0, l_180)
        self.assertEqual(0.0, l_270)
        self.assertEqual(0.0, l_inside)

        a_ef, a_f, l_000, l_090, l_180, l_270, l_inside = mh.get_bath('detached', 'base', None, 1.82, 1.82)

        self.assertEqual(1.82 * 1.82, a_ef)
        self.assertEqual(0.0, a_f)
        self.assertEqual(0.0, l_000)
        self.assertEqual(1.82, l_090)
        self.assertEqual(1.82, l_180)
        self.assertEqual(0.0, l_270)
        self.assertEqual(0.0, l_inside)

        a_ef, a_f, l_000, l_090, l_180, l_270, l_inside = mh.get_bath('attached', None, None, 1.82, 1.82)

        self.assertEqual(0.0, a_ef)
        self.assertEqual(1.82 * 1.82, a_f)
        self.assertEqual(0.0, l_000)
        self.assertEqual(0.0, l_090)
        self.assertEqual(0.0, l_180)
        self.assertEqual(0.0, l_270)
        self.assertEqual(0.0, l_inside)


class TestModeHouseResults(unittest.TestCase):

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
            house_type='attached', a_f_total=90.0, r_open=0.14)

    def test_a_f(self):

        self.assertAlmostEqual(self.dfb.a_f[0], 50.85, delta=0.01)
        self.assertAlmostEqual(self.dfb.a_f[1], 39.15, delta=0.01)
        self.assertAlmostEqual(self.dff.a_f[0], 50.85, delta=0.01)
        self.assertAlmostEqual(self.dff.a_f[1], 39.15, delta=0.01)
        self.assertAlmostEqual(self.dfn.a_f[0], 50.85, delta=0.01)
        self.assertAlmostEqual(self.dfn.a_f[1], 39.15, delta=0.01)
        self.assertAlmostEqual(self.db.a_f[0], 50.85, delta=0.01)
        self.assertAlmostEqual(self.db.a_f[1], 39.15, delta=0.01)
        self.assertAlmostEqual(self.a.a_f[0], 90.0, delta=0.01)


if __name__ == '__main__':
    unittest.main()