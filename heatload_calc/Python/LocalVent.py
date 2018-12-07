import csv


# 局所換気スケジュールデータ
class LocalVent:
    """
    局所換気スケジュールを保持するクラス
    - csvファイルから毎時の局所換気スケジュールを読み込み、辞書型として保持します。
    - メソッド'Vent'は、「室名」、「室分類」、「曜日（'平日' or '休日'）」および「時刻」を与えると、指定した時刻の局所換気量を返します。
    - 局所換気量の単位は[m3/h]です。
    """

    # 局所換気スケジュールデータの取得
    def __init__(self):

        # 局所換気スケジュールの読み込み
        with open('LocalVentSchedule.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            _ = next(reader)

            # 局所換気
            self.__dicVent = {}

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

                # 局所換気をセット
                # 単位は[m3/h]
                key = strRoomName + ',' + strWeek
                self.__dicVent[key] = dblHourly

    # 指定した時刻の局所換気量の取得
    def __call__(self, strRoomName, strWeek, lngTime):
        vent = 0.0
        key = strRoomName + ',' + strWeek
        if key in self.__dicVent.keys():
            vntHourly = self.__dicVent[key]
            vent = vntHourly[lngTime]
        return vent
