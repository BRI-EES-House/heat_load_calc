import datetime


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
        self.Region = int(options["region"])

        # 住宅計算／非住宅計算（Trueなら住宅）
        self.is_residential = options["is_residential"]

        # 計算対象年
        self.__conlngYr = 1989

        # 計算時間間隔(s)
        if self.is_residential:
            self.DTime = 900.0
        else:
            self.DTime = 3600.0

        # 助走計算期間(day)
        self.__lngApproach = 20
        # シミュレーション（本計算）の開始日
        self.StDate = datetime.datetime(self.__conlngYr, 1, 1)
        # シミュレーション（本計算）終了日
        self.EnDate = datetime.datetime(self.__conlngYr, 12, 31)
        if 0:
            self.StDate = datetime.datetime(self.__conlngYr, 8, 1)
            self.EnDate = datetime.datetime(self.__conlngYr, 8, 1)
            self.__lngApproach = 0
        if 0:
            self.StDate = datetime.datetime(self.__conlngYr, 1, 1)
            self.EnDate = datetime.datetime(self.__conlngYr, 1, 1)
            self.__lngApproach = 0
        # self.EnDate = datetime.datetime(self.__conlngYr, 1, 1)
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
        # self.OTset = True
        # 緯度、経度
        self.Latitude, self.Longitude = self.__calcLat_Lon(self.Region)
        # 気象データの設定
        self.wdfile = self.set_wdfile(self.Region)
        # 標準子午線
        self.StMeridian = 135.0

    # 本計算フラグ
    def FlgOrig(self, dtmDate):
        return (self.StDate <= dtmDate)

    # 気象データファイルの設定
    def set_wdfile(self, Region: int):
        if Region == 1:
            # 1地域（北見）
            wfile = 'weather_data\\1_Kitami.csv'
        elif Region == 2:
            # 2地域（岩見沢）
            wfile = 'weather_data\\2_Iwamizawa.csv'
        elif Region == 3:
            # 3地域（盛岡）
            wfile = 'weather_data\\3_Morioka.csv'
        elif Region == 4:
            # 4地域（長野）
            wfile = 'weather_data\\4_Nagano.csv'
        elif Region == 5:
            # 5地域（宇都宮）
            wfile = 'weather_data\\5_Utsunomiya.csv'
        elif Region == 6:
            # 6地域（岡山）
            wfile = 'weather_data\\6_Okayama.csv'
        elif Region == 7:
            # 7地域（宮崎）
            wfile = 'weather_data\\7_Miyazaki.csv'
        elif Region == 8:
            # 8地域（那覇）
            wfile = 'weather_data\\8_Naha.csv'

        return wfile

    # 地域区分から緯度、経度を設定する
    # 当面は6地域の緯度、経度を返す
    def __calcLat_Lon(self, Region):
        Latitude = -999.0
        Longitude = -999.0

        if Region == 1:
            # 1地域（北見）
            Latitude = 43.82
            Longitude = 143.91
        elif Region == 2:
            # 2地域（岩見沢）
            Latitude = 43.21
            Longitude = 141.79
        elif Region == 3:
            # 3地域（盛岡）
            Latitude = 39.70
            Longitude = 141.17
        elif Region == 4:
            # 4地域（長野）
            Latitude = 36.66
            Longitude = 138.20
        elif Region == 5:
            # 5地域（宇都宮）
            Latitude = 36.55
            Longitude = 139.87
        elif Region == 6:
            # 6地域（岡山）
            Latitude = 34.66
            Longitude = 133.92
        elif Region == 7:
            # 7地域（宮崎）
            Latitude = 31.94
            Longitude = 131.42
        elif Region == 8:
            # 8地域（那覇）
            Latitude = 26.21
            Longitude = 127.685
        return Latitude, Longitude
