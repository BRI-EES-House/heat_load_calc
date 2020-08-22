"""
附属書X17 計算期間
「本計算のステップ数」「助走計算のステップ数」「助走計算のうち建物全体を解く日数」を定義する。
"""


def get_n_step(
        n_step_hourly: int,
        n_d_main: int,
        n_d_run_up: int,
        n_d_run_up_build: int
):
    """

    Args:
        n_step_hourly: 計算間隔（1時間を何分割するかどうか）（デフォルトは4（15分間隔））
        n_d_main: 本計算を行う日数, d
        n_d_run_up: 助走計算を行う日数, d
        n_d_run_up_build: 助走計算のうち建物全体を解く日数, d

    Returns:
        以下のタプル
            (1) 本計算のステップ数
            (2) 助走計算のステップ数
            (3) 助走計算のうち建物全体を解くステップ数
    """

    # n_d_run_up（助走計算を行う日数）はn_d_run_up_build（助走計算のうち建物全体を解く日数）以上の値としないといけない。
    if n_d_run_up < n_d_run_up_build:
        raise ValueError('n_d_run_up should be more than or equal to n_d_run_up_build.')

    # 本計算のステップ数
    n_step_main = _get_n_step_main(n_step_hourly=n_step_hourly, n_d_main=n_d_main)

    # 助走計算のステップ数
    n_step_run_up = _get_n_step_run_up(n_step_hourly=n_step_hourly, n_d_run_up=n_d_run_up)

    # 助走計算のうち建物全体を解くステップ数
    n_step_run_up_build = _get_n_step_run_up_build(n_step_hourly=n_step_hourly, n_d_run_up_build=n_d_run_up_build)

    return n_step_main, n_step_run_up, n_step_run_up_build


def _get_n_step_main(n_step_hourly: int, n_d_main: int) -> int:
    """
    本計算のステップ数を計算する。

    Args:
        n_step_hourly: 計算間隔（1時間を何分割するかどうか）（デフォルトは4（15分間隔））
        n_d_main: 本計算を行う日数, d

    Returns:
        本計算のステップ数
    """

    return n_d_main * n_step_hourly * 24


def _get_n_step_run_up(n_step_hourly: int, n_d_run_up: int) -> int:
    """助走計算のステップ数を計算する。

    Args:
        n_step_hourly: 計算間隔（1時間を何分割するかどうか）（デフォルトは4（15分間隔））
        n_d_run_up: 助走計算を行う日数, d

    Returns:
        助走計算のステップ数
    """

    return n_d_run_up * n_step_hourly * 24


def _get_n_step_run_up_build(n_step_hourly: int, n_d_run_up_build: int) -> int:
    """助走計算のうち建物全体を解くステップ数を定義する。
    Args:
        n_step_hourly: 計算間隔（1時間を何分割するかどうか）（デフォルトは4（15分間隔））
        n_d_run_up_build: 助走計算のうち建物全体を解く日数, d
    Returns:
        助走計算のうち建物全体を解くステップ数
    """

    return n_d_run_up_build * n_step_hourly * 24

