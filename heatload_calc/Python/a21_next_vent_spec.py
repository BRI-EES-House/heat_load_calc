import numpy as np

"""
付録21．隣室間換気の定義
"""


def read_next_vent_volume(d_room):
    return np.array([room_vent['volume'] for room_vent in d_room['next_vent']])


def read_upstream_room_type(d_room):
    return [room_vent['upstream_room_type'] for room_vent in d_room['next_vent']]
