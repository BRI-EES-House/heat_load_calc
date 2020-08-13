from typing import Dict

from heat_load_calc.core import period
from heat_load_calc.core import pre_calc_parameters
from heat_load_calc.core import conditions
from heat_load_calc.core import log
from heat_load_calc.core import sequence
from heat_load_calc.core import sequence_ground
from heat_load_calc.core.pre_calc_parameters import PreCalcParameters, PreCalcParametersGround


def calc(
        input_data_dir: str,
        output_data_dir: str = None,
        show_simple_result: bool = False,
        show_detail_result: bool = False,
        n_step_hourly: int = 4,
        n_d_main: int = 365,
        n_d_run_up: int = 365,
        n_d_run_up_build: int = 183
) -> (Dict, Dict):
    """coreメインプログラム

    Args:
        input_data_dir: 計算条件を記したファイルがあるディレクトリ（相対パスで指定）
        output_data_dir: 計算結果を出力するディレクトリ（相対パスで指定）
        show_simple_result: 簡易計算結果をファイル出力するか否か（指定しない場合はFalse=出力しない）
        show_detail_result: 詳細計算結果をファイル出力するか否か（指定しない場合はFalse=出力しない）
        n_step_hourly: 計算間隔（1時間を何分割するかどうか）（デフォルトは4（15分間隔））
        n_d_main: 本計算を行う日数（デフォルトは365日（1年間））, d
        n_d_run_up: 助走計算を行う日数（デフォルトは365日（1年間））, d
        n_d_run_up_build: 助走計算のうち建物全体を解く日数（デフォルトは183日（およそ半年））, d

    Returns:
        以下のタプル
            (1) 計算結果（簡易版）をいれたDataFrame
            (2) 計算結果（詳細版）をいれたDataFrame

    Notes:
        「助走計算のうち建物全体を解く日数」は「助走計算を行う日数」で指定した値以下でないといけない。
    """

    # 本計算のステップ数
    # 助走計算のステップ数
    # 助走計算のうち建物全体を解くステップ数
    n_step_main, n_step_run_up, n_step_run_up_build = period.get_n_step(
        n_step_hourly=n_step_hourly,
        n_d_main=n_d_main,
        n_d_run_up=n_d_run_up,
        n_d_run_up_build=n_d_run_up_build
    )

    # json, csv ファイルからパラメータをロードする。
    # （ループ計算する必要の無い）事前計算を行い, クラス PreCalcParameters に必要な変数を格納する。
    pp, ppg = pre_calc_parameters.make_pre_calc_parameters(data_directory=input_data_dir)

    gc_n = conditions.initialize_ground_conditions(n_grounds=ppg.n_grounds)

    print('助走計算（土壌のみ）')
    for n in range(-n_step_run_up, -n_step_run_up_build):
        gc_n = sequence_ground.run_tick(gc_n=gc_n, ss=ppg, n=n)

    logger = log.Logger(n_spaces=pp.n_spaces, n_bdries=pp.n_bdries)
    logger.pre_logging(pp)

    # 建物を計算するにあたって初期値を与える
    c_n = conditions.initialize_conditions(n_spaces=pp.n_spaces, n_bdries=pp.n_bdries)

    # 地盤計算の結果（項別公比法の指数項mの吸熱応答の項別成分・表面熱流）を建物の計算に引き継ぐ
    c_n = conditions.update_conditions_by_ground_conditions(
        is_ground=pp.is_ground_js.flatten(),
        c=c_n,
        gc=gc_n
    )

    print('助走計算（建物全体）')
    for n in range(-n_step_run_up_build, 0):
        c_n = sequence.run_tick(n=n, ss=pp, c_n=c_n, logger=logger)

    print('本計算')
    for n in range(0, n_step_main):
        c_n = sequence.run_tick(n=n, ss=pp, c_n=c_n, logger=logger)

    logger.post_logging(pp)

    print('ログ作成')

    # ds: data simple, 1時間間隔で主要なパラメータのみを抽出した pd.DataFrame
    # dd: data detail, 15分間隔のすべてのパラメータ pd.DataFrame
    ds, dd = log.record(
        pps=pp,
        logger=logger,
        output_data_dir=output_data_dir,
        show_simple_result=show_simple_result,
        show_detail_result=show_detail_result
    )

    return ds, dd
