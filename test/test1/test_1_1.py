import unittest
import os

from heat_load_calc.core import core


# クラスの名前は何でも良いので、　TestSurfaceHeatBalance のような形で名前を変更してください。
class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        data_dir = str(os.path.dirname(__file__)) + '/data'

        ds, dd = core.calc(input_data_dir=data_dir)

        cls._ds = ds
        cls._dd = dd


#    @unittest.skip('時間がかかるのでとりあえずskip')
    def test_weather(self):

        ds = self._ds
        dd = self._dd

        # 1/1 0:00の外気温度があっているかどうか？
        self.assertEqual(2.3, dd['out_temp']['1989-01-01 00:00:00'])

        # 1/1 0:15の外気温度があっているかどうか？
        self.assertEqual(2.375, dd['out_temp']['1989-01-01 00:15:00'])

        # 1/1 0:00の絶対湿度があっているかどうか？
        self.assertEqual(0.0032, dd['out_abs_humid']['1989-01-01 00:00:00'])


if __name__ == '__main__':

    unittest.main()
