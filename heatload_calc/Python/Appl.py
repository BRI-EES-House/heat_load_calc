import csv


# 機器発熱スケジュールデータ
class Appl:
    """
    機器発熱スケジュールを保持するクラス
    - csvファイルから毎時の機器発熱スケジュールを読み込み、辞書型として保持します。
    - メソッド'Appl'は、「室名」、「室分類」、「機器発熱分類（'顕熱' or '潜熱'）」、「曜日（'平日' or '休日'）」および「時刻」を与えると、指定した時刻の機器発熱量を返します。
    - 顕熱発熱量の単位は[W], 潜熱発熱量の単位は[g/h]です。
    """

    # 機器発熱スケジュールデータの取得
    def __init__(self):

        # 機器発熱スケジュールの読み込み
        with open('appliances.csv', encoding='utf-8') as f:
            reader = csv.reader(f)
            _ = next(reader)

            # 機器発熱
            self.__dicAppl = {}
            for row in reader:
                Col = 0
                strRoomName = row[Col]  # 室名
                Col += 1
                strSHLH = row[Col]  # 機器発熱分類（'顕熱' or '潜熱'）
                Col += 1
                strWeek = row[Col]  # 曜日（'平日' or '休日'）
                Col += 1

                # 毎時スケジュールのリストを設定
                dblHourly = []
                for hour in range(24):
                    dblHourly.append(float(row[Col]))
                    Col += 1

                # 機器発熱をセット
                # 顕熱の単位は[W], 潜熱の単位は[g/h]
                key = strRoomName + ',' + strWeek + ',' + strSHLH
                self.__dicAppl[key] = dblHourly

    # 指定した時刻の機器発熱量の取得
    def __call__(self, strRoomName, strWeek, strSHLH, lngTime):
        key = strRoomName + ',' + strWeek + ',' + strSHLH
        appl = 0.0
        if key in self.__dicAppl.keys():
            vntHourly = self.__dicAppl[key]
            appl = vntHourly[lngTime]
        return appl
