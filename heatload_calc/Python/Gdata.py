import datetime


class Gdata:
    """シミュレーション全体の設定条件"""

    def __init__(self, Region, **options):
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
        self.__Region = Region

        # 計算対象年
        self.__conlngYr = 1989

        # 計算時間間隔(s)
        self.DTime = 900

        # 助走計算期間(day)
        self.__lngApproach = 20
        # self.__lngApproach = 0
        # シミュレーション（本計算）の開始日
        self.StDate = datetime.datetime(self.__conlngYr, 1, 1)
        # self.StDate = datetime.datetime(self.__conlngYr, 1, 1)
        # シミュレーション（本計算）終了日
        self.EnDate = datetime.datetime(self.__conlngYr, 12, 31)
        # self.EnDate = datetime.datetime(self.__conlngYr, 1, 6)
        # 開始日が終了日よりも後の月日の場合は、終了日にプラス1年加算する。
        if self.StDate > self.EnDate:
            self.EnDate = self.EnDate + datetime.timedelta(days=365)
        # 助走計算開始時刻
        self.ApDate = self.StDate - datetime.timedelta(days=self.__lngApproach)
        # 応答係数の作成時間数(hour)
        # self.__lngNcalTime = lngNcalTime
        # 計算結果の行数
        self.OutputRow = int(((self.EnDate - self.StDate).days + 1) * 24 * 3600 / self.DTime)
        # comment - miura : 3600 / dblDtime が必ずしも整数になるとは限らない。その場合のエラー処理が必要か、そもそもdblDtimeではなくて、1時間の分割数とかで入力させるべき。
        # 詳細出力フラグ
        # self.__blnDetailOut = blnDetailOut
        # 作用温度設定フラグ
        self.OTset = True
        # 緯度、経度
        self.Latitude, self.Longitude = self.__calcLat_Lon(self.__Region)
        # 標準子午線
        self.StMeridian = 135.0

    # 本計算フラグ
    def FlgOrig(self, dtmDate):
        return (self.StDate <= dtmDate)

    # 地域区分から緯度、経度を設定する
    # 当面は6地域の緯度、経度を返す
    def __calcLat_Lon(self, Region):
        return 34.6583333333333, 133.918333333333
