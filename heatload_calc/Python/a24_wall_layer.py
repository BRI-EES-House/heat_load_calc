import numpy as np
import a23_surface_heat_transfer_coefficient as a23
import a25_window as a25

"""
付録24．壁体構成
"""

# 壁体の基本情報（壁体名称、層構成、熱伝達率等）を保持するクラス
def call_wall(boundary_type, is_ground: bool, d, is_solar_absorbed_inside):
    """
    :param Name: 壁体名称
    :param outside_emissivity: 室外側放射率[-]
    :param as_i_k: 室外側日射吸収率[-]
    :param InConHeatTrans: 室内対流熱伝達率[W/(m2･K)]
    :param InRadHeatTrans: 室内放射熱伝達率[W/(m2･K)]
    :param Layers: 壁体構成部材の情報クラスの配列
    """

    outside_heat_transfer_coef = 0.0
    if boundary_type == "external_general_part":
        outside_heat_transfer_coef = 1.0 / d['outside_heat_transfer_resistance']

    outside_solar_absorption = 0.0
    if is_solar_absorbed_inside:
        outside_solar_absorption = d['outside_solar_absorption']

    inside_heat_transfer_coef=1.0/d['inside_heat_transfer_resistance']

    Ei = 0.9               # 室内側放射率[－]
    hi = inside_heat_transfer_coef       # 室内側総合熱伝達率[W/(m2･K)]
    hic = 0.0              # 室内対流熱伝達率[W/(m2･K)]
    hir = 0.0              # 室内放射熱伝達率[W/(m2･K)]
    is_ground = is_ground        # 壁体に土壌が含まれる場合はTrue

    # 室外側熱伝達率
    ho = outside_heat_transfer_coef

    if is_solar_absorbed_inside:
        Solas = outside_solar_absorption  # 室側側日射吸収率
        Eo = d['outside_emissivity']  # 室外側表面放射率
    else:
        Solas = None
        Eo = None

    return Eo, Ei, Solas, hi, hic, hir, is_ground, ho


def get_layers(d, is_ground):
    # 壁体構成部材の情報を保持するクラスをインスタンス化
    # 層構成タプルリスト
    #         要素0: 熱抵抗[(m2・K)/W]
    #         a_i_k = thermal_resistance
    #
    #         要素1: 熱容量[J/(m2・K)]
    #         C = thermal_capacity * 1000.0
    layers = [(d_layers['thermal_resistance'], d_layers['thermal_capacity']) for d_layers in d['layers']]
    # 室外側総合熱伝達率の追加（土壌は除く）
    if not is_ground:
        layers.append((d['outside_heat_transfer_resistance'], 0.0))

    # 土壌の場合は土壌3mを追加
    # 土壌の熱伝導率λ=1.0W/mK、容積比熱cp=3300.0kJ/m3K
    else:
        layers.append((3.0 / 1.0, 3300.0 * 3.0))

    return np.array(layers)

