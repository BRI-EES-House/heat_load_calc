import numpy as np


def get_f_mrt_hum_js(p_is_js: np.ndarray, a_s_js: np.ndarray, is_floor_js: np.ndarray) -> np.ndarray:
    """Calculate the shape factor of boundaries j for the occupant in room i
    Args:
        p_is_js: vector of the relation between rooms and boundaries
        a_s_js: area of boundary j, m2, [j, 1]
        is_floor_js: is boundary j floor?, [j, 1]
    Returns:
        shape factor of boundaries j for the occupant in room i, [i, j]
    """

    # boundaries area which is floor, m2, [j, 1]
    a_s_js_floor = a_s_js * is_floor_js

    # boundaries area which is not floor, m2, [j, 1]
    a_s_js_not_floor = a_s_js * np.logical_not(is_floor_js)

    # shape factor of boundaries j for the occupant in room i, [i, j]
    f_mrt_hum_is_js = p_is_js * a_s_js_floor.flatten() / np.dot(p_is_js, a_s_js_floor).reshape(-1, 1) * 0.45 \
        + p_is_js * a_s_js_not_floor.flatten() / np.dot(p_is_js, a_s_js_not_floor).reshape(-1, 1) * 0.55
    
    # check the sum of the shape factor of each room equals to be 1.0.
    if np.any(np.abs(f_mrt_hum_is_js.sum(axis=1) - 1.0) > 1.0e-4):
        raise ValueError()

    return f_mrt_hum_is_js

