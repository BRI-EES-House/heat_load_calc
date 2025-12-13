import pandas as pd
import logging
from typing import Tuple, Dict

from heat_load_calc import schedule, recorder, sequence, weather, period, \
    conditions, interval

logger = logging.getLogger('HeatLoadCalc').getChild('core')


def calc(
        d: Dict,
        entry_point_dir: str
    ) -> Tuple[pd.DataFrame, pd.DataFrame, sequence.Boundaries, schedule.Schedule, weather.Weather]:
    """core main program

    Args:
        d: input data as dictionary / 住宅計算条件
        entry_point_dir: the pass of the entry point directory

    Returns:
        以下のタプル
            (1) 計算結果（詳細版）をいれたDataFrame
            (2) 計算結果（簡易版）をいれたDataFrame
            (3)
            (4) schedule

    Notes:
        「助走計算のうち建物全体を解く日数」は「助走計算を行う日数」で指定した値以下でないといけない。
    """

    # Check the existance of the item "common" in the input file.
    if 'common' not in d:
        raise KeyError('Key common could not be found in the input file.')
    
    d_common = d['common']

    # Set inteval class depending on the item 'interval' in common tag.
    # If not specified in the file, 15 minute interval is set as default.   
    itv: interval.Interval = interval.set_interval(d_common=d_common)

    # Make Weather class.
    w: weather.Weather = weather.Weather.make_weather(
        d_common=d_common,
        itv=itv,
        entry_point_dir=entry_point_dir
    )

    # Make Schedule class.
    scd: schedule.Schedule = schedule.Schedule.get_schedule(
        number_of_occupants='auto',
        a_f_is=[r['floor_area'] for r in d['rooms']],
        itv=itv,
        scd_is=[r['schedule'] for r in d['rooms']]
    )

    # number of steps for main calculation
    # number of steps for run-up calculation
    # number of steps to calculate building in run-up calculation
    n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(d_common=d_common, itv=itv)

    # json, csv ファイルからパラメータをロードする。
    # （ループ計算する必要の無い）事前計算を行い, クラス PreCalcParameters, PreCalcParametersGround に必要な変数を格納する。
    sqc = sequence.Sequence(itv=itv, rd=d, weather=w, scd=scd)

    gc_n = conditions.initialize_ground_conditions(n_grounds=sqc.bs.n_ground)

    logger.info('助走計算（土壌のみ）')

    for n in range(-n_step_run_up, -n_step_run_up_build):
        gc_n = sqc.run_tick_ground(gc_n=gc_n, n=n)

    result = recorder.Recorder(
        n_step_main=n_step_main,
        id_rm_is=list(sqc.rms.id_r_is.flatten()),
        id_bs_js=list(sqc.bs.id_js.flatten())
    )

    result.pre_recording(
        weather=sqc.weather,
        scd=sqc.scd,
        bs=sqc.bs,
        q_sol_frt_is_ns=sqc.q_sol_frt_is_ns,
        q_s_sol_js_ns=sqc.q_s_sol_js_ns,
        q_trs_sol_is_ns=sqc.q_trs_sol_is_ns
    )

    # 建物を計算するにあたって初期値を与える
    c_n = conditions.initialize_conditions(n_spaces=sqc.rms.n_r, n_bdries=sqc.bs.n_b)

    # 地盤計算の結果（項別公比法の指数項mの吸熱応答の項別成分・表面熱流）を建物の計算に引き継ぐ
    c_n = conditions.update_conditions_by_ground_conditions(
        is_ground=sqc.bs.b_ground_js.flatten(),
        c=c_n,
        gc=gc_n
    )

    logger.info('助走計算（建物全体）')

    for n in range(-n_step_run_up_build, 0):
        c_n = sqc.run_tick(n=n, c_n=c_n, recorder=result)

    logger.info('本計算')

    # TODO: recorder に1/1 0:00の瞬時状態値を書き込む
    m = 1

    for n in range(0, n_step_main):

        c_n = sqc.run_tick(n=n, c_n=c_n, recorder=result)

        if n == int(n_step_main / 12 * m):
            logger.info("{} / 12 calculated.".format(m))
            m = m + 1

    result.post_recording(rms=sqc.rms, bs=sqc.bs, f_mrt_is_js=sqc.f_mrt_is_js, es=sqc.es)

    logger.info('ログ作成')

    # dd: data detail, 15分間隔のすべてのパラメータ pd.DataFrame
    dd_i, dd_a = result.export_pd()

    return dd_i, dd_a, sqc.bs, scd, w
