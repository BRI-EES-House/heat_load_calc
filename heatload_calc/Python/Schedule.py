import ACSet
import AnnualCal
import Appl
import Light
import LocalVent
import Resi
import common


# 各種スケジュールデータを統括するクラス
class Schedule:

    # 各種スケジュールクラスの初期化
    def __init__(self):
        self.__objACSet = ACSet.ACSet()
        self.__objAnnualCal = AnnualCal.AnnualCal()
        self.__objAppl = Appl.Appl()
        self.__objLight = Light.Light()
        self.__objLocalVent = LocalVent.LocalVent()
        self.__objResi = Resi.Resi()

    # 空調設定温湿度の取得
    def ACSet(self, strRoomName, strTH, dtmDate):
        """
        :param strRoomName: 室名
        :param strTH: 設定分類（'温度' or '湿度'）
        :param dtmDate:
        :return: 空調設定温湿度
        """
        # 時刻の取得
        lngTime = dtmDate.hour

        # 曜日（'平日' or '休日'）の取得
        Nday = common.Nday(dtmDate)
        strWeek = self.__objAnnualCal.Week(common.Nday(dtmDate))

        # 運転モード（'冷房' or '暖房'）の取得
        strMode = self.__objAnnualCal.Season(Nday)

        return self.__objACSet(strRoomName, strMode, strWeek, strTH, lngTime)

    # 機器発熱スケジュールの取得
    def Appl(self, strRoomName, strSHLH, dtmDate):
        """
        :param strRoomName:
        :param strSHLH: 機器発熱分類（'顕熱' or '潜熱'）
        :param dtmDate:
        :return:
        """
        # 時刻の取得
        lngTime = dtmDate.hour

        # 曜日（'平日' or '休日'）の取得
        strWeek = self.__objAnnualCal.Week(common.Nday(dtmDate))

        return self.__objAppl(strRoomName, strWeek, strSHLH, lngTime)

    # 照明発熱スケジュールの取得
    def Light(self, strRoomName, dtmDate):
        # 時刻の取得
        lngTime = dtmDate.hour

        # 曜日（'平日' or '休日'）の取得
        strWeek = self.__objAnnualCal.Week(common.Nday(dtmDate))

        return self.__objLight(strRoomName, strWeek, lngTime)

    # 局所換気スケジュールの取得
    def LocalVent(self, strRoomName, dtmDate):
        # 時刻の取得
        lngTime = dtmDate.hour

        # 曜日（'平日' or '休日'）の取得
        strWeek = self.__objAnnualCal.Week(common.Nday(dtmDate))

        return self.__objLocalVent(strRoomName, strWeek, lngTime)

    # 在室人員スケジュールの取得
    def Nresi(self, strRoomName, dtmDate):
        # 時刻の取得
        lngTime = dtmDate.hour

        # 曜日（'平日' or '休日'）の取得
        strWeek = self.__objAnnualCal.Week(common.Nday(dtmDate))

        return self.__objResi(strRoomName, strWeek, lngTime)

    # datetime型から曜日を取得する
    def Week(self, dtmDate):
        return self.__objAnnualCal.Week(common.Nday(dtmDate))

    # datetime型から季節を取得する
    def Season(self, dtmDate):
        return self.__objAnnualCal.Season(common.Nday(dtmDate))
