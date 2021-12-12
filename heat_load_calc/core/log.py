import numpy as np
import pandas as pd
import datetime as dt

from heat_load_calc.core.pre_calc_parameters import PreCalcParameters
from heat_load_calc.external import psychrometrics as psy
from heat_load_calc.core import pmv as pmv
from heat_load_calc.core import ot_target_pmv as ot_target_pmv


class Logger:

    def __init__(self, n_rm: int, n_boundaries: int, n_step_main: int):

        self._n_step_main = n_step_main + 1
        self._n_step_i = n_step_main + 1
        self._n_step_a = n_step_main

        # ステップnにおける外気温度（瞬時値）, degree C, [n+1], 出力名："out_temp"
        self.theta_o_ns = np.empty(shape=self._n_step_i, dtype=float)

        # ステップnにおける外気絶対湿度（瞬時値）, kg/kg(DA), [n+1], 出力名："out_abs_humid"
        self.x_o_ns = np.empty(shape=self._n_step_i, dtype=float)

        # ステップnにおける室iの運転状態（平均値）, [i, n], 出力名："rm[i]_ac_operate"
        self.operation_mode = np.empty(shape=(n_rm, self._n_step_a), dtype=object)

        # ステップnにおける室iの空調需要（平均値）, [i, n], 出力名："rm[i]_occupancy"
        self.ac_demand_is_ns = np.empty(shape=(n_rm, self._n_step_a), dtype=float)

        # ステップnにおける室iの人体周辺対流熱伝達率（瞬時値）, W/m2K, [i, n], 出力名："rm[i]_hc_hum"
        self.h_hum_c_is_n = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップnにおける室iの人体放射熱伝達率（瞬時値）, W/m2K, [i, n], 出力名："rm[i]_hr_hum"
        self.h_hum_r_is_n = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップnにおける室iの室温（瞬時値）, degree C, [i, n], 出力名："rm[i]_t_r"
        self.theta_r = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップnにおける室iの相対湿度（瞬時値）, %, [i, n], 出力名："rm[i]_rh_r"
        self.rh = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップnにおける室iの絶対湿度（瞬時値）, kg/kgDA, [i, n], 出力名："rm[i]_x_r"
        self.x_r = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップnにおける室iの平均放射温度（瞬時値）, degree C, [i, n], 出力名："rm[i]_mrt"
        self.theta_mrt_hum = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップnにおける室iの作用温度（瞬時値）, degree C, [i, n], 出力名："rm[i]_ot"
        self.theta_ot = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

        # ステップnにおける室iの窓の透過日射熱取得（瞬時値）, W, [i, n], 出力名："rm[i]_q_sol_t"
        self.q_trs_sol_is_ns = np.empty(shape=(n_rm, self._n_step_i), dtype=float)

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

        # ステップnの室iにおける家具の温度, degree C, [i, n]
        self.theta_frt = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける家具取得熱量, W, [i, n]
        self.q_frt = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける家具吸収日射熱量, W, [i, n]
        self.q_sol_frt_is_ns = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける家具の絶対湿度, kg/kgDA, [i, n]
        self.x_frt = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける家具取得水蒸気量, kg/s, [i, n]
        self.q_l_frt = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおけるPMV目標値, [i, n]
        self.pmv_target = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおけるPMV実現値, [i, n]
        self.pmv = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおけるPPD実現値, [i, n]
        self.ppd = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおける人体廻りの風速, C, [i, n]
        self.v_hum = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの室iにおけるClo値, [i, n]
        self.clo = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの統合された境界j*の室内側表面温度, degree C, [j*, n]
        self.theta_s = np.zeros((n_boundaries, self._n_step_main), dtype=float)

        # ステップnの統合された境界j*の裏面温度, degree C, [j*, n]
        self.theta_rear = np.zeros((n_boundaries, self._n_step_main), dtype=float)

        # ステップnの統合された境界j*の表面放射熱流, W, [j*, n]
        self.qr = np.zeros((n_boundaries, self._n_step_main), dtype=float)

        # ステップnの統合された境界j*の表面対流熱流, W, [j*, n]
        self.qc = np.zeros((n_boundaries, self._n_step_main), dtype=float)

        # ステップnの統合された境界j*の等価温度, degree C, [j*, n]
        self.theta_ei = np.zeros((n_boundaries, self._n_step_main), dtype=float)

        # ステップnの統合された境界j*の表面日射熱流, W, [j*, n]
        self.qisol_s = np.zeros((n_boundaries, self._n_step_main), dtype=float)

        # ステップnの統合された境界j*の表面日射熱流, W, [j*, n]
        self.qiall_s = np.zeros((n_boundaries, self._n_step_main), dtype=float)

        # ステップnの統合された境界j*の表面対流熱伝達率, W/m2K, [j*, n]
        self.h_c_s = np.zeros((n_boundaries, self._n_step_main), dtype=float)

        # ステップnの統合された境界j*の表面放射熱伝達率, W/m2K, [j*, n]
        self.h_r_s = np.zeros((n_boundaries, self._n_step_main), dtype=float)

        # ステップnのすきま風量, m3/s, [i, n]
        self.v_reak_is_ns = np.zeros((n_rm, self._n_step_main), dtype=float)

        # ステップnの自然換気量, m3/s, [i, n]
        self.v_ntrl_is_ns = np.zeros((n_rm, self._n_step_main), dtype=float)

    def pre_logging(self, ss: PreCalcParameters):

        # ステップnにおける外気温度（瞬時値）, ℃, [n+1]
        self.theta_o_ns = ss.theta_o_ns[0:self._n_step_i]

        # ステップnにおける外気絶対湿度（瞬時値）, kg/kg(DA), [n+1]
        self.x_o_ns = ss.x_o_ns[0:self._n_step_i]

        # ステップnの室iにおける当該時刻の空調需要, [i, n]
        self.ac_demand_is_ns = ss.ac_demand_is_ns[:, 0:self._n_step_a]

        # n時点の瞬時値については、最前部に0番目をコピー
        # TODO: ここは修正する必要があると思われる。
        # 瞬時値の場合は、外気温度等と同様に、最後尾にインデックス0番をつけるべき。
        # ただし、test_at_once のテストが崩れるため慎重に対応しないといけない。
        # 加えて、応答係数に用いる瞬時値としての日射と、室の後退差分に用いる平均値としての日射とをプログラムで明確に区別すべきである。
        self.q_trs_sol_is_ns = np.append(np.zeros((ss.n_rm, 1)), ss.q_trs_sol_is_ns, axis=1)

        # nからn+1の平均値については最後尾に0番目をコピー
        self.q_gen_is_ns = np.append(ss.q_gen_is_ns, np.zeros((ss.n_rm, 1)), axis=1)

        # nからn+1の平均値については最後尾に0番目をコピー
        self.x_gen_is_ns = np.append(ss.x_gen_is_ns, np.zeros((ss.n_rm, 1)), axis=1)

        # n時点の瞬時値については、最前部に0番目をコピー
        self.q_sol_frt_is_ns = np.append(np.zeros((ss.n_rm, 1)), ss.q_sol_frt_is_ns, axis=1)

        qisol_s = ss.q_s_sol_js_ns * ss.a_s_js

        # n時点の瞬時値については、最前部に0番目をコピー
        self.qisol_s = np.append(np.zeros((ss.n_bdry, 1)), qisol_s, axis=1)

        self.h_c_s = ss.h_s_c_js.repeat(self._n_step_main + 1, axis=1)

        self.h_r_s = ss.h_s_r_js.repeat(self._n_step_main + 1, axis=1)

    def post_logging(self, ss: PreCalcParameters):

        # ステップnの室iにおける飽和水蒸気圧, Pa, [i, n]
        p_vs = psy.get_p_vs_is(theta_is=self.theta_r)

        # ステップnにおける室iの水蒸気圧, Pa, [i, n]
        p_v = psy.get_p_v_r_is_n(x_r_is_n=self.x_r)

        # ステップnの室iにおける相対湿度, %, [i, n]
        self.rh = psy.get_h(p_v=p_v, p_vs=p_vs)

        # ステップnの室iにおける家具取得熱量, W, [i, n]
        theta_r_is_ns = np.roll(self.theta_r, -1, axis=1)
        theta_frt_is_ns = np.roll(self.theta_frt, -1, axis=1)
        self.q_frt = ss.g_sh_frt_is * (theta_r_is_ns - theta_frt_is_ns)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち対流成分, W, [j, n]
        self.qc = ss.h_s_c_js * ss.a_s_js * (np.dot(ss.p_js_is, self.theta_r) - self.theta_s)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち放射成分, W, [j, n]
        self.qr = ss.h_s_r_js * ss.a_s_js * (np.dot(np.dot(ss.p_js_is, ss.f_mrt_is_js), self.theta_s) - self.theta_s)

        # ステップnの室iの家具等から空気への水分流, kg/s, [i, n]
        x_r_is_ns = np.roll(self.x_r, -1, axis=1)
        x_frt_is_ns = np.roll(self.x_frt, -1, axis=1)
        self.q_l_frt = ss.g_lh_frt_is * (x_r_is_ns - x_frt_is_ns)

    def record(self, pps: PreCalcParameters, output_data_dir: str, show_detail_result: bool):

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

            dd_a[name + '_ac_operate'] = self.operation_mode[i]
            dd_a[name + '_occupancy'] = self.ac_demand_is_ns[i]
            dd_i[name + '_hc_hum'] = self.h_hum_c_is_n[i]
            dd_i[name + '_hr_hum'] = self.h_hum_r_is_n[i]
            dd_i[name + '_t_r'] = self.theta_r[i]
            dd_i[name + '_rh_r'] = self.rh[i]
            dd_i[name + '_x_r'] = self.x_r[i]
            dd_i[name + '_mrt'] = self.theta_mrt_hum[i]
            dd_i[name + '_ot'] = self.theta_ot[i]
            dd_i[name + '_q_sol_t'] = self.q_trs_sol_is_ns[i][0:n_step_i]
            dd_a[name + '_q_s_except_hum'] = self.q_gen_is_ns[i][0:n_step_a]
            dd_a[name + '_q_l_except_hum'] = self.x_gen_is_ns[i][0:n_step_a]
            dd_a[name + '_q_hum_s'] = self.q_hum[i][0:n_step_a]
            dd_a[name + '_q_hum_l'] = self.x_hum[i][0:n_step_a]
            dd_a[name + '_l_s_c'] = self.l_cs[i][0:n_step_a]
            dd_a[name + '_l_s_r'] = self.l_rs[i][0:n_step_a]
            dd_a[name + '_l_l_c'] = self.l_cl[i][0:n_step_a]
            dd_i[name + '_t_fun'] = self.theta_frt[i][0:n_step_i]
            dd_a[name + '_q_s_fun'] = self.q_frt[i][0:n_step_a]
            dd_i[name + '_q_s_sol_fun'] = self.q_sol_frt_is_ns[i][0:n_step_i]
            dd_i[name + '_x_fun'] = self.x_frt[i][0:n_step_i]
            dd_a[name + '_q_l_fun'] = self.q_l_frt[i][0:n_step_a]
            dd_a[name + '_v_reak'] = self.v_reak_is_ns[i][0:n_step_a]
            dd_a[name + '_v_ntrl'] = self.v_ntrl_is_ns[i][0:n_step_a]
            dd_i[name + '_pmv_target'] = self.pmv_target[i][0:n_step_i]
            dd_i[name + '_pmv'] = self.pmv[i][0:n_step_i]
            dd_i[name + '_ppd'] = self.ppd[i][0:n_step_i]
            dd_i[name + '_v_hum'] = self.v_hum[i][0:n_step_i]
            dd_a[name + '_clo'] = self.clo[i][0:n_step_a]

            selected = pps.p_is_js[i] == 1

            for j, t in enumerate(self.theta_s[selected, 0:n_step_i]):
                dd_i[name + '_' + 'b' + str(j) + '_t_s'] = t
            for j, t in enumerate(self.theta_ei[selected, 0:n_step_i]):
                dd_i[name + '_' + 'b' + str(j) + '_t_e'] = t
            for j, t in enumerate(self.theta_rear[selected, 0:n_step_i]):
                dd_i[name + '_' + 'b' + str(j) + '_t_b'] = t
            for j, t in enumerate(self.h_r_s[selected, 0:n_step_i]):
                dd_i[name + '_' + 'b' + str(j) + '_hir_s'] = t
            for j, t in enumerate(self.qr[selected, 0:n_step_i]):
                dd_i[name + '_' + 'b' + str(j) + '_qir_s'] = t
            for j, t in enumerate(self.h_c_s[selected, 0:n_step_i]):
                dd_i[name + '_' + 'b' + str(j) + '_hic_s'] = t
            for j, t in enumerate(self.qc[selected, 0:n_step_i]):
                dd_i[name + '_' + 'b' + str(j) + '_qic_s'] = t
            for j, t in enumerate(self.qisol_s[selected, 0:n_step_i]):
                dd_i[name + '_' + 'b' + str(j) + '_qisol_s'] = t
            for j, t in enumerate(self.qiall_s[selected, 0:n_step_i]):
                dd_i[name + '_' + 'b' + str(j) + '_qiall_s'] = t

        if show_detail_result:
            dd_i.to_csv(output_data_dir + '/result_detail_i.csv', encoding='cp932')
            dd_a.to_csv(output_data_dir + '/result_detail_a.csv', encoding='cp932')

        return dd_i, dd_a
