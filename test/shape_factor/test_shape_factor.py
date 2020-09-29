import unittest
import numpy as np

from heat_load_calc.core import shape_factor as sf


class TestWeatherData15m(unittest.TestCase):

    def test_hr(self):

        '''
        永田先生の放射伝熱計算のテスト
        面積比率を与え、放射熱伝達率の計算結果をテストする
        '''

        print('\n testing shape factor by Nagata')

        # 面積（北外壁、東外壁、南外壁、西外壁、床、天井
        surf_area = np.array([[20.0], [15.0], [20.0], [15.0], [30.0], [30.0]])

        # 空間と境界の関係（今回は6つの境界がすべて空間に属するとする）
        p_js_is = np.array([[1], [1], [1], [1], [1], [1]])

        # 放射熱伝達率を計算
        hr_js = sf.get_h_r_js(a_srf_js=surf_area, p_js_is=p_js_is)

        # 北外壁の放射熱伝達率
        self.assertAlmostEqual(5.92104643, hr_js[0][0])

        # 東外壁の放射熱伝達率
        self.assertAlmostEqual(5.67616719, hr_js[1][0])

        # 床の放射熱伝達率
        self.assertAlmostEqual(6.63019048, hr_js[4][0])


if __name__ == '__main__':
    unittest.main()
