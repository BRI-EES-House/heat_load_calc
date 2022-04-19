import numpy as np
import pandas as pd
import datetime as dt

from heat_load_calc.core.pre_calc_parameters import PreCalcParameters
from heat_load_calc.external import psychrometrics as psy
from heat_load_calc.core import pmv as pmv
from heat_load_calc.core import ot_target_pmv as ot_target_pmv


class Logger:
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

    def __init__(self, n_rm: int, n_boundaries: int, n_step_main: int):
        """
        ロギング用に numpy の配列を用意する。

        Args:
            n_rm: 室の数
            n_boundaries: 境界の数
            n_step_main: 計算ステップの数

        """

        self._n_step_main = n_step_main + 1
        self._n_step_i = n_step_main + 1
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
        self.theta_s = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の等価温度, degree C, [j, n+1], 出力名:"rm[i]_b[j]_t_e
        self.theta_ei = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の裏面温度, degree C, [j, n+1], 出力名:"rm[i]_b[j]_t_b
        self.theta_rear = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面放射熱伝達率, W/m2K, [j, n+1], 出力名:"rm[i]_b[j]_hir_s
        self.h_r_s = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面放射熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qir_s
        self.qr = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面対流熱伝達率, W/m2K, [j, n+1], 出力名:"rm[i]_b[j]_hic_s
        self.h_c_s = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面対流熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qic_s
        self.qc = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面日射熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qisol_s
        self.qisol_s = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面日射熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qiall_s
        self.qiall_s = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ---積算値---

        # ステップ n における室 i の運転状態（平均値）, [i, n], 出力名："rm[i]_ac_operate"
        self.operation_mode = np.empty(shape=(n_rm, self._n_step_a), dtype=object)

        # ステップ n における室 i の空調需要（平均値）, [i, n], 出力名："rm[i]_occupancy"
        self.ac_demand_is_ns = np.empty(shape=(n_rm, self._n_step_a), dtype=float)

        # ステップ n における室 i の人体周辺対流熱伝達率（平均値）, W/m2K, [i, n], 出力名："rm[i]_hc_hum"
        self.h_hum_c_is_n = np.empty(shape=(n_rm, self._n_step_a), dtype=float)

        # ステップ n における室 i の人体放射熱伝達率（平均値）, W/m2K, [i, n], 出力名："rm[i]_hr_hum"
        self.h_hum_r_is_n = np.empty(shape=(n_rm, self._n_step_a), dtype=float)




        # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, n]
        self.q_gen_is_ns = None

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, n]
        self.x_gen_is_ns = None

        # ステップnの室iにおける人体発熱, W, [i, n]
        self.q_hum = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける人体発湿, kg/s, [i, n]
        self.x_hum = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける対流空調顕熱負荷, W, [i, n]
        self.l_cs = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける放射空調顕熱負荷, W, [i, n]
        self.l_rs = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける対流空調潜熱負荷（加湿側を正とする）, W, [i, n]
        self.l_cl = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける家具取得熱量, W, [i, n]
        self.q_frt = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップnの室iにおける家具取得水蒸気量, kg/s, [i, n]
        self.q_l_frt = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnのすきま風量, m3/s, [i, n]
        self.v_reak_is_ns = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの自然換気量, m3/s, [i, n]
        self.v_ntrl_is_ns = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける人体廻りの風速, C, [i, n]
        self.v_hum = np.zeros((n_rm, self._n_step_a), dtype=float)

        # ステップnの室iにおけるClo値, [i, n]
        self.clo = np.zeros((n_rm, self._n_step_main), dtype=float)

    def pre_logging(self, ss: PreCalcParameters):

        # ステップ n における外気温度, ℃, [n+1]
        # 注意：用意された1年分のデータと実行期間が異なる場合があるためデータスライスする必要がある。
        self.theta_o_ns = ss.theta_o_ns[0: self._n_step_i]

        # ステップ n における外気絶対湿度, kg/kg(DA), [n+1]
        # 注意：用意された1年分のデータと実行期間が異なる場合があるためデータスライスする必要がある。
        self.x_o_ns = ss.x_o_ns[0: self._n_step_i]

        # ステップ n における室 i の窓の透過日射熱取得, W, [i, n+1]
        self.q_trs_sol_is_ns = ss.q_trs_sol_is_ns[:, 0:self._n_step_i]

        # ステップ n における室 i に設置された備品等による透過日射吸収熱量, W, [i, n+1]
        self.q_sol_frt_is_ns = ss.q_sol_frt_is_ns[:, 0:self._n_step_i]

        # ステップ n の境界 j の表面日射熱流, W, [j, n+1]
        self.qisol_s = ss.q_s_sol_js_ns[:, 0:self._n_step_i] * ss.a_s_js

        # ステップ n の境界 j の表面対流熱伝達率, W/m2K, [j, n+1]
        self.h_c_s = ss.h_s_c_js.repeat(self._n_step_i, axis=1)

        # ステップ n の境界 j の表面放射熱伝達率, W/m2K, [j, n+1]
        self.h_r_s = ss.h_s_r_js.repeat(self._n_step_i, axis=1)



        # ステップnの室iにおける当該時刻の空調需要, [i, n]
        self.ac_demand_is_ns = ss.ac_demand_is_ns[:, 0:self._n_step_a]

        # nからn+1の平均値については最後尾に0番目をコピー
        self.q_gen_is_ns = np.append(ss.q_gen_is_ns, np.zeros((ss.n_rm, 1)), axis=1)

        # nからn+1の平均値については最後尾に0番目をコピー
        self.x_gen_is_ns = np.append(ss.x_gen_is_ns, np.zeros((ss.n_rm, 1)), axis=1)

    def post_logging(self, ss: PreCalcParameters):

        # ステップ n の室 i における飽和水蒸気圧, Pa, [i, n+1]
        p_vs_is_ns = psy.get_p_vs_is(theta_is=self.theta_r_is_ns)

        # ステップ n における室 i の水蒸気圧, Pa, [i, n+1]
        p_v_is_ns = psy.get_p_v_r_is_n(x_r_is_n=self.x_r_is_ns)

        # ステップnの室iにおける相対湿度, %, [i, n+1]
        self.rh_r_is_ns = psy.get_h(p_v=p_v_is_ns, p_vs=p_vs_is_ns)

        # ステップnの室iにおける家具取得熱量, W, [i, n]
        # ステップ n+1 の温度を用いてステップ n からステップ n+1 の平均的な熱流を求めている（後退差分）
        self.q_frt = np.delete(ss.g_sh_frt_is * (self.theta_r_is_ns - self.theta_frt_is_ns), 0, axis=1)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち対流成分, W, [j, n+1]
        self.qc = ss.h_s_c_js * ss.a_s_js * (np.dot(ss.p_js_is, self.theta_r_is_ns) - self.theta_s)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち放射成分, W, [j, n]
        self.qr = ss.h_s_r_js * ss.a_s_js * (np.dot(np.dot(ss.p_js_is, ss.f_mrt_is_js), self.theta_s) - self.theta_s)

        # ステップ n の室 i の家具等から空気への水分流, kg/s, [i, n]
        # ステップ n+1 の湿度を用いてステップ n からステップ n+1 の平均的な水分流を求めている（後退差分）
        self.q_l_frt = np.delete(ss.g_lh_frt_is * (self.x_r_is_ns - self.x_frt_is_ns), 0, axis=1)

        # ステップ n+1 のPMVを計算するのに、ステップ n からステップ n+1 のClo値を用いる。
        # 現在、Clo値の配列数が1つ多いバグがあるため、適切な長さになるようにスライスしている。
        # TODO: 本来であれば、助走期間における、n=-1 の時の値を用いないといけないが、とりあえず、配列最後の値を先頭に持ってきて代用している。
        clo_pls = np.append(self.clo[:, -1:], self.clo, axis=1)[:, 0:self._n_step_i]
        # ステップ n+1 のPMVを計算するのに、ステップ n からステップ n+1 の人体周りの風速を用いる。
        # TODO: 本来であれば、助走期間における、n=-1 の時の値を用いないといけないが、とりあえず、配列最後の値を先頭に持ってきて代用している。
        v_hum_pls = np.append(self.v_hum[:, -1:], self.v_hum, axis=1)

        self.pmv_is_ns = pmv.get_pmv_is_n(
            p_a_is_n=p_v_is_ns,
            theta_r_is_n=self.theta_r_is_ns,
            theta_mrt_is_n=self.theta_mrt_hum_is_ns,
            clo_is_n=clo_pls,
            v_hum_is_n=v_hum_pls,
            met_is=ss.met_is
        )

        self.ppd_is_ns = pmv.get_ppd_is_n(pmv_is_n=self.pmv_is_ns)

    def record(self, pps: PreCalcParameters):

        n_step_i = self._n_step_i
        n_step_a = self._n_step_a

        date_index_15min_i = pd.date_range(start='1/1/1989', periods=n_step_i, freq='15min', name='start_time')
        date_index_15min_a = pd.date_range(start='1/1/1989', periods=n_step_a, freq='15min', name='start_time')

        dd_i = pd.DataFrame(index=date_index_15min_i)
        dd_a = pd.DataFrame(index=date_index_15min_a)
        dd_a['end_time'] = date_index_15min_a + dt.timedelta(minutes=15)

        dd_i['out_temp'] = self.theta_o_ns
        dd_i['out_abs_humid'] = self.x_o_ns

        for i in range(pps.n_rm):

            name = 'rm' + str(i)

            dd_i[name + '_t_r'] = self.theta_r_is_ns[i]
            dd_i[name + '_rh_r'] = self.rh_r_is_ns[i]
            dd_i[name + '_x_r'] = self.x_r_is_ns[i]
            dd_i[name + '_mrt'] = self.theta_mrt_hum_is_ns[i]
            dd_i[name + '_ot'] = self.theta_ot[i]
            dd_i[name + '_q_sol_t'] = self.q_trs_sol_is_ns[i]
            dd_i[name + '_t_fun'] = self.theta_frt_is_ns[i]
            dd_i[name + '_q_s_sol_fun'] = self.q_sol_frt_is_ns[i]
            dd_i[name + '_x_fun'] = self.x_frt_is_ns[i]
            dd_i[name + '_pmv'] = self.pmv_is_ns[i]
            dd_i[name + '_ppd'] = self.ppd_is_ns[i]

            dd_a[name + '_ac_operate'] = self.operation_mode[i]
            dd_a[name + '_occupancy'] = self.ac_demand_is_ns[i]
            dd_a[name + '_hc_hum'] = self.h_hum_c_is_n[i]
            dd_a[name + '_hr_hum'] = self.h_hum_r_is_n[i]
            dd_a[name + '_q_s_except_hum'] = self.q_gen_is_ns[i][0:n_step_a]
            dd_a[name + '_q_l_except_hum'] = self.x_gen_is_ns[i][0:n_step_a]
            dd_a[name + '_q_hum_s'] = self.q_hum[i][0:n_step_a]
            dd_a[name + '_q_hum_l'] = self.x_hum[i][0:n_step_a]
            dd_a[name + '_l_s_c'] = self.l_cs[i][0:n_step_a]
            dd_a[name + '_l_s_r'] = self.l_rs[i][0:n_step_a]
            dd_a[name + '_l_l_c'] = self.l_cl[i][0:n_step_a]
            dd_a[name + '_q_s_fun'] = self.q_frt[i][0:n_step_a]
            dd_a[name + '_q_l_fun'] = self.q_l_frt[i][0:n_step_a]
            dd_a[name + '_v_reak'] = self.v_reak_is_ns[i][0:n_step_a]
            dd_a[name + '_v_ntrl'] = self.v_ntrl_is_ns[i][0:n_step_a]
            dd_a[name + '_v_hum'] = self.v_hum[i][0:n_step_a]
            dd_a[name + '_clo'] = self.clo[i][0:n_step_a]

            selected = pps.p_is_js[i] == 1

            for j, t in enumerate(self.theta_s[selected, :]):
                dd_i[name + '_' + 'b' + str(j) + '_t_s'] = t
            for j, t in enumerate(self.theta_ei[selected, :]):
                dd_i[name + '_' + 'b' + str(j) + '_t_e'] = t
            for j, t in enumerate(self.theta_rear[selected, :]):
                dd_i[name + '_' + 'b' + str(j) + '_t_b'] = t
            for j, t in enumerate(self.h_r_s[selected, :]):
                dd_i[name + '_' + 'b' + str(j) + '_hir_s'] = t
            for j, t in enumerate(self.qr[selected, :]):
                dd_i[name + '_' + 'b' + str(j) + '_qir_s'] = t
            for j, t in enumerate(self.h_c_s[selected, :]):
                dd_i[name + '_' + 'b' + str(j) + '_hic_s'] = t
            for j, t in enumerate(self.qc[selected, :]):
                dd_i[name + '_' + 'b' + str(j) + '_qic_s'] = t
            for j, t in enumerate(self.qisol_s[selected, :]):
                dd_i[name + '_' + 'b' + str(j) + '_qisol_s'] = t
            for j, t in enumerate(self.qiall_s[selected, :]):
                dd_i[name + '_' + 'b' + str(j) + '_qiall_s'] = t

        return dd_i, dd_a
