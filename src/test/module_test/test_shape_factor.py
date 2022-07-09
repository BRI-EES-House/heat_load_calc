import unittest
import numpy as np

from heat_load_calc import shape_factor as sf


class TestShapeFactor(unittest.TestCase):

    def test_hr_case0(self):
        """
        永田先生の放射伝熱計算のテスト
        面積比率を与え、放射熱伝達率の計算結果をテストする
        """

        # 面積（北外壁、東外壁、南外壁、西外壁、床、天井
        surf_area = np.array([[20.0], [15.0], [20.0], [15.0], [30.0], [30.0]])

        # 放射熱伝達率を計算
        hr_js = sf._calc_h_s_r_i_js(a_s_i_js=surf_area)

        # 北外壁の放射熱伝達率
        self.assertAlmostEqual(5.92104643, hr_js[0][0])

        # 東外壁の放射熱伝達率
        self.assertAlmostEqual(5.67616719, hr_js[1][0])

        # 南外壁の放射熱伝達率
        self.assertAlmostEqual(5.92104643, hr_js[2][0])

        # 西外壁の放射熱伝達率
        self.assertAlmostEqual(5.67616719, hr_js[3][0])

        # 床の放射熱伝達率
        self.assertAlmostEqual(6.63019048, hr_js[4][0])

        # 天井の放射熱伝達率
        self.assertAlmostEqual(6.63019048, hr_js[5][0])

    def test_hr_case1(self):
        """
        永田先生の放射伝熱計算のテスト
        面積比率を与え、放射熱伝達率の計算結果をテストする
        """

        # 面積（北外壁、東外壁、南外壁、西外壁、床、天井
        surf_area = np.array([[0.0], [15.0], [20.0], [15.0], [30.0], [30.0]])

        # 放射熱伝達率を計算
        hr_js = sf._calc_h_s_r_i_js(a_s_i_js=surf_area)

        # 北外壁の放射熱伝達率
        self.assertAlmostEqual(5.14227449, hr_js[0][0])

        # 東外壁の放射熱伝達率
        self.assertAlmostEqual(5.75676599, hr_js[1][0])

        # 南外壁の放射熱伝達率
        self.assertAlmostEqual(6.05447714, hr_js[2][0])

        # 西外壁の放射熱伝達率
        self.assertAlmostEqual(5.75676599, hr_js[3][0])

        # 床の放射熱伝達率
        self.assertAlmostEqual(7.02424180, hr_js[4][0])

        # 天井の放射熱伝達率
        self.assertAlmostEqual(7.02424180, hr_js[5][0])

    def test_hr_case2(self):
        """
        永田先生の放射伝熱計算のテスト
        面積比率を与え、放射熱伝達率の計算結果をテストする
        """

        # 面積（北外壁、東外壁、南外壁、西外壁、床、天井
        surf_area = np.array([[0.0], [0.0], [0.0], [0.0], [0.0], [30.0]])

        # 放射熱伝達率を計算
        hr_js = sf._calc_h_s_r_i_js(a_s_i_js=surf_area)

        # 北外壁の放射熱伝達率
        self.assertAlmostEqual(5.14227449, hr_js[0][0])

        # 東外壁の放射熱伝達率
        self.assertAlmostEqual(5.14227449, hr_js[1][0])

        # 南外壁の放射熱伝達率
        self.assertAlmostEqual(5.14227449, hr_js[2][0])

        # 西外壁の放射熱伝達率
        self.assertAlmostEqual(5.14227449, hr_js[3][0])

        # 床の放射熱伝達率
        self.assertAlmostEqual(5.14227449, hr_js[4][0])

        # 天井の放射熱伝達率
        self.assertAlmostEqual(51.4227449, hr_js[5][0])

    def test_get_h_r_is(self):

        h_s_r_js = sf.get_h_s_r_js(
            id_rm_is=np.array([[0], [1]]),
            a_s_js=np.array([20.0, 0.0, 15.0, 15.0, 20.0, 20.0, 15.0, 15.0, 30.0, 30.0, 30.0, 30.0]).reshape(-1, 1),
            connected_room_id_js=np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]).reshape(-1, 1)
        )

        self.assertAlmostEqual(5.92104643, h_s_r_js[0][0])
        self.assertAlmostEqual(5.14227449, h_s_r_js[1][0])
        self.assertAlmostEqual(5.67616719, h_s_r_js[2][0])
        self.assertAlmostEqual(5.75676599, h_s_r_js[3][0])
        self.assertAlmostEqual(5.92104643, h_s_r_js[4][0])
        self.assertAlmostEqual(6.05447714, h_s_r_js[5][0])
        self.assertAlmostEqual(5.67616719, h_s_r_js[6][0])
        self.assertAlmostEqual(5.75676599, h_s_r_js[7][0])
        self.assertAlmostEqual(6.63019048, h_s_r_js[8][0])
        self.assertAlmostEqual(7.02424180, h_s_r_js[9][0])
        self.assertAlmostEqual(6.63019048, h_s_r_js[10][0])
        self.assertAlmostEqual(7.02424180, h_s_r_js[11][0])

    def test_get_f_mrt_is_js(self):

        f_mrt_is_js = sf.get_f_mrt_is_js(
            a_s_js=np.array([20.0, 0.0, 15.0, 15.0, 20.0, 20.0, 15.0, 15.0, 30.0, 30.0, 30.0, 30.0]).reshape(-1, 1),
            h_s_r_js=np.array(
                [
                    5.92104643, 5.14227449, 5.67616719, 5.75676599, 5.92104643, 6.05447714,
                    5.67616719, 5.75676599, 6.63019048, 7.02424180, 6.63019048, 7.02424180
                ]
            ).reshape(-1, 1),
            p_is_js=np.array(
                [
                    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
                    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
                ]
            )
        )

        self.assertAlmostEqual(f_mrt_is_js[0, 0], 0.147118019)
        self.assertAlmostEqual(f_mrt_is_js[0, 1], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[0, 2], 0.105775198)
        self.assertAlmostEqual(f_mrt_is_js[0, 3], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[0, 4], 0.147118019)
        self.assertAlmostEqual(f_mrt_is_js[0, 5], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[0, 6], 0.105775198)
        self.assertAlmostEqual(f_mrt_is_js[0, 7], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[0, 8], 0.247106783)
        self.assertAlmostEqual(f_mrt_is_js[0, 9], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[0, 10], 0.247106783)
        self.assertAlmostEqual(f_mrt_is_js[0, 11], 0.0)

        self.assertAlmostEqual(f_mrt_is_js[1, 0], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[1, 1], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[1, 2], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[1, 3], 0.120729603)
        self.assertAlmostEqual(f_mrt_is_js[1, 4], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[1, 5], 0.169297512)
        self.assertAlmostEqual(f_mrt_is_js[1, 6], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[1, 7], 0.120729603)
        self.assertAlmostEqual(f_mrt_is_js[1, 8], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[1, 9], 0.294621641)
        self.assertAlmostEqual(f_mrt_is_js[1, 10], 0.0)
        self.assertAlmostEqual(f_mrt_is_js[1, 11], 0.294621641)


if __name__ == '__main__':
    unittest.main()
