import numpy as np
import pandas as pd
import datetime as dt
import itertools
from typing import List

from heat_load_calc import pmv as pmv, psychrometrics as psy
from heat_load_calc.interval import EInterval, Interval
from heat_load_calc.weather import Weather
from heat_load_calc.schedule import Schedule
from heat_load_calc.rooms import Rooms
from heat_load_calc.equipments import Equipments
from heat_load_calc.boundaries import Boundaries
from heat_load_calc import operation_mode


class Recorder:
    """
    Notes:
        データは、「瞬時値」を記したものと、「平均値」「積算値」を記したものの2種類に分類される。
        瞬時値は、1/1 0:00 から始まり、最後のデータは、次の年の 1/1 0:00 (12/31 24:00) となる。
        従って、計算ステップの数よりデータ数は1多くなる。
        例えば1時間ごとの計算の場合、1年は8760ステップのため、瞬時値の数は8761になる。
        一方、平均値・積算値は、1/1 0:00～1:00（計算間隔が1時間の場合）といったように、ある瞬時時刻から次の瞬時時刻の間の値である。
        従って、データの数は計算ステップの数と一致する。
        例えば、1時間ごとの計算の場合、1年は8760ステップのため、平均値・積算値の数は8760になる。

        データ末尾について、
        -i とあるものは瞬時値を表す。
        -a とあるものは平均値・積算値を表す。
    """

    # 本負荷計算に年の概念は無いが、便宜上1989年として記録する。（閏年でなければ、任意）
    YEAR = '1989'

    def __init__(self, n_step_main: int, id_rm_is: List[int], id_bs_js: List[int], itv: Interval = Interval(eitv=EInterval.M15)):
        """
        ロギング用に numpy の配列を用意する。

        Args:
            n_step_main: 計算ステップの数
            id_rm_is: 室のid, [i]
            id_bs_js: 境界のid, [j]
            itv: インターバルクラス

        """

        # インターバル
        self._itv = itv

        # 室の数
        n_rm = len(id_rm_is)
        self._n_rm = n_rm

        # 境界の数
        n_bs = len(id_bs_js)
        self._n_bs = n_bs

        # 室のID
        self._id_rm_is = id_rm_is

        # 境界のID
        self._id_bs_js = id_bs_js

        # 瞬時値の行数
        self._n_step_i = n_step_main + 1

        # 平均・積算値の行数
        self._n_step_a = n_step_main

        # ---瞬時値---

        # 室に関するもの

        # ステップ n における外気温度, degree C, [n+1], 出力名："out_temp"
        self.theta_o_ns = np.empty(shape=self._n_step_i, dtype=float)

        # ステップ n における外気絶対湿度, kg/kg(DA), [n+1], 出力名："out_abs_humid"
        self.x_o_ns = np.empty(shape=self._n_step_i, dtype=float)

        # ステップ　n　における室　i　の室温, degree C, [i, n+1], 出力名："rm[i]_t_r"
        self.theta_r_is_ns = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップ n における室 i の相対湿度, %, [i, n+1], 出力名："rm[i]_rh_r"
        self.rh_r_is_ns = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップ n における室 i の絶対湿度, kg/kgDA, [i, n+1], 出力名："rm[i]_x_r"
        self.x_r_is_ns = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップ n における室 i の平均放射温度, degree C, [i, n+1], 出力名："rm[i]_mrt"
        self.theta_mrt_hum_is_ns = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップ n における室 i の作用温度, degree C, [i, n+1], 出力名："rm[i]_ot"
        self.theta_ot = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップ n における室 i の窓の透過日射熱取得, W, [i, n+1], 出力名："rm[i]_q_sol_t"
        self.q_trs_sol_is_ns = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップ n の室 i における家具の温度, degree C, [i, n+1], 出力名："rm[i]_t_fun"
        self.theta_frt_is_ns = np.empty((n_rm, self._n_step_i), dtype=float)

        # ステップ n の室 i における家具吸収日射熱量, W, [i, n+1], 出力名："rm[i]_q_s_sol_fun"
        self.q_sol_frt_is_ns = np.empty((n_rm, self._n_step_i), dtype=float)

        # ステップ n の室 i における家具の絶対湿度, kg/kgDA, [i, n+1], 出力名："rm[i]_x_fun"
        self.x_frt_is_ns = np.empty((n_rm, self._n_step_i), dtype=float)

        # ステップ n の室 i におけるPMV実現値, [i, n+1], 出力名："rm[i]_pmv"
        self.pmv_is_ns = np.empty((n_rm, self._n_step_i), dtype=float)

        # ステップ n の室 i におけるPPD実現値, [i, n+1], 出力名："rm[i]_ppd"
        self.ppd_is_ns = np.empty((n_rm, self._n_step_i), dtype=float)

        # 境界に関するもの

        # ステップ n の境界 j の室内側表面温度, degree C, [j, n+1], 出力名:"rm[i]_b[j]_t_s
        self.theta_s_js_ns = np.zeros((n_bs, self._n_step_i), dtype=float)

        # ステップ n の境界 j の等価温度, degree C, [j, n+1], 出力名:"rm[i]_b[j]_t_e
        self.theta_ei_js_ns = np.zeros((n_bs, self._n_step_i), dtype=float)

        # ステップ n の境界 j の裏面温度, degree C, [j, n+1], 出力名:"rm[i]_b[j]_t_b
        self.theta_rear_js_ns = np.zeros((n_bs, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面放射熱伝達率, W/m2K, [j, n+1], 出力名:"rm[i]_b[j]_hir_s
        self.h_s_r_js_ns = np.zeros((n_bs, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面放射熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qir_s
        self.q_r_js_ns = np.zeros((n_bs, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面対流熱伝達率, W/m2K, [j, n+1], 出力名:"rm[i]_b[j]_hic_s
        self.h_s_c_js_ns = np.zeros((n_bs, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面対流熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qic_s
        self.q_c_js_ns = np.zeros((n_bs, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面日射熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qisol_s
        self.q_i_sol_s_ns_js = np.zeros((n_bs, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面日射熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qiall_s
        self.q_s_js_ns = np.zeros((n_bs, self._n_step_i), dtype=float)

        # ステップ n の境界 j の係数cvl, degree C, [j, n+1], 出力名:"rm[i]_b[j]_cvl
        self.f_cvl_js_ns = np.zeros((n_bs, self._n_step_i), dtype=float)

        # ---積算値---

        # ステップ n における室 i の運転状態（平均値）, [i, n], 出力名："rm[i]_ac_operate"
        self.operation_mode_is_ns = np.empty(shape=(n_rm, self._n_step_a), dtype=object)

        # ステップ n における室 i の空調需要（平均値）, [i, n], 出力名："rm[i]_occupancy"
        self.ac_demand_is_ns = np.empty(shape=(n_rm, self._n_step_a), dtype=float)

        # ステップ n における室 i の人体周辺対流熱伝達率（平均値）, W/m2K, [i, n], 出力名："rm[i]_hc_hum"
        self.h_hum_c_is_ns = np.empty(shape=(n_rm, self._n_step_a), dtype=float)

        # ステップ n における室 i の人体放射熱伝達率（平均値）, W/m2K, [i, n], 出力名："rm[i]_hr_hum"
        self.h_hum_r_is_ns = np.empty(shape=(n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i における人体発熱を除く内部発熱, W, [i, n], 出力名："rm[i]_q_s_except_hum"
        self.q_gen_is_ns = np.empty(shape=(n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i における人体発湿を除く内部発湿, kg/s, [i, n], 出力名："rm[i]_q_l_except_hum"
        self.x_gen_is_ns = np.empty(shape=(n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i における人体発熱, W, [i, n], 出力名："rm[i]_q_hum_s"
        self.q_hum_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i における人体発湿, kg/s, [i, n], 出力名："rm[i]_q_hum_l"
        self.x_hum_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i における対流空調顕熱負荷, W, [i, n], 出力名："rm[i]_l_s_c"
        self.l_cs_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i における放射空調顕熱負荷, W, [i, n], 出力名："rm[i]_l_s_r"
        self.l_rs_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i における対流空調潜熱負荷（加湿側を正とする）, W, [i, n], 出力名："rm[i]_l_l_c"
        self.l_cl_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i における家具取得熱量, W, [i, n], 出力名："rm[i]_q_s_fun"
        self.q_frt_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i における家具取得水蒸気量, kg/s, [i, n], 出力名："rm[i]_q_l_fun"
        self.q_l_frt_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i におけるすきま風量, m3/s, [i, n], 出力名："rm[i]_v_reak"
        self.v_reak_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i における自然換気量, m3/s, [i, n], 出力名："rm[i]_v_ntrl"
        self.v_ntrl_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップ　n　の室　i　における人体廻りの風速, m/s, [i, n], 出力名："rm[i]_v_hum"
        self.v_hum_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップ n の室 i におけるClo値, [i, n], 出力名："rm[i]_clo"
        self.clo_is_ns = np.zeros((n_rm, self._n_step_a), dtype=float)

        self._output_list_room_a = [
            ('operation_mode_is_ns', 'ac_operate'),
            ('ac_demand_is_ns', 'occupancy'),
            ('h_hum_c_is_ns', 'hc_hum'),
            ('h_hum_r_is_ns', 'hr_hum'),
            ('q_gen_is_ns', 'q_s_except_hum'),
            ('x_gen_is_ns', 'q_l_except_hum'),
            ('q_hum_is_ns', 'q_hum_s'),
            ('x_hum_is_ns', 'q_hum_l'),
            ('l_cs_is_ns', 'l_s_c'),
            ('l_rs_is_ns', 'l_s_r'),
            ('l_cl_is_ns', 'l_l_c'),
            ('q_frt_is_ns', 'q_s_fun'),
            ('q_l_frt_is_ns', 'q_l_fun'),
            ('v_reak_is_ns', 'v_reak'),
            ('v_ntrl_is_ns', 'v_ntrl'),
            ('v_hum_is_ns', 'v_hum'),
            ('clo_is_ns', 'clo')
        ]

        self._output_list_room_i =[
            ('theta_r_is_ns', 't_r'),
            ('rh_r_is_ns', 'rh_r'),
            ('x_r_is_ns', 'x_r'),
            ('theta_mrt_hum_is_ns', 'mrt'),
            ('theta_ot', 'ot'),
            ('q_trs_sol_is_ns', 'q_sol_t'),
            ('theta_frt_is_ns', 't_fun'),
            ('q_sol_frt_is_ns', 'q_s_sol_fun'),
            ('x_frt_is_ns', 'x_fun'),
            ('pmv_is_ns', 'pmv'),
            ('ppd_is_ns', 'ppd')
        ]

        self._output_list_boundary_i = [
            ('theta_s_js_ns', 't_s'),
            ('theta_ei_js_ns', 't_e'),
            ('theta_rear_js_ns', 't_b'),
            ('h_s_r_js_ns', 'hir_s'),
            ('q_r_js_ns', 'qir_s'),
            ('h_s_c_js_ns', 'hic_s'),
            ('q_c_js_ns', 'qic_s'),
            ('q_i_sol_s_ns_js', 'qisol_s'),
            ('q_s_js_ns', 'qiall_s'),
            ('f_cvl_js_ns', 'f_cvl')
        ]

    def pre_recording(
            self,
            weather: Weather,
            scd: Schedule,
            bs: Boundaries,
            q_sol_frt_is_ns: np.ndarray,
            q_s_sol_js_ns: np.ndarray,
            q_trs_sol_is_ns: np.ndarray
    ):

        # 注意：用意された1年分のデータと実行期間が異なる場合があるためデータスライスする必要がある。

        # ---瞬時値---

        # ステップ n における外気温度, ℃, [n+1]
        self.theta_o_ns = weather.theta_o_ns_plus[0: self._n_step_i]

        # ステップ n における外気絶対湿度, kg/kg(DA), [n+1]
        self.x_o_ns = weather.x_o_ns_plus[0: self._n_step_i]

        # ステップ n における室 i の窓の透過日射熱取得, W, [i, n+1]
        self.q_trs_sol_is_ns = q_trs_sol_is_ns[:, 0:self._n_step_i]

        # ステップ n における室 i に設置された備品等による透過日射吸収熱量, W, [i, n+1]
        self.q_sol_frt_is_ns = q_sol_frt_is_ns[:, 0:self._n_step_i]

        # ステップ n の境界 j の表面日射熱流, W, [j, n+1]
        self.q_i_sol_s_ns_js = q_s_sol_js_ns[:, 0:self._n_step_i] * bs.a_s_js

        # ステップ n の境界 j の表面対流熱伝達率, W/m2K, [j, n+1]
        self.h_s_c_js_ns = bs.h_s_c_js.repeat(self._n_step_i, axis=1)

        # ステップ n の境界 j の表面放射熱伝達率, W/m2K, [j, n+1]
        self.h_s_r_js_ns = bs.h_s_r_js.repeat(self._n_step_i, axis=1)

        # ---平均値・積算値---

        # ステップ n の室 i における当該時刻の空調需要, [i, n_step_a]
        self.ac_demand_is_ns = scd.r_ac_demand_is_ns[:, 0:self._n_step_a]

        # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, n_step_a]
        self.q_gen_is_ns = scd.q_gen_is_ns[:, 0:self._n_step_a]

        # ステップ n の室 i における人体発湿を除く内部発湿, kg/s, [i, n_step_a]
        self.x_gen_is_ns = scd.x_gen_is_ns[:, 0:self._n_step_a]

    def post_recording(self, rms: Rooms, bs: Boundaries, f_mrt_is_js: np.ndarray, es: Equipments):

        # ---瞬時値---

        # ステップ n の室 i における飽和水蒸気圧, Pa, [i, n+1]
        p_vs_is_ns = psy.get_p_vs(theta=self.theta_r_is_ns)

        # ステップ n における室 i の水蒸気圧, Pa, [i, n+1]
        p_v_is_ns = psy.get_p_v_r_is_n(x_r_is_n=self.x_r_is_ns)

        # ステップnの室iにおける相対湿度, %, [i, n+1]
        self.rh_r_is_ns = psy.get_h(p_v=p_v_is_ns, p_vs=p_vs_is_ns)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち放射成分, W, [j, n]
        self.q_r_js_ns = bs.h_s_r_js * bs.a_s_js * (np.dot(np.dot(bs.p_js_is, f_mrt_is_js), self.theta_s_js_ns) - self.theta_s_js_ns)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち対流成分, W, [j, n+1]
        self.q_c_js_ns = bs.h_s_c_js * bs.a_s_js * (np.dot(bs.p_js_is, self.theta_r_is_ns) - self.theta_s_js_ns)

        # ---平均値・瞬時値---

        # ステップnの室iにおける家具取得熱量, W, [i, n]
        # ステップ n+1 の温度を用いてステップ n からステップ n+1 の平均的な熱流を求めている（後退差分）
        self.q_frt_is_ns = np.delete(rms.g_sh_frt_is * (self.theta_r_is_ns - self.theta_frt_is_ns), 0, axis=1)

        # ステップ n の室 i の家具等から空気への水分流, kg/s, [i, n]
        # ステップ n+1 の湿度を用いてステップ n からステップ n+1 の平均的な水分流を求めている（後退差分）
        self.q_l_frt_is_ns = np.delete(rms.g_lh_frt_is * (self.x_r_is_ns - self.x_frt_is_ns), 0, axis=1)

        self.clo_is_ns = operation_mode._get_clo_is_ns(operation_mode_is_n=self.operation_mode_is_ns)

        # ステップ n+1 のPMVを計算するのに、ステップ n からステップ n+1 のClo値を用いる。
        # 現在、Clo値の配列数が1つ多いバグがあるため、適切な長さになるようにスライスしている。
        # TODO: 本来であれば、助走期間における、n=-1 の時の値を用いないといけないが、とりあえず、配列最後の値を先頭に持ってきて代用している。
        clo_pls = np.append(self.clo_is_ns[:, -1:], self.clo_is_ns, axis=1)[:, 0:self._n_step_i]

        self.v_hum_is_ns = operation_mode._get_v_hum_is_n(
            operation_mode_is=self.operation_mode_is_ns,
            is_radiative_cooling_is=es.is_radiative_cooling_is,
            is_radiative_heating_is=es.is_radiative_heating_is
        )

        # ステップ n+1 のPMVを計算するのに、ステップ n からステップ n+1 の人体周りの風速を用いる。
        # TODO: 本来であれば、助走期間における、n=-1 の時の値を用いないといけないが、とりあえず、配列最後の値を先頭に持ってきて代用している。
        v_hum_pls = np.append(self.v_hum_is_ns[:, -1:], self.v_hum_is_ns, axis=1)

        # ---瞬時値---

        # ステップ n の室 i におけるPMV実現値, [i, n+1]
        self.pmv_is_ns = pmv.get_pmv_is_n(
            p_a_is_n=p_v_is_ns,
            theta_r_is_n=self.theta_r_is_ns,
            theta_mrt_is_n=self.theta_mrt_hum_is_ns,
            clo_is_n=clo_pls,
            v_hum_is_n=v_hum_pls,
            met_is=rms.met_is
        )

        # ステップ n の室 i におけるPPD実現値, [i, n+1]
        self.ppd_is_ns = pmv.get_ppd_is_n(pmv_is_n=self.pmv_is_ns)

    def recording(self, n: int, **kwargs):

        # 瞬時値の書き込み

        if n >= -1:

            # 瞬時値出力のステップ番号
            n_i = n + 1

            # 次の時刻に引き渡す値
            self.theta_r_is_ns[:, n_i] = kwargs["theta_r_is_n_pls"].flatten()
            self.theta_mrt_hum_is_ns[:, n_i] = kwargs["theta_mrt_hum_is_n_pls"].flatten()
            self.x_r_is_ns[:, n_i] = kwargs["x_r_is_n_pls"].flatten()
            self.theta_frt_is_ns[:, n_i] = kwargs["theta_frt_is_n_pls"].flatten()
            self.x_frt_is_ns[:, n_i] = kwargs["x_frt_is_n_pls"].flatten()
            self.theta_ei_js_ns[:, n_i] = kwargs["theta_ei_js_n_pls"].flatten()
            self.q_s_js_ns[:, n_i] = kwargs["q_s_js_n_pls"].flatten()

            # 次の時刻に引き渡さない値
            self.theta_ot[:, n_i] = kwargs["theta_ot_is_n_pls"].flatten()
            self.theta_s_js_ns[:, n_i] = kwargs["theta_s_js_n_pls"].flatten()
            self.theta_rear_js_ns[:, n_i] = kwargs["theta_rear_js_n"].flatten()
            self.f_cvl_js_ns[:, n_i] = kwargs["f_cvl_js_n_pls"].flatten()

        # 平均値・積算値の書き込み

        if n >= 0:

            # 平均値出力のステップ番号
            n_a = n

            # 次の時刻に引き渡す値
            self.operation_mode_is_ns[:, n_a] = kwargs["operation_mode_is_n"].flatten()

            # 次の時刻に引き渡さない値
            # 積算値
            self.l_cs_is_ns[:, n_a] = kwargs["l_cs_is_n"].flatten()
            self.l_rs_is_ns[:, n_a] = kwargs["l_rs_is_n"].flatten()
            self.l_cl_is_ns[:, n_a] = kwargs["l_cl_is_n"].flatten()
            # 平均値
            self.h_hum_c_is_ns[:, n_a] = kwargs["h_hum_c_is_n"].flatten()
            self.h_hum_r_is_ns[:, n_a] = kwargs["h_hum_r_is_n"].flatten()
            self.q_hum_is_ns[:, n_a] = kwargs["q_hum_is_n"].flatten()
            self.x_hum_is_ns[:, n_a] = kwargs["x_hum_is_n"].flatten()
            self.v_reak_is_ns[:, n_a] = kwargs["v_leak_is_n"].flatten()
            self.v_ntrl_is_ns[:, n_a] = kwargs["v_vent_ntr_is_n"].flatten()

    def export_pd(self):

        # データインデックス（「瞬時値・平均値用」・「積算値用（開始時刻）」・「積算値用（終了時刻）」）を作成する。
        date_index_a_end, date_index_a_start, date_index_i = self._get_date_index()

        # dataframe を作成（瞬時値・平均値用）
        df_a1 = pd.DataFrame(data=self._get_flat_data_a().T, columns=self.get_header_a(), index=[date_index_a_start, date_index_a_end])

        # 列入れ替え用の新しいヘッダーを作成
        new_columns_a = list(itertools.chain.from_iterable(
            [[self._get_room_header_name(id=i, name=column[1]) for column in self._output_list_room_a] for i in self._id_rm_is]
        ))

        # 列の入れ替え
        df_a2 = df_a1.reindex(columns=new_columns_a)

        # dataframe を作成（積算値用）
        df_i1 = pd.DataFrame(data=self._get_flat_data_i().T, columns=self.get_header_i(), index=date_index_i)

        # 列入れ替え用の新しいヘッダーを作成
        new_columns_i = ['out_temp', 'out_abs_humid'] + list(itertools.chain.from_iterable(
            [[self._get_room_header_name(id=id, name=column[1]) for column in self._output_list_room_i] for id in self._id_rm_is]
        )) + list(itertools.chain.from_iterable(
            [[self._get_boundary_name(id=id, name=column[1]) for column in self._output_list_boundary_i] for id in self._id_bs_js]
        ))

        # 列の入れ替え
        df_i2 = df_i1.reindex(columns=new_columns_i)

        return df_i2, df_a2

    def get_header_i(self):

        return ['out_temp', 'out_abs_humid'] \
            + list(itertools.chain.from_iterable(
                [self._get_room_header_names(name=column[1]) for column in self._output_list_room_i]))\
            + list(itertools.chain.from_iterable(
                [self._get_boundary_names(name=column[1]) for column in self._output_list_boundary_i]))

    def get_header_a(self):

        return list(itertools.chain.from_iterable(
            [self._get_room_header_names(name=column[1]) for column in self._output_list_room_a]))

    def _get_flat_data_i(self):
        """[列（項目数）✕行（時系列）]のデータを作成する。
        Returns:

        """

        # 出力リストに従って1つずつ記録された2次元のデータを縦に並べていき（この時点で3次元になる）、concatenate でフラット化する。
        # 先頭に外気温度と外気湿度の2つのデータを並べてある。他のデータが2次元データのため、
        # 外気温度と外気湿度のデータもあえて 1 ✕ n の2次元データにしてから統合してある。
        return np.concatenate(
            [[self.theta_o_ns], [self.x_o_ns]]
            + [self.__dict__[column[0]] for column in self._output_list_room_i]
            + [self.__dict__[column[0]] for column in self._output_list_boundary_i]
        )

    def _get_flat_data_a(self):
        """[列（項目数）✕行（時系列）]のデータを作成する。

        Returns:

        """

        # 出力リストに従って1つずつ記録された2次元のデータを縦に並べていき（この時点で3次元になる）、concatenate でフラット化する。
        return np.concatenate([self.__dict__[column[0]] for column in self._output_list_room_a])

    def _get_date_index(self):
        """データインデックスを作成する。

        Returns:

        """

        # pandas 用の時間間隔 freq 引数
        freq = self._itv.get_pandas_freq()

        # date time index 作成（瞬時値・平均値）
        date_index_i = pd.date_range(start='1/1/' + self.YEAR, periods=self._n_step_i, freq=freq, name='start_time')

        # date time index 作成（積算値）（start と end の2種類作成する）
        date_index_a_start = pd.date_range(start='1/1/' + self.YEAR, periods=self._n_step_a, freq=freq)
        date_index_a_end = date_index_a_start + dt.timedelta(minutes=15)
        date_index_a_start.name = 'start_time'
        date_index_a_end.name = 'end_time'

        return date_index_a_end, date_index_a_start, date_index_i

    @classmethod
    def _get_room_header_name(cls, id: int, name: str):
        """room 用のヘッダー名称を取得する。

        Args:
            id: room のID
            name: 出力項目名称

        Returns:
            ヘッダー名称
        """

        return 'rm' + str(id) + '_' + name

    def _get_room_header_names(self, name: str):
        """room 用のヘッダー名称を室の数分取得する。

        Args:
            name: 出力項目名称

        Returns:
            ヘッダー名称のリスト
        """
        return [self._get_room_header_name(id=id, name=name) for id in self._id_rm_is]

    @classmethod
    def _get_boundary_name(cls, id: int, name: str):
        """boundary 用のヘッダ名称を取得する。

        Args:
            id: boundary の ID
            name: 出力項目名称

        Returns:

        """

        return 'b' + str(id) + '_' + name

    def _get_boundary_names(self, name: str):
        """boundary 用のヘッダ名称を boundary の数だけ取得する。

        Args:
            name: 出力項目名称

        Returns:

        """
        return [self._get_boundary_name(id=id, name=name) for id in self._id_bs_js]

