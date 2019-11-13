import math
import numpy as np
import copy
from typing import List

# 壁体構成部材のクラス
class Layer:

    # 初期化
    def __init__(self, name, thermal_resistance, thermal_capacity):
        """
        :param name: 部位名称
        :param thermal_resistance: 熱抵抗[m2･K/W]
        :param spech: 熱容量[kJ/(m2・K)]
        """
        self.name = name  # 部材名称

        # 熱抵抗[(m2・K)/W]
        self.R = thermal_resistance

        # 熱容量[J/(m2・K)]
        self.C = thermal_capacity * 1000.0

# 壁体の基本情報（壁体名称、層構成、熱伝達率等）を保持するクラス
class Wall:

    # 初期化
    def __init__(self, is_ground: bool, outside_emissivity: float,
        outside_solar_absorption: float, inside_heat_transfer_coef: float,
        outside_heat_transfer_coef: float,
        Layers: List[Layer]):
        """
        :param Name: 壁体名称
        :param outside_emissivity: 室外側放射率[-]
        :param outside_solar_absorption: 室外側日射吸収率[-]
        :param InConHeatTrans: 室内対流熱伝達率[W/(m2･K)]
        :param InRadHeatTrans: 室内放射熱伝達率[W/(m2･K)]
        :param Layers: 壁体構成部材の情報クラスの配列
        """
        self.Eo = outside_emissivity        # 室外側放射率[-]
        self.Ei = 0.9               # 室内側放射率[－]
        self.Solas = outside_solar_absorption    # 室外側日射吸収率[-]
        self.hi = inside_heat_transfer_coef       # 室内側総合熱伝達率[W/(m2･K)]
        self.hic = 0.0              # 室内対流熱伝達率[W/(m2･K)]
        self.hir = 0.0              # 室内放射熱伝達率[W/(m2･K)]
        self.is_ground = is_ground        # 壁体に土壌が含まれる場合はTrue

        # 室内総合熱伝達率[W/(m2･K)]
        # self.hi = self.hic + self.hir

        # 壁体構成部材配列
        self.Layers = copy.deepcopy(Layers)

        # 室外側熱伝達率
        self.ho = outside_heat_transfer_coef

