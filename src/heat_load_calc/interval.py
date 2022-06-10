from enum import Enum

"""
時間間隔に関するモジュール
"""


class Interval(Enum):
    """
    計算するインターバル
    現状以下を用意する。
        1時間
        30分
        15分
    Notes:
        1時間を正数で分割する必要があるため、列挙型で管理することにした。
        上記に挙げたインターバール以外にも例えば以下のインターバールを将来的に実装することが考えられる。
        20分, 12分, 10分, 6分, 5分, 4分, 3分, 2分, 1分
    """

    H1 = '1h'
    M30 = '30m'
    M15 = '15m'

    def get_n_hour(self):
        """
        1時間を分割するステップ数を求める。

        Args:
            interval: 生成するデータの時間間隔

        Returns:
            1時間を分割するステップ数

        Notes:
            1時間: 1
            30分: 2
            15分: 4
        """

        return {
            Interval.H1: 1,
            Interval.M30: 2,
            Interval.M15: 4
        }[self]

    def get_time(self):
        """
        1時間を分割するステップに応じてインターバル時間を取得する。

        Args:
            interval: 生成するデータの時間間隔

        Returns:
            インターバル時間, h
        """

        return {
            Interval.H1: 1.0,
            Interval.M30: 0.5,
            Interval.M15: 0.25
        }[self]
