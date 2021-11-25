import numpy as np
import pandas as pd
import datetime as dt

from heat_load_calc.core.pre_calc_parameters import PreCalcParameters
from heat_load_calc.external import psychrometrics as psy
from heat_load_calc.core import pmv as pmv
from heat_load_calc.core import ot_target_pmv as ot_target_pmv


class Logger:

    def __init__(self, n_spaces: int, n_boundaries: int, n_step_main: int):

        self._n_step_main = n_step_main + 1

        # ステップnの室iにおける運転状態, [i, n]
        self.operation_mode = np.empty((n_spaces, self._n_step_main), dtype=object)

        # ステップnの室iにおける当該時刻の空調需要, [i, n]
        self.ac_demand_is_ns = None

        # ステップnの室iにおける室温, degree C, [i, n]
        self.theta_r = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける相対湿度, %, [i, n]
        self.rh = None

        # ステップnの室iにおける絶対湿度, kg/kgDA, [i, n]
        self.x_r = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける平均放射温度, degree C, [i, n]
        self.theta_mrt_hum = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける作用温度, degree C, [i, n]
        self.theta_ot = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける人体周辺対流熱伝達率, W/m2K, [i, n]
        self.h_hum_c_is_n = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける人体放射熱伝達率, W/m2K, [i, n]
        self.h_hum_r_is_n = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける窓の透過日射熱取得, W, [i, n]
        self.q_trs_sol_is_ns = None

        # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, n]
        self.q_gen_is_ns = None

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, n]
        self.x_gen_is_ns = None

        # ステップnの室iにおける人体発熱, W, [i, n]
        self.q_hum = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける人体発湿, kg/s, [i, n]
        self.x_hum = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける対流空調顕熱負荷, W, [i, n]
        self.l_cs = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける放射空調顕熱負荷, W, [i, n]
        self.l_rs = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける対流空調潜熱負荷（加湿側を正とする）, W, [i, n]
        self.l_cl = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける家具の温度, degree C, [i, n]
        self.theta_frt = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける家具取得熱量, W, [i, n]
        self.q_frt = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける家具吸収日射熱量, W, [i, n]
        self.q_sol_frt_is_ns = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける家具の絶対湿度, kg/kgDA, [i, n]
        self.x_frt = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける家具取得水蒸気量, kg/s, [i, n]
        self.q_l_frt = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおけるPMV目標値, [i, n]
        self.pmv_target = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおけるPMV実現値, [i, n]
        self.pmv = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおけるPPD実現値, [i, n]
        self.ppd = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおける人体廻りの風速, C, [i, n]
        self.v_hum = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの室iにおけるClo値, [i, n]
        self.clo = np.zeros((n_spaces, self._n_step_main), dtype=float)

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
        self.v_reak_is_ns = np.zeros((n_spaces, self._n_step_main), dtype=float)

        # ステップnの自然換気量, m3/s, [i, n]
        self.v_ntrl_is_ns = np.zeros((n_spaces, self._n_step_main), dtype=float)

    def pre_logging(self, ss: PreCalcParameters):

        self.theta_o_ns = ss.theta_o_ns
        self.x_o_ns = ss.x_o_ns
        self.ac_demand_is_ns = np.append(ss.ac_demand_is_ns, np.zeros((ss.n_rm, 1)), axis=1)
        self.q_trs_sol_is_ns = np.append(ss.q_trs_sol_is_ns, np.zeros((ss.n_rm, 1)), axis=1)
        self.q_gen_is_ns = np.append(ss.q_gen_is_ns, np.zeros((ss.n_rm, 1)), axis=1)
        self.x_gen_is_ns = np.append(ss.x_gen_is_ns, np.zeros((ss.n_rm, 1)), axis=1)
        self.q_sol_frt_is_ns = np.append(ss.q_sol_frt_is_ns, np.zeros((ss.n_rm, 1)), axis=1)

        qisol_s = ss.q_s_sol_js_ns * ss.a_s_js
        self.qisol_s = np.append(qisol_s, np.zeros((ss.n_bdry, 1)), axis=1)
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
        self.q_frt = ss.g_sh_frt_is * (self.theta_r - self.theta_frt)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち対流成分, W, [j, n]
        self.qc = ss.h_s_c_js * ss.a_s_js * (np.dot(ss.p_js_is, self.theta_r) - self.theta_s)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち放射成分, W, [j, n]
        self.qr = ss.h_s_r_js * ss.a_s_js * (np.dot(np.dot(ss.p_js_is, ss.f_mrt_is_js), self.theta_s) - self.theta_s)

        # ステップnの室iの家具等から空気への水分流, kg/s, [i, n]
        self.q_l_frt = ss.g_lh_frt_is * (self.x_r - self.x_frt)


def record(pps: PreCalcParameters, logger: Logger, output_data_dir: str, show_detail_result: bool, n_step_main: int, n_d_main: int):

    n_step_main_i = n_step_main + 1
    n_step_main_a = n_step_main + 1

    date_index_15min_i = pd.date_range(start='1/1/1989', periods=n_step_main+1, freq='15min')
    date_index_15min_a = pd.date_range(start='1/1/1989', periods=n_step_main+1, freq='15min')

    dd_i = pd.DataFrame(index=date_index_15min_i)
    dd_a = pd.DataFrame(index=date_index_15min_a)
    dd_a['end_time'] = date_index_15min_a + dt.timedelta(minutes=15)

    dd_i['out_temp'] = logger.theta_o_ns[0:n_step_main_i]
    dd_i['out_abs_humid'] = logger.x_o_ns[0:n_step_main_i]


    for i in range(pps.n_rm):

        name = 'rm' + str(i)

        dd_a[name + '_ac_operate'] = logger.operation_mode[i][0:n_step_main_a]
        dd_a[name + '_occupancy'] = logger.ac_demand_is_ns[i][0:n_step_main_a]
        dd_i[name + '_hc_hum'] = logger.h_hum_c_is_n[i][0:n_step_main_i]
        dd_i[name + '_hr_hum'] = logger.h_hum_r_is_n[i][0:n_step_main_i]
        dd_i[name + '_t_r'] = logger.theta_r[i][0:n_step_main_i]
        dd_i[name + '_rh_r'] = logger.rh[i][0:n_step_main_i]
        dd_i[name + '_x_r'] = logger.x_r[i][0:n_step_main_i]
        dd_i[name + '_mrt'] = logger.theta_mrt_hum[i][0:n_step_main_i]
        dd_i[name + '_ot'] = logger.theta_ot[i][0:n_step_main_i]
        dd_i[name + '_q_sol_t'] = logger.q_trs_sol_is_ns[i][0:n_step_main_i]
        dd_a[name + '_q_s_except_hum'] = logger.q_gen_is_ns[i][0:n_step_main_a]
        dd_a[name + '_q_l_except_hum'] = logger.x_gen_is_ns[i][0:n_step_main_a]
        dd_a[name + '_q_hum_s'] = logger.q_hum[i][0:n_step_main_a]
        dd_a[name + '_q_hum_l'] = logger.x_hum[i][0:n_step_main_a]
        dd_a[name + '_l_s_c'] = logger.l_cs[i][0:n_step_main_a]
        dd_a[name + '_l_s_r'] = logger.l_rs[i][0:n_step_main_a]
        dd_a[name + '_l_l_c'] = logger.l_cl[i][0:n_step_main_a]
        dd_i[name + '_t_fun'] = logger.theta_frt[i][0:n_step_main_i]
        dd_a[name + '_q_s_fun'] = logger.q_frt[i][0:n_step_main_a]
        dd_i[name + '_q_s_sol_fun'] = logger.q_sol_frt_is_ns[i][0:n_step_main_i]
        dd_i[name + '_x_fun'] = logger.x_frt[i][0:n_step_main_i]
        dd_a[name + '_q_l_fun'] = logger.q_l_frt[i][0:n_step_main_a]
        dd_i[name + '_v_reak'] = logger.v_reak_is_ns[i][0:n_step_main_i]
        dd_i[name + '_v_ntrl'] = logger.v_ntrl_is_ns[i][0:n_step_main_i]
        dd_i[name + '_pmv_target'] = logger.pmv_target[i][0:n_step_main_i]
        dd_i[name + '_pmv'] = logger.pmv[i][0:n_step_main_i]
        dd_i[name + '_ppd'] = logger.ppd[i][0:n_step_main_i]
        dd_i[name + '_v_hum'] = logger.v_hum[i][0:n_step_main_i]
        dd_a[name + '_clo'] = logger.clo[i][0:n_step_main_i]

        selected = pps.p_is_js[i] == 1
        boundary_names = pps.name_bdry_js[selected]

        for j, t in enumerate(logger.theta_s[selected, 0:n_step_main_i]):
            dd_i[name + '_' + 'b' + str(j) + '_t_s'] = t
        for j, t in enumerate(logger.theta_ei[selected, 0:n_step_main_i]):
            dd_i[name + '_' + 'b' + str(j) + '_t_e'] = t
        for j, t in enumerate(logger.theta_rear[selected, 0:n_step_main_i]):
            dd_i[name + '_' + 'b' + str(j) + '_t_b'] = t
        for j, t in enumerate(logger.h_r_s[selected, 0:n_step_main_i]):
            dd_i[name + '_' + 'b' + str(j) + '_hir_s'] = t
        for j, t in enumerate(logger.qr[selected, 0:n_step_main_i]):
            dd_i[name + '_' + 'b' + str(j) + '_qir_s'] = t
        for j, t in enumerate(logger.h_c_s[selected, 0:n_step_main_i]):
            dd_i[name + '_' + 'b' + str(j) + '_hic_s'] = t
        for j, t in enumerate(logger.qc[selected, 0:n_step_main_i]):
            dd_i[name + '_' + 'b' + str(j) + '_qic_s'] = t
        for j, t in enumerate(logger.qisol_s[selected, 0:n_step_main_i]):
            dd_i[name + '_' + 'b' + str(j) + '_qisol_s'] = t
        for j, t in enumerate(logger.qiall_s[selected, 0:n_step_main_i]):
            dd_i[name + '_' + 'b' + str(j) + '_qiall_s'] = t

    if show_detail_result:
        dd_i.to_csv(output_data_dir + '/result_detail_i.csv', encoding='cp932')
        dd_a.to_csv(output_data_dir + '/result_detail_a.csv', encoding='cp932')

    return dd_i, dd_a
