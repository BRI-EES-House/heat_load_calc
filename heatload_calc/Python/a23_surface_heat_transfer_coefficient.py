import numpy as np
import a18_initial_value_constants as a18

"""
付録23．	表面熱伝達率
"""


# 室内側表面総合熱伝達率 式(122)
def get_h_i_i_ks(Ri_i_k_n):
    return 1.0 / Ri_i_k_n

