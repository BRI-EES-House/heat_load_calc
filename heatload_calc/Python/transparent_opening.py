# 開口部透明部位の情報を保持するクラス
class transparent_opening:
    """開口部透明部位の基本情報（開口部名称、日射熱取得率、熱貫流率等）を保持するクラス"""

    # 初期化
    def __init__(self, Name, d_window):
        """
        :param Name: 開口部名称
        :param d_window: 開口部情報
        """
        self.Name = Name                                            # 開口部名称, string値
        self.T = float(d_window['eta_value'])                       # 透過率＝日射熱取得率とする
        self.B = 0.0
        self.Uw = float(d_window['u_value'])                        # 開口部熱貫流率[W/m2K]
        self.ho = 1.0/float(d_window['outside_heat_transfer_resistance'])     # 室外側熱伝達率[W/m2K]
        self.Eo = float(d_window['outside_emissivity'])             # 室外側放射率[-]
        self.Ei = 0.9                                               # 室内側放射率[－]
        self.hic = 0.0  # 室内対流熱伝達率[W/(m2･K)]
        self.hir = 0.0  # 室内放射熱伝達率[W/(m2･K)]

        # 室内総合熱伝達率[W/(m2･K)]
        self.hi = 1.0/float(d_window['inside_heat_transfer_resistance'])

        # 窓部材熱抵抗[m2K/W]
        # self.Rw = 1.0 / self.Uw - 1.0 / self.hi - 1.0 / self.ho

        # 開口部の室内表面から屋外までの熱貫流率[W/(m2･K)]
        self.Uso = 1.0 / (1.0 / self.Uw - 1.0 / self.hi)

        # 拡散日射に対する入射角特性
        self.Cd = 0.92

        # 入射角特性番号
        self.__incident_angle_characteristics = float(d_window['incident_angle_characteristics'])

    # 直達日射の入射角特性の計算
    def get_CID(self, CosT: float) -> float:
        """
        :param CosT: 入射角の方向余弦
        :return: 直達日射の入射角特性
        """
        CID = (2.392 * CosT - 3.8636 * CosT ** 3.0 + 3.7568 * CosT ** 5.0 - 1.3965 * CosT ** 7.0) / 0.88
        return CID

    # 吸収日射熱取得[W/m2]の計算
    def get_QGA(self, Id: float, Isk: float, Ir: float, CosT: float, Fsdw: float) -> float:
        """
        :param Id: 傾斜面入射直達日射量[W/m2]
        :param Isk: 傾斜面入射天空日射量[W/m2]
        :param Ir: 傾斜面入射反射日射量[W/m2]
        :param CosT: 入射角の方向余弦
        :param Fsdw: 日よけ等による日影面積率
        :return: 吸収日射熱取得[W/m2]
        """
        # 直達日射の入射角特性の計算
        CID = self.get_CID(CosT)

        # 吸収日射熱取得[W/m2]の計算
        QGA = self.B * ((1.0 - Fsdw) * CID * Id + self.Cd * (Isk + Ir))

        return QGA

    # 透過日射熱取得（直達成分）[W/m2]の計算
    def get_QGTD(self, Id: float, CosT: float, Fsdw: float) -> float:
        """
        :param Id: 傾斜面入射直達日射量[W/m2]
        :param CosT: 入射角の方向余弦
        :param Fsdw: 日よけ等による日影面積率
        :return: 透過日射熱取得（直達成分）[W/m2]
        """
        # 直達日射の入射角特性の計算
        CID = self.get_CID(CosT)

        # 透過日射熱取得（直達成分）[W/m2]の計算
        QGTD = self.T * (1.0 - Fsdw) * CID * Id

        return QGTD

    # 透過日射熱取得（拡散成分）[W/m2]の計算
    def get_QGTS(self, Isk: float, Ir: float) -> float:
        """
        :param Isk: 傾斜面入射天空日射量[W/m2]
        :param Ir: 傾斜面入射反射日射量[W/m2]
        :return: 透過日射熱取得（拡散成分）[W/m2]
        """
        QGTS = self.T * self.Cd * (Isk + Ir)
        return QGTS

    # 透過日射熱取得[W/m2]の計算
    def get_QGT(self, Id: float, Isk: float, Ir: float, CosT: float, Fsdw: float) -> float:
        """
        :param Id: 傾斜面入射直達日射量[W/m2]
        :param Isk: 傾斜面入射天空日射量[W/m2]
        :param Ir: 傾斜面入射反射日射量[W/m2]
        :param CosT: 入射角の方向余弦
        :param Fsdw: 日よけ等による日影面積率
        :return: 透過日射熱取得[W/m2]
        """
        # 透過日射熱取得（直達成分）[W/m2]の計算
        QGTD = self.get_QGTD(Id, CosT, Fsdw)

        # 透過日射熱取得（拡散成分）[W/m2]の計算
        QGTS = self.get_QGTS(Isk, Ir)

        # 透過日射熱取得[W/m2]の計算
        QGT = QGTD + QGTS

        return QGT
