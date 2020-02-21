import datetime
from typing import List
import numpy as np

from s3_space_loader import Space
from s3_space_loader import Logger
from s3_space_loader import Spaces

import Psychrometrics as psy


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

        # ステップnの室iにおける着衣温度, degree C, [i, n]
        self.v_hum = np.zeros((n_spaces, 24 * 365 * 4 * 3))

        # ステップnの室iにおける窓の透過日射熱取得, W, [8760*4]
        self.q_trs_sol = None

    def pre_logging(self, ss: Spaces):

        self.ac_demand = ss.ac_demand_is_n
        self.q_trs_sol = ss.q_trs_sol_is_ns

    def post_logging(self, ss: Spaces):

        # ステップnの室iにおける飽和水蒸気圧, Pa, [i, n]
        p_vs = psy.get_p_vs_is(theta_is=self.theta_r)

        # ステップn+1の室iにおける水蒸気圧, Pa, [i, n]
        p_v = psy.get_p_v_r(x_r_is_n=self.x_r)

        # ステップn+1の室iにおける相対湿度, %
        self.rh = psy.get_h(p_v=p_v, p_vs=p_vs)


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
        headder1.append(name + "_風速[m/s]")
        headder1.append(name + "_透過日射熱取得[W]")
        headder1.append(name + "_機器顕熱発熱[W]")
        headder1.append(name + "_照明発熱[W]")
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


def append_tick_log(spaces: List[Space], log: List[List], To_n: float, n: int, xo_n: float, logger2: Logger2):

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
        row.append('{0:.2f}'.format(logger2.v_hum[i, n]))
        row.append('{0:.2f}'.format(logger2.q_trs_sol[i, n]))

#        row.append('{0:.2f}'.format(space.logger.q_trs_sol_i_ns[n]))
        row.append('{0:.2f}'.format(space.logger.heat_generation_appliances_schedule[n]))
        row.append('{0:.2f}'.format(space.logger.heat_generation_lighting_schedule[n]))
        row.append('{0:.2f}'.format(space.logger.q_hum_i_ns[n]))
        row.append('{0:.2f}'.format(space.logger.x_hum_i_ns[n]))
        row.append('{0:.1f}'.format(space.logger.Lcs_i_n[n]))
        row.append('{0:.1f}'.format(space.logger.Lrs_i_n[n]))
        row.append('{0:.1f}'.format(space.logger.Lcl_i_n[n]))
        row.append('{0:.2f}'.format(space.logger.theta_frnt_i_ns[n]))
        row.append('{0:.1f}'.format(space.logger.Qfuns_i_n[n]))
        row.append('{0:.1f}'.format(space.logger.q_sol_frnt_i_ns[n]))
        row.append('{0:.5f}'.format(space.logger.xf_i_n[n]))
        row.append('{0:.5f}'.format(space.logger.Qfunl_i_n[n]))
        n = space.n_bnd_i_jstrs
        for g in range(n):
            row.append('{0:.2f}'.format(space.logger.Ts_i_k_n[g, n]))
        for g in range(n):
            row.append('{0:.2f}'.format(space.logger.Tei_i_k_n[g, n]))
        for g in range(n):
            row.append('{0:.2f}'.format(space.logger.theta_rear_i_jstrs_ns[g,n]))
        for g in range(n):
            row.append('{0:.2f}'.format(space.logger.Qr[g, n]))
        for g in range(n):
            row.append('{0:.2f}'.format(space.logger.Qc[g, n]))
    log.append(row)
