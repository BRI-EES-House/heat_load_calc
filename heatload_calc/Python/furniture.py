from common import funiture_sensible_capacity, funiture_latent_capacity

# 家具の熱容量・熱コンダクタンスと備品等の湿気容量・湿気コンダクタンスの計算
def calc_furniture(space):
    space.Capfun = space.volume * funiture_sensible_capacity * 1000.
                                                # 家具熱容量[J/K]
    # self.Capfun = 0.0
    space.Cfun = 0.00022 * space.Capfun       # 家具と空気間の熱コンダクタンス[W/K]
    space.Gf = funiture_latent_capacity * space.volume
                                                # 家具類の湿気容量[kg]
    space.Cx = 0.0018 * space.Gf              # 室空気と家具類間の湿気コンダクタンス[kg/(s･kg/kg(DA))]
