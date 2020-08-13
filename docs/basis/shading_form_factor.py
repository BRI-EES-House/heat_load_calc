import math


def calc_shading_ff(y1:float, yw:float, z:float) -> float:
    """

    Args:   長さの寸法は統一されていれば[m]である必要はない
    :param y1:  窓の上端から庇までの長さ[m]
    :param yw:  窓の高さ[m]
    :param z:   庇の出幅[m]
    :return:    窓から庇を見る形態係数[－]
    """
    ac = y1 + yw
    ab = z
    ad = y1
    dc = yw
    bd = math.sqrt(ad**2.0 + ab**2.0)
    bc = math.sqrt((ad + dc)**2.0 + ab**2.0)

    return ((ac + bd) - (ad + bc)) / (2.0 * dc)
