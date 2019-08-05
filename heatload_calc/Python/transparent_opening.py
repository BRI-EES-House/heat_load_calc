from oblique_incidence_characteristics import get_CID

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
        self.incident_angle_characteristics = int(d_window['incident_angle_characteristics'])


