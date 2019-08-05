from common import Sgm

# 表面対流・放射熱伝達率の計算
def calc_surface_heat_transfer_coefficient(surfaces):
    # 室内側表面熱伝達率の計算
    for surface in surfaces:
        surface.hir = surface.Ei / (1.0 - surface.Ei * surface.FF) \
                * 4.0 * Sgm * (20.0 + 273.15) ** 3.0
        # surface.hir = 5.0
        surface.hic = max(0.0, surface.hi - surface.hir)
        # print(surface.name, surface.hic, surface.hir, surface.hi)