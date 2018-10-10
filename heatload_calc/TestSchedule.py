import matplotlib
from matplotlib.testing.decorators import image_comparison
import math
import datetime
import unittest
import nbimporter
import Schedule as nb

class TestSchedule(unittest.TestCase):

    #空調設定温湿度の取得
    def test_Appl(self):
        sc = nb.Schedule()
        self.assertEqual(27.0, sc.ACSet('主たる居室','', '温度', datetime.datetime.strptime('2017/06/01 12:06', '%Y/%m/%d %H:%M')))
    
    #機器発熱スケジュールの取得
    def test_Appl(self):
        sc = nb.Schedule()
        self.assertEqual(0.0, sc.Appl('主たる居室', '', '顕熱', datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')))

    #照明発熱スケジュールの取得
    def test_Light(self):
        sc = nb.Schedule()
        self.assertEqual(0.0, sc.Light('主たる居室', '', datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')))

    #局所換気スケジュールの取得
    def test_LocalVent(self):
        sc = nb.Schedule()
        self.assertEqual(0.0, sc.LocalVent('主たる居室', '', datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')))

    #在室人員スケジュールの取得
    def test_Nresi(self):
        sc = nb.Schedule()
        self.assertEqual(0.0, sc.Nresi('主たる居室', '', datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')))

    #datetime型から曜日(平日または休日)を取得
    def test_Season(self):
        sc = nb.Schedule()
        self.assertEqual('休日', sc.Week(datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')) )
        self.assertEqual('平日', sc.Week(datetime.datetime.strptime('2017/07/21 19:00', '%Y/%m/%d %H:%M')) )

    #datetime型から季節(冷房または暖房)を取得
    def test_Season(self):
        sc = nb.Schedule()
        self.assertEqual('冷房', sc.Season(datetime.datetime.strptime('2017/07/20 19:00', '%Y/%m/%d %H:%M')) )
        self.assertEqual('暖房', sc.Season(datetime.datetime.strptime('2017/12/20 19:00', '%Y/%m/%d %H:%M')) )

if __name__ == '__main__':
    unittest.main()