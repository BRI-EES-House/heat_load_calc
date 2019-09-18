import datetime
import a17_calculation_period as a17


class Gdata:
    """シミュレーション全体の設定条件"""

    def __init__(self, **options):
        """
        :param Region: 地域区分
        :param TimeInterval: 計算時間間隔(s)
        :param PreCalc: 助走計算期間(day)
        :param SimStMo: シミュレーション（本計算）の開始日の月部分
        :param SimStDay: シミュレーション（本計算）の開始日の日部分
        :param SimEnMo: シミュレーション（本計算）の終了日の月部分
        :param SimEnDay: シミュレーション（本計算）の終了日の日部分
        :param Latitude: 緯度
        :param Longitude: 経度
        :param StMeridian: 標準子午線
        :param options: その他のオプション
        """
        # 地域区分
        self.Region = options["region"]

        # 計算対象年
        self.conlngYr = 1989

        # 計算期間、助走計算日数の設定
        a17.calc_period(self)

        # 応答係数の作成時間数(hour)
        # self.__lngNcalTime = lngNcalTime
        # 計算結果の行数
        self.OutputRow = int(((self.EnDate - self.StDate).days + 1) * 24 * 3600 / 900)
        # comment - miura : 3600 / dblDtime が必ずしも整数になるとは限らない。その場合のエラー処理が必要か、そもそもdblDtimeではなくて、1時間の分割数とかで入力させるべき。
        # 詳細出力フラグ
        # self.__blnDetailOut = blnDetailOut
        # 作用温度設定フラグ
        # self.OTset = True


# 本計算フラグ
def is_actual_calc(gdata: Gdata, dtmDate: datetime) -> bool:
    return (gdata.StDate <= dtmDate)
