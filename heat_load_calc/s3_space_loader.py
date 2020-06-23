import math
import numpy as np
from typing import List
from collections import namedtuple

from a39_global_parameters import BoundaryType
from heat_load_calc.core.operation_mode import OperationMode
from heat_load_calc.core.pre_calc_parameters import PreCalcParameters
from heat_load_calc.external import psychrometrics as psy


def get_start_indices(number_of_boundaries: np.ndarray):

    start_indices = []
    indices = 0
    for n_bdry in number_of_boundaries:
        indices = indices + n_bdry
        start_indices.append(indices)
    start_indices.pop(-1)
    return start_indices


