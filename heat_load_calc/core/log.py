import numpy as np
import pandas as pd

from heat_load_calc.core.pre_calc_parameters import PreCalcParameters
from heat_load_calc.external import psychrometrics as psy


class Logger:

    def __init__(self, n_spaces: int, n_bdries: int):

        # ステップnの室iにおける運転状態, [i, n]
        self.operation_mode = np.empty((n_spaces, 24 * 365 * 4 * 3), dtype=object)

        # ステップnの室iにおける当該時刻の空調需要, [i, n]
        self.ac_demand = None

        # ステップnの室iにおける室温, degree C, [i, n]
        self.theta_r = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける相対湿度, %, [i, n]
        self.rh = None

        # ステップnの室iにおける絶対湿度, kg/kgDA, [i, n]
        self.x_r = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける平均放射温度, degree C, [i, n]
        self.theta_mrt = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける作用温度, degree C, [i, n]
        self.theta_ot = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおけるClo値, [i, n]
        self.clo = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける窓の透過日射熱取得, W, [i, n]
        self.q_trs_sol = None

        # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, n]
        self.q_gen = None

        # ステップnの室iにおける人体発湿を除く内部発湿, kg/s, [i, n]
        self.x_gen = None

        # ステップnの室iにおける人体発熱, W, [i, n]
        self.q_hum = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける人体発湿, kg/s, [i, n]
        self.x_hum = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける対流空調顕熱負荷, W, [i, n]
        self.l_cs = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける放射空調顕熱負荷, W, [i, n]
        self.l_rs = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける対流空調潜熱負荷（加湿側を正とする）, W, [i, n]
        self.l_cl = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける家具の温度, degree C, [i, n]
        self.theta_frnt = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける家具取得熱量, W, [i, n]
        self.q_frnt = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける家具吸収日射熱量, W, [i, n]
        self.q_sol_frnt = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける家具の絶対湿度, kg/kgDA, [i, n]
        self.x_frnt = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける家具取得水蒸気量, kg/s, [i, n]
        self.q_l_frnt = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの統合された境界j*の室内側表面温度, degree C, [j*, n]
        self.theta_s = np.zeros((n_bdries, 24 * 365 * 4 * 3))

        # ステップnの統合された境界j*の室内等価室温, degree C, [j*, n]
#        self.theta_e = np.zeros((n_bdrys, 24 * 365 * 4 * 3))

        # ステップnの統合された境界j*の裏面温度, degree C, [j*, n]
        self.theta_rear = np.zeros((n_bdries, 24 * 365 * 4 * 3))

        # ステップnの統合された境界j*の表面放射熱流, W, [j*, n]
        self.qr = np.zeros((n_bdries, 24 * 365 * 4 * 3))

        # ステップnの統合された境界j*の表面対流熱流, W, [j*, n]
        self.qc = np.zeros((n_bdries, 24 * 365 * 4 * 3))

        # ステップnの統合された境界j*の等価温度, degree C, [j*, n]
        self.theta_ei = np.zeros((n_bdries, 24 * 365 * 4 * 3))

    def pre_logging(self, ss: PreCalcParameters):

        self.theta_o = ss.theta_o_ns
        self.x_o = ss.x_o_ns
        self.ac_demand = ss.ac_demand_is_ns
        self.q_trs_sol = ss.q_trs_sol_is_ns
        self.q_gen = ss.q_gen_is_ns
        self.x_gen = ss.x_gen_is_ns
        self.q_sol_frnt = ss.q_sol_frnt_is_ns

    def post_logging(self, ss: PreCalcParameters):

        # ステップnの室iにおける飽和水蒸気圧, Pa, [i, n]
        p_vs = psy.get_p_vs_is(theta_is=self.theta_r)

        # ステップnにおける室iの水蒸気圧, Pa, [i, n]
        p_v = psy.get_p_v_r_is_n(x_r_is_n=self.x_r)

        # ステップnの室iにおける相対湿度, %, [i, n]
        self.rh = psy.get_h(p_v=p_v, p_vs=p_vs)

        # ステップnの室iにおける家具取得熱量, W, [i, n]
        self.q_frnt = ss.c_h_frt_is * (self.theta_r - self.theta_frnt)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち対流成分, W, [j, n]
        self.qc = ss.h_c_js * ss.a_srf_js * (np.dot(ss.p_js_is, self.theta_r) - self.theta_s)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち放射成分, W, [j, n]
        self.qr = ss.h_r_js * ss.a_srf_js * (np.dot(np.dot(ss.p_js_is, ss.f_mrt_is_js), self.theta_s) - self.theta_s)

        # ステップnの室iの家具等から空気への水分流, kg/s, [i, n]
        self.q_l_frnt = ss.c_w_frt_is * (self.x_r - self.x_frnt)


def record(pps: PreCalcParameters, logger: Logger, output_data_dir: str, show_simple_result: bool, show_detail_result: bool):

    date_index_15min = pd.date_range(start='1/1/1989', periods=365*96, freq='15min')

    dd = pd.DataFrame(index=date_index_15min)

    dd['out_temp'] = logger.theta_o
    dd['out_abs_humid'] = logger.x_o

    for i in range(pps.n_spaces):

        name = pps.space_name_is[i]

        dd[name + '_ac_operate'] = logger.operation_mode[i][0:365*96]
        dd[name + '_occupancy'] = logger.ac_demand[i][0:365*96]
        dd[name + '_t_r'] = logger.theta_r[i][0:365*96]
        dd[name + '_rh_r'] = logger.rh[i][0:365*96]
        dd[name + '_x_r'] = logger.x_r[i][0:365*96]
        dd[name + '_mrt'] = logger.theta_mrt[i][0:365*96]
        dd[name + '_ot'] = logger.theta_ot[i][0:365*96]
        dd[name + '_clo'] = logger.clo[i][0:365*96]
        dd[name + '_q_sol_t'] = logger.q_trs_sol[i][0:365*96]
        dd[name + '_q_s_except_hum'] = logger.q_gen[i][0:365*96]
        dd[name + '_q_l_except_hum'] = logger.x_gen[i][0:365*96]
        dd[name + '_q_hum_s'] = logger.q_hum[i][0:365*96]
        dd[name + '_q_hum_l'] = logger.x_hum[i][0:365*96]
        dd[name + '_l_s_c'] = logger.l_cs[i][0:365*96]
        dd[name + '_l_s_r'] = logger.l_rs[i][0:365*96]
        dd[name + '_l_l_c'] = logger.l_cl[i][0:365*96]
        dd[name + '_t_fun'] = logger.theta_frnt[i][0:365*96]
        dd[name + '_q_s_fun'] = logger.q_frnt[i][0:365*96]
        dd[name + '_q_s_sol_fin'] = logger.q_sol_frnt[i][0:365*96]
        dd[name + '_x_fun'] = logger.x_frnt[i][0:365*96]
        dd[name + '_q_l_fun'] = logger.q_l_frnt[i][0:365*96]

        selected = pps.p_is_js[i] == 1
        boundary_names = pps.name_bdry_js[selected]

        for j, t in enumerate(logger.theta_s[selected, :]):
            dd[name + '_' + boundary_names[j] + '_t_s'] = t[0:365*96]
        for j, t in enumerate(logger.theta_ei[selected, :]):
            dd[name + '_' + boundary_names[j] + '_t_e'] = t[0:365*96]
        for j, t in enumerate(logger.theta_rear[selected, :]):
            dd[name + '_' + boundary_names[j] + '_t_b'] = t[0:365*96]
        for j, t in enumerate(logger.qr[selected, :]):
            dd[name + '_' + boundary_names[j] + '_qir_s'] = t[0:365*96]
        for j, t in enumerate(logger.qc[selected, :]):
            dd[name + '_' + boundary_names[j] + '_qic_s'] = t[0:365*96]

    if show_detail_result:
        dd.to_csv(output_data_dir + '/result_detail.csv', encoding='cp932')

    date_index_1h = pd.date_range(start='1/1/1989', periods=365*24, freq='H')

    ds = pd.DataFrame(index=date_index_1h)

    ds['out_temp'] = dd['out_temp'].resample('H').mean().round(2)
    ds['out_abs_humid'] = dd['out_abs_humid'].resample('H').mean().round(2)

    for i in range(pps.n_spaces):

        name = pps.space_name_is[i]

        ds[name + '_ac_operate'] = dd[name + '_ac_operate'].asfreq('H')
        ds[name + '_t_r'] = dd[name + '_t_r'].resample('H').mean().round(2)
        ds[name + '_x_r'] = dd[name + '_x_r'].resample('H').mean().round(4)
        ds[name + '_ot'] = dd[name + '_ot'].resample('H').mean().round(2)
        ds[name + '_l_s_c'] = dd[name + '_l_s_c'].resample('H').sum().round(0)
        ds[name + '_l_s_r'] = dd[name + '_l_s_r'].resample('H').sum().round(0)
        ds[name + '_l_l_c'] = dd[name + '_l_l_c'].resample('H').sum().round(0)

    if show_simple_result:
        ds.to_csv(output_data_dir + '/result_digest.csv', encoding='cp932')

    return ds, dd
