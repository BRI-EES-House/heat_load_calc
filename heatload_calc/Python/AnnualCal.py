import csv
import datetime
import common


# 年間カレンダーデータ
class AnnualCal:
    """
    年間カレンダーを保持するクラス
    - csvファイルから年間カレンダーを読み込み、辞書型で保持します
    - 「曜日（'平日' or '休日'）」および「運転モード（'冷房' or '暖房'）」の２つのカレンダーを辞書型として保持しており、通日をkeyとして与えると、該当日の曜日または運転モードの情報を返します
    """

    # 年間カレンダーデータの取得
    def __init__(self):
        # 曜日（'平日' or '休日'）の年間カレンダー
        self.__dicWeek = {}
        # 運転モード（'冷房' or '暖房'）の年間カレンダー
        self.__dicSeason = {}

        # 年間カレンダーデータの読み込み
        with open('calendar.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            _ = next(reader)
            for row in reader:
                # 通日の計算
                lngNday = common.Nday(datetime.datetime.strptime(row[0], '%m月%d日'))
                self.__dicWeek[lngNday] = row[1]  # 曜日
                self.__dicSeason[lngNday] = row[2]  # 運転モード

    # 曜日の取得
    def Week(self, lngNday):
        # lngNday:通日
        nday = lngNday
        if nday > 365:
            nday -= 365
        return self.__dicWeek[nday]

    # 運転モードの取得
    def Season(self, lngNday):
        # lngNday:通日
        nday = lngNday
        if nday > 365:
            nday -= 365
        return self.__dicSeason[nday]
