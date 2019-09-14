import numpy as np
import a23_surface_heat_transfer_coefficient as a23
import a25_window as a25

"""
付録24．壁体構成
"""

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

