import datetime
import Gdata

def calc_period(gdata: Gdata) ->None:
    # 助走計算期間(day)
    gdata.lngApproach = 20
    # シミュレーション（本計算）の開始日
    gdata.StDate = datetime.datetime(gdata.conlngYr, 1, 1)
    # シミュレーション（本計算）終了日
    gdata.EnDate = datetime.datetime(gdata.conlngYr, 12, 31)
    if 1:
        gdata.StDate = datetime.datetime(gdata.conlngYr, 8, 1)
        gdata.EnDate = datetime.datetime(gdata.conlngYr, 8, 1)
        gdata.lngApproach = 0
    if 0:
        gdata.StDate = datetime.datetime(gdata.conlngYr, 1, 1)
        gdata.EnDate = datetime.datetime(gdata.conlngYr, 1, 1)
        gdata.lngApproach = 0
    
    # 開始日が終了日よりも後の月日の場合は、終了日にプラス1年加算する。
    if gdata.StDate > gdata.EnDate:
        gdata.EnDate = gdata.EnDate + datetime.timedelta(days=365)
    # 助走計算開始時刻
    gdata.ApDate = gdata.StDate - datetime.timedelta(days=gdata.lngApproach)