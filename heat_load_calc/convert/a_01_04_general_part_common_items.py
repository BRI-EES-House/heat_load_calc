from typing import Dict, List
from collections import namedtuple

# 物性値を格納する名前付きタプル
#   name: 名前
#   method: 入力方法（熱伝導率と厚さを入力する方法と熱抵抗と厚さを入力する方法の2種類が存在する。）
#   lambda_m: 熱伝導率, W/mK
#   c_m: 体積熱容量, J/LK (method = 'conductivity' の場合に指定しないといけない。）
#   r_m: 熱抵抗, m2K/W (method = 'resistance' の場合に指定しないといけない。）
#   t_m: 厚さ, m
Layer = namedtuple('Layer', ('name', 'method', 'lambda_m', 'r_m', 'c_m', 't_m'))


def make_layer_hlc(layer_i_j: Dict) -> Dict:
    """
    層(1つ)から負荷計算用の層を作成する。

    Args:
        layer_i_j: 部分iの層j

    Returns:
        負荷計算用の層
    """

    # 負荷計算用の層を作成する。
    # 応答係数法においては熱抵抗(m2K/W)と熱容量(kJ/m2K)があればよい。
    # 熱容量は層iの材料の容積比熱（単位体積あたりの熱容量）ではなくて単位面積あたりの層の熱容量であることに注意。

    # 部分iの層jの名前（名前はデバッグ用にあったら便利なので作成）
    name_i_j = layer_i_j['name']

    # 部分iの層jの熱抵抗, m2K/W
    r_i_j = get_r_i_j(layer_i_j)

    # 部分iの層jの熱容量, kJ/m2K
    c_i_j = get_c_hlc_i(c_m_i=layer_i_j['volumetric_specific_heat'], t_i=layer_i_j['thickness'])

    return {
        'name': name_i_j,
        'thermal_resistance': r_i_j,
        'thermal_capacity': c_i_j
    }


def get_u_i(layers_i: List[Dict], r_i: float, r_o: float) -> float:
    """
    部分iの熱貫流率を計算する

    Args:
        layers_i : 部分iの層
        r_i : 室内側熱伝達抵抗, m2K/W
        r_o : 室外側熱伝達抵抗, m2K/W

    Returns:
        部分iの熱還流率, W/m2K
    """

    # 部分iの層の熱抵抗の合計（表面熱伝達抵抗を除く）, m2K/W
    r_layers_i = get_r_layers_i(layers_i=layers_i)

    return 1 / (r_i + r_layers_i + r_o)


def get_r_layers_i(layers_i: List[Dict]) -> float:
    """
    部分iの層の熱抵抗の合計（表面熱伝達抵抗を除く）を計算する

    Args:
        layers_i : 部分iの層

    Returns:
        部分iの層の熱抵抗の合計（表面熱伝達抵抗を除く）, m2K/W
    """

    return sum([get_r_i_j(layer_i_j) for layer_i_j in layers_i])


def get_r_i_j(layer_i_j: Dict) -> float:
    """
    部分iの層jの情報からその層の熱抵抗を計算する。

    Args:
        layer_i_j : 部分iの層j

    Returns:
        部分iの層jの熱抵抗, m2K/W

    Notes:
        層の熱抵抗の表現方法として、熱伝導率と厚さで表す方法と熱抵抗そのもので表す方法の2種類あるため、
        入力方法ごとに熱抵抗を計算する。
    """

    # 入力方法
    #   'conductivity': 熱伝導率(W/mK)と厚さ(m)で表す方法
    #   'resistance': 熱抵抗(m2K/W)そのもので表す方法
    method = layer_i_j['heat_resistance_input_method']

    # 熱伝導率と厚さで表す場合
    if method == 'conductivity':
        return get_r_hlc_i(lambda_i=layer_i_j['thermal_conductivity'], t_i=layer_i_j['thickness'])

    # 熱抵抗で表す場合
    elif method == 'resistance':
        return layer_i_j['thermal_resistance']

    else:
        raise KeyError()


def get_r_hlc_i(lambda_i: float, t_i: float) -> float:
    """
    負荷計算用の層iにおける熱抵抗を求める。

    Args:
        lambda_i: 負荷計算用の層iにおける熱伝導率, W/mK
        t_i: 負荷計算用の層iにおける厚さ, m

    Returns:
        負荷計算用の層iにおける熱抵抗, W/m2K
    """

    return t_i / lambda_i


def get_c_hlc_i(c_m_i: float, t_i: float) -> float:
    """
    負荷計算用の層iにおける熱容量を求める。

    Args:
        c_m_i: 負荷計算用層iの材料の単位体積あたりの容積比熱, J/LK
        t_i: 負荷計算用層iの厚さ, m

    Returns:
        負荷計算用の層iにおける熱容量, kJ/m2K
    """

    # 1m3 = 1000L
    # 1kJ = 1000J

    # 容積比熱は小文字のc
    # 熱容量は大文字のC

    return c_m_i * t_i
