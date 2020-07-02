import pandas as pd

from heat_load_calc.weather import weather_data
from heat_load_calc.weather import region_location
from heat_load_calc.weather import solar_position


def make_weather(region: int, output_data_dir: str = None, csv_output: bool = False):

    # 気象データの読み込み
    #   (1)ステップnにおける外気温度, ℃, [8760 * 4]
    #   (2)ステップnにおける法線面直達日射量, W/m2, [8760 * 4]
    #   (3)ステップnにおける水平面天空日射量, W/m2, [8760 * 4]
    #   (4)ステップnにおける夜間放射量, W/m2, [8760 * 4]
    #   (5)ステップnにおける外気絶対湿度, kg/kgDA, [8760 * 4]
    theta_o_ns, i_dn_ns, i_sky_ns, r_n_ns, x_o_ns = weather_data.load(region=region)

    # 緯度, rad & 経度, rad
    phi_loc, lambda_loc = region_location.get_phi_loc_and_lambda_loc(region=region)

    # 太陽位置
    #   (1) ステップnにおける太陽高度, rad, [8760 * 96]
    #   (2) ステップnにおける太陽方位角, rad, [8760 * 96]
    h_sun_ns, a_sun_ns = solar_position.calc_solar_position(phi_loc=phi_loc, lambda_loc=lambda_loc)

    dd = pd.DataFrame(index=pd.date_range(start='1/1/1989', periods=365*96, freq='15min'))
    dd['temperature [degree C]'] = theta_o_ns.round(3)
    dd['absolute humidity [kg/kg(DA)]'] = x_o_ns.round(6)
    dd['normal direct solar radiation [W/m2]'] = i_dn_ns
    dd['horizontal sky solar radiation [W/m2]'] = i_sky_ns
    dd['outward radiation [W/m2]'] = r_n_ns
    dd['sun altitude [rad]'] = h_sun_ns
    dd['sun azimuth [rad]'] = a_sun_ns

    if csv_output:
        dd.to_csv(output_data_dir + '/weather.csv', encoding='utf-8')

    return dd