from Psychrometrics import xtrh

# ## ２）室間換気量に関するクラス

# 室間換気量に関する情報を保持します。
# 
# - roomname:      流入室名称
# - volume:        流入量, m3/h

class NextVent:
    def __init__(self, Windward_roomname, volume):
        # 風上室名
        self.windward_roomname = Windward_roomname

        # 流入風量[m3/h]
        self.volume = volume

        # 風上室の室温を初期化(前時刻の隣室温度)
        self.oldTr = 15.0
        self.oldxr = xtrh(20.0, 40.0)

    # 風上室の室温を更新
    def update_oldstate(self, oldTr, oldxr):
        self.oldTr = oldTr
        self.oldxr = oldxr
