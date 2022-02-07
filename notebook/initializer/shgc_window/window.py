from typing import Dict
import numpy as np
import xlrd
import logging

from notebook.initializer.shgc_window import glass_thermal_balance as gtb
from notebook.initializer.shgc_window import multiple_reflection as mr


def calc_for_from_excel():

    wb = xlrd.open_workbook('....xlsx')

    sheet_single = wb.sheets()['single']

    for i in range(10):
        tau_f = sheet_single.cell(1, i)
        d = {
            'tau_f': tau_f
        }

        calc_for_single(d)

    sheet_double = wb.sheets()['double']

    for i in range(10):
        tau_f = sheet_double.cell(1,i)
        d = {

        }

        calc_for_double(d)




def calc_for_single(d: Dict):

    m = mr.Glass(ss=[
        mr.SolarSpecSingleLayer(tau_f=0.859, tau_b=0.859, rho_f=0.077, rho_b=0.077)
    ])

    g = gtb.Glass(
        gls=[
            gtb.GlassLayer(gus=[gtb.GlassUnit(d=0.003, lmd=1.0)], sff=gtb.NonLowESurface(), sfb=gtb.NonLowESurface())
        ],
        als=[]
    )

    calc(m=m, g=g)


def calc_for_double(d: Dict):

#    air_type = d['air_type']

#    gus = {
#        'air': gtb.MixedAirProperty(c_air=100.0, c_argon=0.0, c_sf6=0.0, c_krypton=0.0)
#    }[air_type]

    m = mr.Glass(ss=[
        mr.SolarSpecSingleLayer(tau_f=0.859, tau_b=0.859, rho_f=0.077, rho_b=0.077),
        mr.SolarSpecSingleLayer(tau_f=0.859, tau_b=0.859, rho_f=0.077, rho_b=0.077)
    ])

    g = gtb.Glass(
        gls=[
            gtb.GlassLayer(gus=[gtb.GlassUnit(d=0.003, lmd=1.0)], sff=gtb.NonLowESurface(), sfb=gtb.NonLowESurface()),
            gtb.GlassLayer(gus=[gtb.GlassUnit(d=0.003, lmd=1.0)], sff=gtb.NonLowESurface(), sfb=gtb.NonLowESurface())
        ],
        als=[
            gtb.AirLayer(
                air_property=gtb.MixedAirProperty(c_air=100.0, c_argon=0.0, c_sf6=0.0, c_krypton=0.0),
                direction=gtb.GlassDirection.VERTICAL,
                s=0.006
            )
        ]
    )

    calc(m=m, g=g)


def calc(m: mr.Glass, g: gtb.Glass):

    # W/m2
    i_solar = 300.0

    spec = m.get_total_solar_spec()

    # 透過率
    tau = spec.tau_f

    abs = np.array(m.get_abs_multi_layer())

    # 吸収率, nparray[float]
    i_abs = abs * i_solar

    theta_g, reg, r_qin = g.get_temp_and_r(
        theta_e=0.0,
        theta_i=20.0,
        surface_method='JIS_R3107',
        season='winter',
        decision_air_layer_temp='calc',
        ia=i_abs
    )

    shgc = r_qin / i_solar + tau

    u = g.get_heat_transmittance()

    logging.debug('abs: ' + str(abs))
    logging.debug('tau: ' + str(tau))
    logging.debug('r_qin: ' + str(r_qin))
    logging.debug('U_value: ' +  str(u))
    logging.debug('SHGC: ' + str(shgc))


if __name__ == '__main__':

    calc_for_single(d={})
