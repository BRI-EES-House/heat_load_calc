from Psychrometrics import xtrh

# ## ２）室間換気量に関するクラス

# 室間換気量に関する情報を保持します。
# 
# - roomname:      流入室名称
# - volume:        流入量, m3/h

class NextVent:
    def __init__(self, Windward_roomname, volume):
        # 風上室名
        self.__Windward_roomname = Windward_roomname

        # 流入風量[m3/h]
        self.__volume = volume

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
    def next_vent(self):
        return self.__volume
