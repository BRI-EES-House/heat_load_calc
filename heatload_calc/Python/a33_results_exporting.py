import datetime
from typing import List
import numpy as np

from s3_space_loader import Space
from s3_space_loader import Spaces
import s4_1_sensible_heat as s41

import psychrometrics as psy


class Logger2:

    def __init__(self, n_spaces: int, n_bdrys: int):

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
        self.theta_s = np.zeros((n_bdrys, 24 * 365 * 4 * 3))

        # ステップnの統合された境界j*の室内等価室温, degree C, [j*, n]
        self.theta_e = np.zeros((n_bdrys, 24 * 365 * 4 * 3))

        # ステップnの統合された境界j*の裏面温度, degree C, [j*, n]
        self.theta_rear = np.zeros((n_bdrys, 24 * 365 * 4 * 3))

        # ステップnの統合された境界j*の表面放射熱流, W, [j*, n]
        self.qr = np.zeros((n_bdrys, 24 * 365 * 4 * 3))

        # ステップnの統合された境界j*の表面対流熱流, W, [j*, n]
        self.qc = np.zeros((n_bdrys, 24 * 365 * 4 * 3))

    def pre_logging(self, ss: Spaces):

        self.ac_demand = ss.ac_demand_is_n
        self.q_trs_sol = ss.q_trs_sol_is_ns
        self.q_gen = ss.q_gen_is_ns
        self.x_gen = ss.x_gen_is_ns
        self.q_sol_frnt = ss.q_sol_frnt_is_ns

    def post_logging(self, ss: Spaces):

        # ステップnの室iにおける飽和水蒸気圧, Pa, [i, n]
        p_vs = psy.get_p_vs_is(theta_is=self.theta_r)

        # ステップnにおける室iの水蒸気圧, Pa, [i, n]
        p_v = psy.get_p_v_r_is_n(x_r_is_n=self.x_r)

        # ステップnの室iにおける相対湿度, %, [i, n]
        self.rh = psy.get_h(p_v=p_v, p_vs=p_vs)

        # ステップnの室iにおける家具取得熱量, W, [i, n]
        self.q_frnt = s41.get_Qfuns(ss.c_fun_is, self.theta_r, self.theta_frnt)


def append_headers(spaces: List[Space]) -> List[List]:

    headder1 = []

    headder1.append('日時')

    headder1.append('外気温度[℃]')

    headder1.append('外気絶対湿度[kg/kg(DA)]')

    for space in spaces:
        name = space.name_i
        headder1.append(name + "_運転状態")
        headder1.append(name + "_在室状況")
        headder1.append(name + "_空気温度[℃]")
        headder1.append(name + "_室相対湿度[%]")
        headder1.append(name + "_室絶対湿度[kg/kg(DA)]")
        headder1.append(name + "_室MRT[℃]")
        headder1.append(name + "_室作用温度[℃]")
        headder1.append(name + "_着衣量[clo]")
        headder1.append(name + "_透過日射熱取得[W]")
        headder1.append(name + "_人体発熱を除く内部発熱[W]")
        headder1.append(name + "_人体発湿を除く内部発湿[kg/s]")
        headder1.append(name + "_人体顕熱発熱[W]")
        headder1.append(name + "_人体潜熱発熱[W]")
        headder1.append(name + "_対流空調顕熱負荷[W]")
        headder1.append(name + "_放射空調顕熱負荷[W]")
        headder1.append(name + "_対流空調潜熱負荷[W]")
        headder1.append(name + "_家具温度[℃]")
        headder1.append(name + "_家具取得熱量[W]")
        headder1.append(name + "_家具吸収日射熱量[W]")
        headder1.append(name + "_家具絶対湿度[kg/kg(DA)]")
        headder1.append(name + "_家具取得水蒸気量[kg/s]")
        n = space.n_bnd_i_jstrs
        if 1:
            for g in range(n):
                headder1.append(name + "_" + space.name_bdry_i_jstrs[g] + "_表面温度[℃]")
        if 1:
            for g in range(n):
                headder1.append(name + "_" + space.name_bdry_i_jstrs[g] + "_等価室温[℃]")
        if 1:
            for g in range(n):
                headder1.append(name + "_" + space.name_bdry_i_jstrs[g] + "_境界温度[℃]")
        if 1:
            for g in range(n):
                headder1.append(name + "_" + space.name_bdry_i_jstrs[g] + "_表面放射熱流[W]")
        if 1:
            for g in range(n):
                headder1.append(name + "_" + space.name_bdry_i_jstrs[g] + "_表面対流熱流[W]")

    # 出力リスト
    OutList = []

    OutList.append(headder1)

    return OutList


def append_tick_log(
        spaces: List[Space],
        log: List[List],
        To_n: float,
        n: int,
        xo_n: float,
        logger2: Logger2,
        start_indices
):

    # DTMは1989年1月1日始まりとする
    start_date = datetime.datetime(1989, 1, 1)

    # 1/1 0:00 からの時間　単位はday
    delta_day = float(n) / float(96)

    # 1/1 0:00 からの時刻, datetime 型
    dtm = start_date + datetime.timedelta(days=delta_day)

    row = [
        str(dtm),
        '{0:.1f}'.format(To_n[n]),
        '{0:.4f}'.format(xo_n[n])
    ]

    for i, space in enumerate(spaces):
        row.append(logger2.operation_mode[i, n])
        row.append(logger2.ac_demand[i, n])
        row.append('{0:.2f}'.format(logger2.theta_r[i, n]))
        row.append('{0:.0f}'.format(logger2.rh[i, n]))
        row.append('{0:.4f}'.format(logger2.x_r[i, n]))
        row.append('{0:.2f}'.format(logger2.theta_mrt[i, n]))
        row.append('{0:.2f}'.format(logger2.theta_ot[i, n]))
        row.append('{0:.2f}'.format(logger2.clo[i, n]))
        row.append('{0:.2f}'.format(logger2.q_trs_sol[i, n]))
        row.append('{0:.2f}'.format(logger2.q_gen[i, n]))
        row.append('{0:.2f}'.format(logger2.x_gen[i, n]))
        row.append('{0:.2f}'.format(logger2.q_hum[i, n]))
        row.append('{0:.2f}'.format(logger2.x_hum[i, n]))
        row.append('{0:.1f}'.format(logger2.l_cs[i, n]))
        row.append('{0:.1f}'.format(logger2.l_rs[i, n]))
        row.append('{0:.1f}'.format(logger2.l_cl[i, n]))
        row.append('{0:.2f}'.format(logger2.theta_frnt[i, n]))
        row.append('{0:.1f}'.format(logger2.q_frnt[i, n]))
        row.append('{0:.1f}'.format(logger2.q_sol_frnt[i, n]))
        row.append('{0:.5f}'.format(logger2.x_frnt[i, n]))
        row.append('{0:.5f}'.format(logger2.q_l_frnt[i, n]))

        for t in np.split(logger2.theta_s, start_indices)[i]:
            row.append('{0:.2f}'.format(t[n]))

        j = space.n_bnd_i_jstrs

        for g in range(j):
            row.append('{0:.2f}'.format(space.logger.Tei_i_k_n[g, n]))

        for t in np.split(logger2.theta_rear, start_indices)[i]:
            row.append('{0:.2f}'.format(t[n]))

        for t in np.split(logger2.qr, start_indices)[i]:
            row.append('{0:.2f}'.format(t[n]))
#        for g in range(j):
#            row.append('{0:.2f}'.format(space.logger.Qr[g, n]))

        for t in np.split(logger2.qc, start_indices)[i]:
            row.append('{0:.2f}'.format(t[n]))
#        for g in range(j):
#            row.append('{0:.2f}'.format(space.logger.Qc[g, n]))

    log.append(row)
