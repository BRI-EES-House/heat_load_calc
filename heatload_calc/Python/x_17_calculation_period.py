# 附属書X17 計算期間
# 本計算のステップ数」「助走計算のステップ数」「助走計算のうち建物全体を解く日数」を定義する。


def get_n_step_main() -> int:
    """
    本計算のステップ数を計算する。

    Returns:
        本計算のステップ数
    """

    return get_n_d_main() * get_n_step_day()


def get_n_step_run_up() -> int:
    """
    助走計算のステップ数を計算する。

    Returns:
        助走計算のステップ数
    """

    return get_n_d_run_up() * get_n_step_day()


def get_n_step_run_up_build() -> int:
    """
    助走計算のうち建物全体を解くステップ数を定義する。

    Returns:
        助走計算のうち建物全体を解くステップ数
    """

    return get_n_d_run_up_build() * get_n_step_day()


def get_n_d_main() -> int:
    """
    本計算の日数を定義する。

    Returns:
        本計算の日数, d
    """

    # 本計算の日数は365日
    return 365


def get_n_d_run_up() -> int:
    """
    助走計算の日数を定義する。

    Returns:
        助走計算の日数, d
    """

    # 助走計算の日数は365日
    return 365


def get_n_d_run_up_build() -> int:
    """
    助走計算のうち建物全体を解く日数を定義する。

    Returns:
        助走計算のうち建物全体を解く日数, d
    """

    # 助走計算のうち建物全体を解く日数は183日（およそ半年）とする。
    return 183


def get_n_step_day() -> int:
    """
    1日あたりのステップ数を計算する。

    Returns:
        1日あたりのステップ数

    Notes:
        今回の負荷計算では15分ごとの計算を行う。
        従って1時間あたりは4ステップ。1日では、4✕24の96ステップ
    """

    return 96
