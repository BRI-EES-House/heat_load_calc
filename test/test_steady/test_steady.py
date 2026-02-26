import numpy as np
from enum import Enum, auto

from heat_load_calc.input_models.input_building import InputBuilding
from heat_load_calc.input_models.input_infiltration import InputInfiltration
from heat_load_calc.input_models.input_room import InputRoom
from heat_load_calc.input_models.input_boundary import InputBoundary
from heat_load_calc.input_models.input_furniture import InputFurniture, InputFurnitureDefault, InputFurnitureSpecify
from heat_load_calc.input_models.input_schedule_data import InputScheduleData, InputScheduleDataConst

from heat_load_calc.weather import Weather
from heat_load_calc.schedule import Schedule
from heat_load_calc.interval import Interval
from heat_load_calc.tenum import EInterval
from heat_load_calc.sequence import Sequence
from heat_load_calc.operation_mode import OperationMode
from heat_load_calc.boundaries import Boundaries
from heat_load_calc.conditions import Conditions
from heat_load_calc.building import Building
from heat_load_calc.rooms import Rooms
from heat_load_calc.tenum import EInfiltrationMethod, EStory, ECValueEstimateMethod, EInsidePressure, EShapeFactorMethod

class TestCase(Enum):

    SINGLE_ZONE = auto()
    MULTI_ZONE = auto()

# s = settings

# weather settings (constant)

s_weather = {
    'solar_azimuth': -15.0, # deg.
    'solar_altitude': 30.0, # deg.
    'direct_solar_radiation': 700.0, # W
    'sky_radiation': 200.0, # W
    'nighttime_radiation': 0.0, # W
    'outdoor_temperature': 0.0, # deg.C
    'outdoor_absolute_humidity': 0.0, # kg/kg(DA)
} 

s_schedule = {
    TestCase.SINGLE_ZONE:{
        'number_of_room': 1,
        'heat_generated_inside': 100.0, # W
        'moisture_generated_insid': 0.0, # kg/s
        'local_ventilation_amount': 1.0/3600, # m3/s
        'number_of_people': 0.0,
        'air_conditioning_demand': 0.0,
        'ac_mode': 0,
    },
    TestCase.MULTI_ZONE:{
        'number_of_room': 2,
        'heat_generated_inside': [100.0, 50.0], # W
        'moisture_generated_insid': [0.0, 0.0], # kg/s
        'local_ventilation_amount': [1.0/3600, 1.0/3600], # m3/s
        'number_of_people': [0.0, 0.0],
        'air_conditioning_demand': [0.0, 0.0],
        'ac_mode': [0, 0],
    }
}

steady_condition = {
    TestCase.SINGLE_ZONE:{
        'operation_mode': [OperationMode.STOP_CLOSE],
        'room_temperature': [43.97202065068], # deg.C
        'MRT': [27.9767467], # deg.C
        'absolute_humidity': [0.0], # kg/kg(DA)
        'furniture_temperature': [159.003296832], # deg.C
        'furniture_absolute_humidity': [0.0], # kg/kg(DA)
        'heat_flow_at_surface': [
            111.791801018316,
            115.054074456381,
            110.951576197515,
            111.791801018316,
            221.710603408839, 
            51.7029121294266
        ], # deg.C
        'equivalent_surface_temperature': [
            29.233155229121,
            29.233155229121,
            29.233155229121,
            29.233155229121,
            64.3084919621933,
            29.233155229121
        ],
    },
    TestCase.MULTI_ZONE:{
        'operation_mode': [OperationMode.STOP_CLOSE, OperationMode.STOP_CLOSE],
        'room_temperature': [98.4453457337847, 84.1682535365713], # deg.C
        'MRT': [92.1275839485637, 81.4104763944663],
        'absolute_humidity': [0.0, 0.0], # kg/kg(DA)
        'furniture_temperature': [144.968310321296, 130.691218124083], # deg.C
        'furniture_absolute_humidity': [0.0, 0.0], # kg/kg(DA)
        'heat_flow_at_surface': [
            22.5640843447614,
            28.7776071971038, 
            27.1092772092918, 
            28.7776071971038, 
            34.5498206239126, 
            18.4455892778106, 
            24.6659904777119, 
            22.9976604898999, 
            24.6659904777119, 
            20.1735351503884, 
            401.848561318479, 
            343.04893859407, 
            -6.47651020672211, 
            6.47651020672555
        ], # deg.C
        'equivalent_surface_temperature': [
            90.9040129182149,
            90.6859250357919,
            90.6859250357919,
            90.6859250357919,
            105.737344414368,
            78.4766505951595,
            78.3120550702779,
            78.3120550702779,
            78.3120550702779,
            78.3120550702779,
            91.791646652984,
            79.1465664971971,
            90.6859250357919,
            93.3634744488544
        ],
    },
}

s_building = {
    'story': EStory.ONE,
    'c_value': 0.0,
    'inside_pressure': EInsidePressure.NEGATIVE
}

s_rooms = {
    TestCase.SINGLE_ZONE:[
        {
            'id': 0,
            'name': 'main_occupant_room',
            'a_f': 1.0,
            'volume': 1.0,
            'natural_ventilation': 0.0,
        }
    ],
    TestCase.MULTI_ZONE:[
        {
            'id': 0,
            'name': '1F_room',
            'a_f': 1.0,
            'volume': 1.0,
            'natural_ventilation': 0.0,
        },
        {
            'id': 1,
            'name': '2F_room',
            'a_f': 1.0,
            'volume': 1.0,
            'natural_ventilation': 0.0,
        }
    ]
}

def make_weather():

    return Weather.create_constant(
        a_sun=np.radians(s_weather['solar_azimuth']),
        h_sun=np.radians(s_weather['solar_altitude']),
        i_dn=s_weather['direct_solar_radiation'],
        i_sky=s_weather['sky_radiation'],
        r_n=s_weather['nighttime_radiation'],
        theta_o=s_weather['outdoor_temperature'],
        x_o=s_weather['outdoor_absolute_humidity']
    )


def make_schedule(test_case: TestCase):

    return Schedule.create_constant(
        n_rm=s_schedule[test_case]['number_of_room'],
        q_gen=s_schedule[test_case]['heat_generated_inside'],
        x_gen=s_schedule[test_case]['moisture_generated_insid'],
        v_mec_vent_local=s_schedule[test_case]['local_ventilation_amount'],
        n_hum=s_schedule[test_case]['number_of_people'],
        r_ac_demanc=s_schedule[test_case]['air_conditioning_demand'],
        t_ac_mode=s_schedule[test_case]['ac_mode']
    )


def make_building():
    
    return InputBuilding(
        ipt_infiltration=InputInfiltration(
            method=EInfiltrationMethod.BALANCE_RESIDENTIAL,
            story=s_building['story'],
            c_value_estimate=ECValueEstimateMethod.SPECIFY,
            c_value=s_building['c_value'],
            ua_value=None,
            struct=None,
            inside_pressure=s_building['inside_pressure']
        )
    )


def make_rooms(test_case: TestCase):

    return [
        InputRoom(
            id=d['id'],
            name=d['name'],
            sub_name='',
            a_f=d['a_f'],
            v=d['volume'],
            ipt_furniture=InputFurnitureDefault(solar_absorption_ratio=0.5),
            v_vent_ntr_set=d['natural_ventilation'],
            met=1.0,
            ipt_schedule_data=None
        )
        for d
        in s_rooms[test_case]
    ]


def initialize(test_case: TestCase, d: dict):

    w = make_weather()

    scd = make_schedule(test_case=test_case)

    itv = Interval(eitv=EInterval.M15)

    shape_factor_method = EShapeFactorMethod.NAGATA

    ipt_building = make_building()

    bdg = Building.create_building(ipt_building=ipt_building)

    ipt_rooms = make_rooms(test_case=test_case)

    rms = Rooms(ipt_rooms=ipt_rooms)

    ipt_boundaries = [InputBoundary.read(d_boundary=d_boundary) for d_boundary in d['boundaries']]

    bs = Boundaries(id_r_is=rms.id_r_is, ds=d['boundaries'], w=w, rad_method=shape_factor_method, ipt_boundaries=ipt_boundaries)

    sqc = Sequence(itv=itv, d=d, weather=w, scd=scd, bdg=bdg, rms=rms, bs=bs)

    return sqc


def get_steady_state_conditions(test_case: TestCase, bs: Boundaries):

    operation_mode_is_n = np.array(
        steady_condition[test_case]['operation_mode']
    ).reshape(-1, 1)

    theta_r_is_n = np.array(
        steady_condition[test_case]['room_temperature']
    ).reshape(-1, 1)

    theta_mrt_hum_is_n = np.array(
        steady_condition[test_case]['MRT']
    ).reshape(-1, 1)

    x_r_is_n = np.array(
        steady_condition[test_case]['absolute_humidity']
    ).reshape(-1, 1)

    q_s_js_n = np.array(
        steady_condition[test_case]['heat_flow_at_surface']
    ).reshape(-1, 1)

    theta_ei_js_n = np.array(
        steady_condition[test_case]['equivalent_surface_temperature']
    ).reshape(-1, 1)

    theta_dsh_s_a_js_ms_n = q_s_js_n * bs.phi_a1_js_ms / (1.0 - bs.r_js_ms)

    theta_dsh_s_t_js_ms_n = (
                np.dot(bs.k_ei_js_js, theta_ei_js_n)
                + bs.k_eo_js * bs.theta_o_eqv_js_nspls[:, 1].reshape(-1, 1)
                + np.dot(bs.k_s_r_js_is, theta_r_is_n)
                ) * bs.phi_t1_js_ms / (1.0 - bs.r_js_ms)
    
    theta_frt_is_n = np.array(
        steady_condition[test_case]['furniture_temperature']
    ).reshape(-1, 1)

    x_frt_is_n = np.array(
        steady_condition[test_case]['furniture_absolute_humidity']
    ).reshape(-1, 1)
    
    c_n = Conditions(
            operation_mode_is_n=operation_mode_is_n,
            theta_r_is_n=theta_r_is_n,
            theta_mrt_hum_is_n=theta_mrt_hum_is_n,
            x_r_is_n=x_r_is_n,
            theta_dsh_s_a_js_ms_n=theta_dsh_s_a_js_ms_n,
            theta_dsh_s_t_js_ms_n=theta_dsh_s_t_js_ms_n,
            q_s_js_n=q_s_js_n,
            theta_frt_is_n=theta_frt_is_n,
            x_frt_is_n=x_frt_is_n,
            theta_ei_js_n=theta_ei_js_n
    )

    return c_n
