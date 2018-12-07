import csv

# 照明発熱スケジュールデータ
class Light:
    """
    照明発熱スケジュールを保持するクラス
    - csvファイルから毎時の照明発熱スケジュールを読み込み、辞書型として保持します。
    - メソッド'Light'は、「室名」、「室分類」、「曜日（'平日' or '休日'）」および「時刻」を与えると、指定した時刻の照明発熱量を返します。
    - 照明発熱量の単位は[W], ただし蛍光灯の安定器損失20%を含んだ値です。
    """

    # 照明発熱スケジュールデータの取得
    def __init__(self):

        # 照明発熱スケジュールの読み込み
        with open('LightingSchedule.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)

            # 照明発熱
            self.__dicLight = {}
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

                # 照明発熱をセット
                # 単位は[W], 蛍光灯の安定器損失20%を含む
                key = strRoomName + ',' + strWeek
                self.__dicLight[key] = dblHourly

    # 指定した時刻の照明発熱量の取得
    def __call__(self, strRoomName, strWeek, lngTime):
        key = strRoomName + ',' + strWeek
        light = 0.0
        if key in self.__dicLight.keys():
            vntHourly = self.__dicLight[key]
            light = vntHourly[lngTime]
        return light
