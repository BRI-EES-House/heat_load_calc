from heat_load_calc.core import period
from heat_load_calc.core import pre_calc_parameters
from heat_load_calc.core import conditions
from heat_load_calc.core import log


def calc():

    # 本計算のステップ数
    n_step_main = period.get_n_step_main()

    # 助走計算のステップ数
    n_step_run_up = period.get_n_step_run_up()

    # 助走計算の日数のうち建物全体を解く日数, d
    n_step_run_up_build = period.get_n_step_run_up_build()

    # json, csv ファイルからパラメータをロードする。
    # （ループ計算する必要の無い）事前計算を行い, クラス PreCalcParameters に必要な変数を格納する。
    pps = pre_calc_parameters.make_pre_calc_parameters()

    c_n = conditions.initialize_conditions(ss=pps)

    logger = log.Logger(n_spaces=pps.number_of_spaces, n_bdrys=pps.total_number_of_bdry)
    logger.pre_logging(pps)

    return n_step_main, n_step_run_up, n_step_run_up_build, pps, c_n, logger
