import math
import numpy as np
import copy
from typing import List


# 壁体構成部材のクラス
class Layer:

    # 初期化
    def __init__(self, name, cond, spech, thick):
        """
        :param name: 部位名称
        :param cond: 熱伝導率[W/(m・K)]
        :param spech: 容積比熱[kJ/(m3・K)]
        :param thick: 厚さ[m]
        """
        self.name = name  # 部材名称
        self.Lam = float(cond)  # 熱伝導率[W/(m・K)]

        # 容積比熱[kJ/(m3・K)] → [J/(m3・K)]
        self.Spcheat = float(spech * 1000) if spech is not None else 0.0

        # 厚さ[m]
        self.Dim = float(thick) if thick is not None else 0.0

        # 熱抵抗[(m2・K)/W]
        if abs(self.Dim) < 0.001:
            self.R = 1 / self.Lam  # 厚さが0.0mの場合は分子を1とする
        else:
            self.R = self.Dim / self.Lam

        # 熱容量[J/(m2・K)]
        self.C = self.Spcheat * self.Dim


# 壁体の基本情報（壁体名称、層構成、熱伝達率等）を保持するクラス
class Wall:

    # 初期化
    def __init__(self, Name: str, IsSoil: bool, OutEmissiv: float, OutSolarAbs: float, InHeatTrans: float,
                 Layers: List[Layer]):
        """
        :param Name: 壁体名称
        :param OutEmissiv: 室外側放射率[-]
        :param OutSolarAbs: 室外側日射吸収率[-]
        :param InConHeatTrans: 室内対流熱伝達率[W/(m2･K)]
        :param InRadHeatTrans: 室内放射熱伝達率[W/(m2･K)]
        :param Layers: 壁体構成部材の情報クラスの配列
        """
        self.Name = Name  # 名前
        self.Eo = OutEmissiv  # 室外側放射率[-]
        self.Solas = OutSolarAbs  # 室外側日射吸収率[-]
        self.IsSoil = IsSoil        # 壁体に土壌が含まれる場合はTrue
        self.Ei = 0.9               # 室内側放射率[－]

        # 室内総合熱伝達率[W/(m2･K)]
        self.hi = InHeatTrans
        # 室内表面熱伝達率の初期化[W/(m2･K)]
        self.hic = 0.0
        self.hir = 0.0

        # 壁体構成部材配列
        self.Layers = copy.deepcopy(Layers)

        # 室外側熱伝達率
        self.ho = self.Layers[-1].Lam

