import csv


# 人体スケジュールデータ
class Resi:
    """
    人体スケジュールを保持するクラス
    - csvファイルから毎時の人体スケジュールを読み込み、辞書型として保持します。
    - メソッド'Nresi'は、「室名」、「室分類」、「曜日（'平日' or '休日'）」および「時刻」を与えると、指定した時刻の在室人員数を返します。
    - 在室人員数の単位は[人]です。
    """

    # 人体スケジュールデータの取得
    def __init__(self):

        # 人体スケジュールの読み込み
        with open('ResidenceSchedule.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)

            # 在室人員数
            self.__dicResi = {}

            for row in reader:
                Col = 0
                strRoomName = row[Col]  # 室名
                Col += 1
                strWeek = row[Col]  # 曜日（'平日' or '休日'）
                Col += 1

                # 毎時スケジュールのリストを設定
                dblHourly = []
                for hour in range(24):
                    dblHourly.append(float(row[Col]))
                    Col += 1

                # 在室人員数をセット
                # 単位は[人]
                key = strRoomName + ',' + strWeek
                self.__dicResi[key] = dblHourly

    # 指定した時刻の在室人員数の取得
    def __call__(self, strRoomName, strWeek, lngTime):
        key = strRoomName + ',' + strWeek
        nresi = 0
        if key in self.__dicResi.keys():
            vntHourly = self.__dicResi[key]
            nresi = vntHourly[lngTime]
        return nresi
