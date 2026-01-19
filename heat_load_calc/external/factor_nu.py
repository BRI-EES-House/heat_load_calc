"""
方位係数を取得する。
"""

from enum import Enum


class Direction(Enum):

    TOP = 'top'
    N = 'n'
    NE = 'ne'
    E = 'e'
    SE = 'se'
    S = 's'
    SW = 'sw'
    W = 'w'
    NW = 'nw'
    BOTTOM = 'bottom'
    UPWARD = 'upward'
    HORIZONTAL = 'horizontal'
    DOWNWARD = 'downward'

    def get_nu(self, region: int, season: str) -> float:
        """Get direction coefficient.

        Args:
            region: 地域の区分
            season: 'heating' 又は 'cooling' ただし、8地域においては'heating'は指定できない
        Returns:
            方位係数
        """

        if region == 8 and season == 'heating':
            raise ValueError('暖房期の方位係数の計算において8地域が指定されました。')

        return {
            'heating': {
                Direction.TOP: {1: 1.000, 2: 1.000, 3: 1.000, 4: 1.000, 5: 1.000, 6: 1.000, 7: 1.000},
                Direction.N: {1: 0.260, 2: 0.263, 3: 0.284, 4: 0.256, 5: 0.238, 6: 0.261, 7: 0.227},
                Direction.NE: {1: 0.333, 2: 0.341, 3: 0.348, 4: 0.330, 5: 0.310, 6: 0.325, 7: 0.281},
                Direction.E: {1: 0.564, 2: 0.554, 3: 0.540, 4: 0.531, 5: 0.568, 6: 0.579, 7: 0.543},
                Direction.SE: {1: 0.823, 2: 0.766, 3: 0.751, 4: 0.724, 5: 0.846, 6: 0.833, 7: 0.843},
                Direction.S: {1: 0.935, 2: 0.856, 3: 0.851, 4: 0.815, 5: 0.983, 6: 0.936, 7: 1.023},
                Direction.SW: {1: 0.790, 2: 0.753, 3: 0.750, 4: 0.723, 5: 0.815, 6: 0.763, 7: 0.848},
                Direction.W: {1: 0.535, 2: 0.544, 3: 0.542, 4: 0.527, 5: 0.538, 6: 0.523, 7: 0.548},
                Direction.NW: {1: 0.325, 2: 0.341, 3: 0.351, 4: 0.326, 5: 0.297, 6: 0.317, 7: 0.284},
                Direction.BOTTOM: {1: 0.000, 2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000, 6: 0.000, 7: 0.000},
            },
            'cooling': {
                Direction.TOP: {1: 1.000, 2: 1.000, 3: 1.000, 4: 1.000, 5: 1.000, 6: 1.000, 7: 1.000, 8: 1.000},
                Direction.N: {1: 0.329, 2: 0.341, 3: 0.335, 4: 0.322, 5: 0.373, 6: 0.341, 7: 0.307, 8: 0.325},
                Direction.NE: {1: 0.430, 2: 0.412, 3: 0.390, 4: 0.426, 5: 0.437, 6: 0.431, 7: 0.415, 8: 0.414},
                Direction.E: {1: 0.545, 2: 0.503, 3: 0.468, 4: 0.518, 5: 0.500, 6: 0.512, 7: 0.509, 8: 0.515},
                Direction.SE: {1: 0.560, 2: 0.527, 3: 0.487, 4: 0.508, 5: 0.500, 6: 0.498, 7: 0.490, 8: 0.528},
                Direction.S: {1: 0.502, 2: 0.507, 3: 0.476, 4: 0.437, 5: 0.472, 6: 0.434, 7: 0.412, 8: 0.480},
                Direction.SW: {1: 0.526, 2: 0.548, 3: 0.550, 4: 0.481, 5: 0.520, 6: 0.491, 7: 0.479, 8: 0.517},
                Direction.W: {1: 0.508, 2: 0.529, 3: 0.553, 4: 0.481, 5: 0.518, 6: 0.504, 7: 0.495, 8: 0.505},
                Direction.NW: {1: 0.411, 2: 0.428, 3: 0.447, 4: 0.401, 5: 0.442, 6: 0.427, 7: 0.406, 8: 0.411},
                Direction.BOTTOM: {1: 0.000, 2: 0.000, 3: 0.000, 4: 0.000, 5: 0.000, 6: 0.000, 7: 0.000, 8: 0.000},
            }
        }[season][self][region]

    def is_horizontal(self) -> bool:
        """
        方位が水平方向かどうかを判定する。
        Returns:
            水平方向か否か
        """
        return self in [
            Direction.N,
            Direction.NE,
            Direction.E,
            Direction.SE,
            Direction.S,
            Direction.SW,
            Direction.W,
            Direction.NW,
            Direction.HORIZONTAL
        ]
