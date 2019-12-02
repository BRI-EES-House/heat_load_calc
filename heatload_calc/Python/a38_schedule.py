import numpy as np


def get_local_vent_schedules(room, n_p):
    """局所換気スケジュールを取得する。

    Args:
        room:

    Returns:
        局所換気スケジュール
    """

    return np.repeat(room['schedule']['local_vent_amount'], 4)


def get_sensible_heat_generation_of_cooking(room, n_p):
    """調理潜熱発熱スケジュールを取得する。

    Args:
        room:

    Returns:
        調理潜熱発熱スケジュール
    """

    return np.repeat(room['schedule']['vapor_generation_cooking'], 4)


def get_latent_heat_generation_of_cooking(room, n_p):
    """調理発熱スケジュールを取得する。

    Args:
        room:

    Returns:
        調理発熱スケジュール
    """

    return np.repeat(room['schedule']['heat_generation_cooking'], 4)


def get_heat_generation_of_appliances(room, n_p):
    """機器発熱スケジュールを取得する。

    Args:
        room:

    Returns:
        機器発熱スケジュール
    """

    return np.repeat(room['schedule']['heat_generation_appliances'], 4)


def get_heat_generation_of_lighting(room, n_p):
    """照明発熱スケジュールを取得する。

    Args:
        room:

    Returns:
        照明発熱スケジュール
    """

    return np.repeat(room['schedule']['heat_generation_lighting'], 4)


def get_number_of_residents(room, n_p):
    """在室人数スケジュールを取得する。

    Args:
        room:

    Returns:
        在室人数スケジュール
    """

    return np.repeat(room['schedule']['number_of_people'], 4)


def get_air_conditioning_schedules(room, n_p) -> (np.ndarray, np.ndarray, np.ndarray, np.ndarray):
    """空調スケジュールを取得する。

    Args:
        room:

    Returns:
        空調スケジュール
    """

    # 空調スケジュールの読み込み
    # 設定温度／PMV上限値の設定
    is_upper_temp_limit_set_schedule = np.repeat(room['schedule']['is_upper_temp_limit_set'], 4)
    # 設定温度／PMV下限値の設定
    is_lower_temp_limit_set_schedule = np.repeat(room['schedule']['is_lower_temp_limit_set'], 4)

    # PMV上限値
    pmv_upper_limit_schedule = np.repeat(room['schedule']['pmv_upper_limit'], 4)
    # PMV下限値
    pmv_lower_limit_schedule = np.repeat(room['schedule']['pmv_lower_limit'], 4)

    return is_upper_temp_limit_set_schedule, \
           is_lower_temp_limit_set_schedule, \
           pmv_upper_limit_schedule, \
           pmv_lower_limit_schedule


