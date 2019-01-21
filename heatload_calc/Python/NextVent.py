import SeasonalValue
from SeasonalValue import SeasonalValue
from Psychrometrics import xtrh


# ## ２）室間換気量に関するクラス

# 室間換気量に関する情報を保持します。
# 
# - roomname:      流入室名称
# - winter:        暖房期の流入量, m3/h
# - inter:         中間期の流入量, m3/h
# - summer:        冷房期の流入量, m3/h

class NextVent:
    def __init__(self, Windward_roomname, winter, inter, summer):
        # 風上室名
        self.__Windward_roomname = Windward_roomname

        # 風下室名
        self.__SeasonValue = SeasonalValue(float(winter), float(inter), float(summer))

        # 風上室の室温を初期化(前時刻の隣室温度)
        self.oldTr = 15.0
        self.oldxr = xtrh(20.0, 40.0)

    # 風上室の室温を更新
    def update_oldstate(self, oldTr, oldxr):
        # 前時刻の隣室温度
        self.oldTr = oldTr
        # 前時刻の隣室湿度
        self.oldxr = oldxr

    # 風上室の室名を返す
    @property
    def Windward_roomname(self):
        return self.__Windward_roomname

    # 風量を返す
    def next_vent(self, season):
        vent_volume = 0.0
        if season == "暖房":
            vent_volume = self.__SeasonValue.winter
        elif season == "中間":
            vent_volume = self.__SeasonValue.inter
        elif season == "冷房":
            vent_volume = self.__SeasonValue.summer
        else:
            print('未定義の季節[{}]です'.format(season))
        return vent_volume
