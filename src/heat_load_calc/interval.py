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
        """1時間を分割するステップ数を求める。

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
        """1時間を分割するステップに応じてインターバル時間を取得する。

        Returns:
            インターバル時間, h
        """

        return {
            Interval.H1: 1.0,
            Interval.M30: 0.5,
            Interval.M15: 0.25
        }[self]

    def get_annual_number(self):
        """対応するインターバルにおいて1年間は何ステップに対応するのか、その数を取得する。

        Returns:
            1年間のステップ数
        Notes:
            瞬時値の結果は、1/1 0:00 と 12/31 24:00(=翌年の1/1 0:00) の値を含むため、+1 される。
            この関数で返す値は「+1されない」値である。
        """

        return 8760 * self.get_n_hour()

    def get_pandas_freq(self):
        """pandas 用の freq 引数を取得する。

        Returns:
            freq 引数
        """

        return {
            Interval.M15: '15min',
            Interval.M30: '30min',
            Interval.H1: 'H'
        }[self]
