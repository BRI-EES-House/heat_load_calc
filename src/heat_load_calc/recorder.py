import numpy as np
import pandas as pd
import datetime as dt
import itertools

from heat_load_calc.pre_calc_parameters import PreCalcParameters
from heat_load_calc import pmv as pmv, psychrometrics as psy


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

    def __init__(self, n_rm: int, n_boundaries: int, n_step_main: int):
        """
        ロギング用に numpy の配列を用意する。

        Args:
            n_rm: 室の数
            n_boundaries: 境界の数
            n_step_main: 計算ステップの数

        """

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
        self.theta_s_js_ns = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の等価温度, degree C, [j, n+1], 出力名:"rm[i]_b[j]_t_e
        self.theta_ei_js_ns = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の裏面温度, degree C, [j, n+1], 出力名:"rm[i]_b[j]_t_b
        self.theta_rear_js_ns = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面放射熱伝達率, W/m2K, [j, n+1], 出力名:"rm[i]_b[j]_hir_s
        self.h_s_r_js_ns = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面放射熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qir_s
        self.q_r_js_ns = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面対流熱伝達率, W/m2K, [j, n+1], 出力名:"rm[i]_b[j]_hic_s
        self.h_s_c_js_ns = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面対流熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qic_s
        self.q_c_js_ns = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面日射熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qisol_s
        self.q_i_sol_s_ns_js = np.zeros((n_boundaries, self._n_step_i), dtype=float)

        # ステップ n の境界 j の表面日射熱流, W, [j, n+1], 出力名:"rm[i]_b[j]_qiall_s
        self.q_s_js_ns = np.zeros((n_boundaries, self._n_step_i), dtype=float)

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

    def pre_recording(self, ss: PreCalcParameters):

        # 注意：用意された1年分のデータと実行期間が異なる場合があるためデータスライスする必要がある。

        # ---瞬時値---

        # ステップ n における外気温度, ℃, [n+1]
        self.theta_o_ns = ss.theta_o_ns[0: self._n_step_i]

        # ステップ n における外気絶対湿度, kg/kg(DA), [n+1]
        self.x_o_ns = ss.x_o_ns[0: self._n_step_i]

        # ステップ n における室 i の窓の透過日射熱取得, W, [i, n+1]
        self.q_trs_sol_is_ns = ss.q_trs_sol_is_ns[:, 0:self._n_step_i]

        # ステップ n における室 i に設置された備品等による透過日射吸収熱量, W, [i, n+1]
        self.q_sol_frt_is_ns = ss.q_sol_frt_is_ns[:, 0:self._n_step_i]

        # ステップ n の境界 j の表面日射熱流, W, [j, n+1]
        self.q_i_sol_s_ns_js = ss.q_s_sol_js_ns[:, 0:self._n_step_i] * ss.a_s_js

        # ステップ n の境界 j の表面対流熱伝達率, W/m2K, [j, n+1]
        self.h_s_c_js_ns = ss.h_s_c_js.repeat(self._n_step_i, axis=1)

        # ステップ n の境界 j の表面放射熱伝達率, W/m2K, [j, n+1]
        self.h_s_r_js_ns = ss.h_s_r_js.repeat(self._n_step_i, axis=1)

        # ---平均値・積算値---

        # ステップ n の室 i における当該時刻の空調需要, [i, n]
        self.ac_demand_is_ns = ss.ac_demand_is_ns[:, 0:self._n_step_a]

        # ステップnの室iにおける人体発熱を除く内部発熱, W, [i, 8760*4]
        self.q_gen_is_ns = ss.q_gen_is_ns[:, 0:self._n_step_a]

        # ステップ n の室 i における人体発湿を除く内部発湿, kg/s, [i, n]
        self.x_gen_is_ns = ss.x_gen_is_ns[:, 0:self._n_step_a]

    def post_recording(self, ss: PreCalcParameters):

        # ---瞬時値---

        # ステップ n の室 i における飽和水蒸気圧, Pa, [i, n+1]
        p_vs_is_ns = psy.get_p_vs(theta=self.theta_r_is_ns)

        # ステップ n における室 i の水蒸気圧, Pa, [i, n+1]
        p_v_is_ns = psy.get_p_v_r_is_n(x_r_is_n=self.x_r_is_ns)

        # ステップnの室iにおける相対湿度, %, [i, n+1]
        self.rh_r_is_ns = psy.get_h(p_v=p_v_is_ns, p_vs=p_vs_is_ns)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち放射成分, W, [j, n]
        self.q_r_js_ns = ss.h_s_r_js * ss.a_s_js * (np.dot(np.dot(ss.p_js_is, ss.f_mrt_is_js), self.theta_s_js_ns) - self.theta_s_js_ns)

        # ステップnの境界jにおける表面熱流（壁体吸熱を正とする）のうち対流成分, W, [j, n+1]
        self.q_c_js_ns = ss.h_s_c_js * ss.a_s_js * (np.dot(ss.p_js_is, self.theta_r_is_ns) - self.theta_s_js_ns)

        # ---平均値・瞬時値---

        # ステップnの室iにおける家具取得熱量, W, [i, n]
        # ステップ n+1 の温度を用いてステップ n からステップ n+1 の平均的な熱流を求めている（後退差分）
        self.q_frt_is_ns = np.delete(ss.g_sh_frt_is * (self.theta_r_is_ns - self.theta_frt_is_ns), 0, axis=1)

        # ステップ n の室 i の家具等から空気への水分流, kg/s, [i, n]
        # ステップ n+1 の湿度を用いてステップ n からステップ n+1 の平均的な水分流を求めている（後退差分）
        self.q_l_frt_is_ns = np.delete(ss.g_lh_frt_is * (self.x_r_is_ns - self.x_frt_is_ns), 0, axis=1)

        # ステップ n+1 のPMVを計算するのに、ステップ n からステップ n+1 のClo値を用いる。
        # 現在、Clo値の配列数が1つ多いバグがあるため、適切な長さになるようにスライスしている。
        # TODO: 本来であれば、助走期間における、n=-1 の時の値を用いないといけないが、とりあえず、配列最後の値を先頭に持ってきて代用している。
        clo_pls = np.append(self.clo_is_ns[:, -1:], self.clo_is_ns, axis=1)[:, 0:self._n_step_i]
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
            met_is=ss.met_is
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
            self.v_hum_is_ns[:, n_a] = kwargs["v_hum_is_n"].flatten()
            self.clo_is_ns[:, n_a] = kwargs["clo_is_n"].flatten()

    def export_pd(self, pps: PreCalcParameters):

        n_step_i = self._n_step_i
        n_step_a = self._n_step_a

        date_index_15min_i = pd.date_range(start='1/1/1989', periods=n_step_i, freq='15min', name='start_time')

        date_index_15min_a_start = pd.date_range(start='1/1/1989', periods=n_step_a, freq='15min')
        date_index_15min_a_end = date_index_15min_a_start + dt.timedelta(minutes=15)
        date_index_15min_a_start.name = 'start_time'
        date_index_15min_a_end.name = 'end_time'

        df_i = pd.DataFrame(index=date_index_15min_i)

        df_i['out_temp'] = self.theta_o_ns
        df_i['out_abs_humid'] = self.x_o_ns

        def get_room_name(i: int, name: str):
            return 'rm' + str(i) + '_' + name

        def get_room_names(name: str):
            return [get_room_name(i=i, name=name) for i in range(pps.n_rm)]

        def get_boundary_name(j: int, name: str):
            rm_index = np.where(pps.p_js_is[j] == 1)[0][0]
            return 'rm' + str(rm_index) + '_b' + str(j) + '_' + name

        def get_boundary_names(name: str):
            return [get_boundary_name(j=j, name=name) for j in range(pps.n_bdry)]

        output_list_room_a = [
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

        df_a1 = pd.DataFrame(
            data=np.concatenate([self.__dict__[column[0]] for column in output_list_room_a]).T,
            columns=list(itertools.chain.from_iterable([get_room_names(name=column[1]) for column in output_list_room_a])),
            index=[date_index_15min_a_start, date_index_15min_a_end]
        )

        new_columns_a = list(itertools.chain.from_iterable(
            [[get_room_name(i=i, name=column[1]) for column in output_list_room_a] for i in range(pps.n_rm)]
        ))

        df_a2 = df_a1.reindex(columns=new_columns_a)

        output_list_room_i =[
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

        output_list_boundary_i = [
            ('theta_s_js_ns', 't_s'),
            ('theta_ei_js_ns', 't_e'),
            ('theta_rear_js_ns', 't_b'),
            ('h_s_r_js_ns', 'hir_s'),
            ('q_r_js_ns', 'qir_s'),
            ('h_s_c_js_ns', 'hic_s'),
            ('q_c_js_ns', 'qic_s'),
            ('q_i_sol_s_ns_js', 'qisol_s'),
            ('q_s_js_ns', 'qiall_s')
        ]

        df_i1 = pd.DataFrame(
            data=np.concatenate(
                [[self.theta_o_ns], [self.x_o_ns]]
                + [self.__dict__[column[0]] for column in output_list_room_i]
                + [self.__dict__[column[0]] for column in output_list_boundary_i]
            ).T,
            columns=['out_temp', 'out_abs_humid']
                + list(itertools.chain.from_iterable([get_room_names(name=column[1]) for column in output_list_room_i]))
                + list(itertools.chain.from_iterable([get_boundary_names(name=column[1]) for column in output_list_boundary_i])),
            index=date_index_15min_i
        )

        new_columns_i = ['out_temp', 'out_abs_humid'] + list(itertools.chain.from_iterable(
            [[get_room_name(i=i, name=column[1]) for column in output_list_room_i] for i in range(pps.n_rm)]
        )) + list(itertools.chain.from_iterable(
            [[get_boundary_name(j=j, name=column[1]) for column in output_list_boundary_i] for j in range(pps.n_bdry)]
        ))

        df_i2 = df_i1.reindex(columns=new_columns_i)

        return df_i2, df_a2
