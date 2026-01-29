from typing import Dict


from heat_load_calc.tenum import EInterval


"""
時間間隔に関するモジュール
"""


class Interval:

    def __init__(self, eitv: EInterval):

        self._eitv = eitv
    
    @property
    def interval(self):
        return self._eitv

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
            EInterval.H1: 1,
            EInterval.M30: 2,
            EInterval.M15: 4
        }[self._eitv]

    def get_delta_h(self):
        """Get the interval time depending the number of steps dividing one hour. / 1時間を分割するステップに応じてインターバル時間を取得する。

        Returns:
            interval time for calculation/ 計算時間間隔, h
        """

        return {
            EInterval.H1: 1.0,
            EInterval.M30: 0.5,
            EInterval.M15: 0.25
        }[self._eitv]

    def get_delta_t(self):
        """Get the interval time depending the number of steps dividing one hour. / 1時間を分割するステップに応じてインターバル時間を取得する。

        Returns:
            interval time for calculation/ 計算時間間隔, s
        """

        return {
            EInterval.H1: 3600,
            EInterval.M30: 1800,
            EInterval.M15: 900
        }[self._eitv]

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
            EInterval.M15: '15min',
            EInterval.M30: '30min',
            EInterval.H1: 'h'
        }[self._eitv]


def set_interval(d_common: Dict):

    # Check the existance of the item "interval" in the common tag.
    # If not exist, M15 is set as default value.
    if 'interval' not in d_common:

        return Interval(eitv=EInterval.M15)

    else:
    
        s_itv = d_common['interval']

        return Interval(eitv=EInterval(s_itv))
