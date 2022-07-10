import numpy as np
from enum import Enum


class Direction(Enum):

    S = 's'
    SW = 'sw'
    W = 'w'
    NW = 'nw'
    N = 'n'
    NE = 'ne'
    E = 'e'
    SE = 'se'
    TOP = 'top'
    BOTTOM = 'bottom'

    @property
    def alpha_w_j(self):
        """境界 j の傾斜面の方位角を取得する。

        Returns:
            alpha_w_j: 境界 j の傾斜面の方位角, rad
        """

        if self == Direction.TOP or self == Direction.BOTTOM:

            raise KeyError("方位が上面・下面が定義されているにもかかわらず、方位角を取得しようとしました。")

        else:

            return np.radians(
                {
                    Direction.S: 0.0,
                    Direction.SW: 45.0,
                    Direction.W: 90.0,
                    Direction.NW: 135.0,
                    Direction.N: 180.0,
                    Direction.NE: -135.0,
                    Direction.E: -90.0,
                    Direction.SE: -45.0
                }[self]
            )

    @property
    def beta_w_j(self):
        """境界 j の傾斜面の傾斜角を取得する。

        Returns:
            境界 j の傾斜面の傾斜角, rad
        """

        if self in [
            Direction.S, Direction.SW, Direction.W, Direction.NW, Direction.N, Direction.NE, Direction.E, Direction.SE,
        ]:
            return np.radians(90.0)
        elif self == Direction.TOP:
            return np.radians(0.0)
        elif self == Direction.BOTTOM:
            return np.radians(180.0)
        else:
            raise KeyError()

