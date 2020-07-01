from heat_load_calc.core import period
from heat_load_calc.core import pre_calc_parameters
from heat_load_calc.core import conditions
from heat_load_calc.core import log
from heat_load_calc.core import sequence


def calc(input_data_dir: str, output_data_dir: str, show_simple_result: bool = False, show_detail_result: bool = False):

    # 本計算のステップ数
    n_step_main = period.get_n_step_main()

    # 助走計算のステップ数
    n_step_run_up = period.get_n_step_run_up()

    # 助走計算の日数のうち建物全体を解く日数, d
    n_step_run_up_build = period.get_n_step_run_up_build()

    # json, csv ファイルからパラメータをロードする。
    # （ループ計算する必要の無い）事前計算を行い, クラス PreCalcParameters に必要な変数を格納する。
    pps = pre_calc_parameters.make_pre_calc_parameters(data_directory=input_data_dir)

    gc_n = conditions.initialize_ground_conditions(n_gound=pps.number_of_grounds)

    print('助走計算（土壌のみ）')
    for n in range(-n_step_run_up, -n_step_run_up_build):
        gc_n = sequence.run_tick_groundonly(gc_n=gc_n, ss=pps, n=n)

    logger = log.Logger(n_spaces=pps.number_of_spaces, n_bdrys=pps.total_number_of_bdry)
    logger.pre_logging(pps)

    # 建物を計算するにあたって初期値を与える
    c_n = conditions.initialize_conditions(ss=pps)

    # 地盤計算の結果（項別公比法の指数項mの吸熱応答の項別成分・表面熱流）を建物の計算に引き継ぐ
    c_n = conditions.update_conditions_by_ground_conditions(
        is_ground=pps.is_ground_js.flatten(),
        c=c_n,
        gc=gc_n
    )

    print('助走計算（建物全体）')
    for n in range(-n_step_run_up_build, 0):
        c_n = sequence.run_tick(n=n, ss=pps, c_n=c_n, logger=logger)

    print('本計算')
    for n in range(0, n_step_main):
        c_n = sequence.run_tick(n=n, ss=pps, c_n=c_n, logger=logger)

    logger.post_logging(pps)

    print('ログ作成')

    # ds: data simple, 1時間間隔で主要なパラメータのみを抽出した pd.DataFrame
    # dd: data detail, 15分間隔のすべてのパラメータ pd.DataFrame
    ds, dd = log.record(
        pps=pps,
        logger=logger,
        output_data_dir=output_data_dir,
        show_simple_result=show_simple_result,
        show_detail_result=show_detail_result
    )

    return ds, dd
