from apdx10_oblique_incidence_characteristics import get_CID, get_Cd
import a23_surface_heat_transfer_coefficient as a23

"""
付録25．開口部の仕様
"""

# 室内表面から裏面空気までの熱貫流率 式(124)
def get_Uso(Uw, Ri_i_k_n):
    return 1.0 / (1.0 / Uw - Ri_i_k_n)


