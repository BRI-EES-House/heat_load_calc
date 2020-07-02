import unittest
import os

from heat_load_calc.core import core


# クラスの名前は何でも良いので、　TestSurfaceHeatBalance のような形で名前を変更してください。
class MyTestCase(unittest.TestCase):

    # 関数の名前も何でも良いので、 test_xxxxx(self): の形で適当に変更してください。
    # ↓ このテストは時間がかかるので、skip して他のテストをサクッとまわしたいときは、次の行をアクティブにする。
    # @unittest.skip('時間がかかるのでとりあえずskip')
    def test_something1(self):

        data_dir = str(os.path.dirname(__file__)) + '/data'

        ds, dd = core.calc(input_data_dir=data_dir)

        # 1/1 0:00の外気温度があっているかどうか？
        self.assertEqual(2.3, dd['外気温度[℃]']['1989-01-01 00:00:00'])

        # 1/1 0:15の外気温度があっているかどうか？
        self.assertEqual(2.375, dd['外気温度[℃]']['1989-01-01 00:15:00'])

        # 1/1 0:00の絶対湿度があっているかどうか？
        self.assertEqual(0.0032, dd['外気絶対湿度[kg/kg(DA)]']['1989-01-01 00:00:00'])


if __name__ == '__main__':

    unittest.main()
