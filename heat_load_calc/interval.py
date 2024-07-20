from enum import Enum

"""
時間間隔に関するモジュール
"""


class Interval(Enum):
    """Interval for calculation. / 計算するインターバル。
    
    Notes:
        Interval is selected by;
            1 hour
            30 minutes
            15 minutes.
    """

    H1 = '1h'
    M30 = '30m'
    M15 = '15m'

    def get_n_hour(self):
        """Calculate the number of steps deviding the hour. / 1時間を分割するステップ数を求める。

        Returns:
            number of steps divideing hour / 1時間を分割するステップ数

        Notes:
            1 hour / 1時間: 1
            30 minutes / 30分: 2
            15 minutes / 15分: 4
        """

        return {
            Interval.H1: 1,
            Interval.M30: 2,
            Interval.M15: 4
        }[self]

    def get_delta_h(self):
        """Get the interval time depending the number of steps dividing one hour. / 1時間を分割するステップに応じてインターバル時間を取得する。

        Returns:
            interval time for calculation/ 計算時間間隔, h
        """

        return {
            Interval.H1: 1.0,
            Interval.M30: 0.5,
            Interval.M15: 0.25
        }[self]

    def get_delta_t(self):
        """Get the interval time depending the number of steps dividing one hour. / 1時間を分割するステップに応じてインターバル時間を取得する。

        Returns:
            interval time for calculation/ 計算時間間隔, s
        """

        return {
            Interval.H1: 3600,
            Interval.M30: 1800,
            Interval.M15: 900
        }[self]

    def get_n_step_annual(self):
        """Get the annual number of steps. / 1年間のステップ数を取得する。

        Returns:
            annual number of steps / 1年間のステップ数
        Notes:
            瞬時値の結果は、1/1 0:00 と 12/31 24:00(=翌年の1/1 0:00) の値を含むため、+1 される。
            この関数で返す値は「+1されない」値である。
        """

        return 8760 * self.get_n_hour()

    def get_pandas_freq(self):
        """Get the freq argument for pandas. / pandas 用の freq 引数を取得する。

        Returns:
            freq 引数
        """

        return {
            Interval.M15: '15min',
            Interval.M30: '30min',
            Interval.H1: 'h'
        }[self]
