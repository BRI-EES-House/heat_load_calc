from typing import Dict, List

from heat_load_calc.convert import get_u_psi_eta_from_u_a_and_eta_a as get_u_and_eta
from heat_load_calc.convert import model_house
from heat_load_calc.convert import check_ua_a_eta_a as cue
from heat_load_calc.convert.ees_house import GeneralPartType, SpaceType, GlassType, FlameType
from heat_load_calc.convert.ees_house import GeneralPart, GeneralPartNoSpec, GeneralPartSpec, GeneralPartSpecUValueOther
from heat_load_calc.convert.ees_house import Door, DoorNoSpec, DoorSpec
from heat_load_calc.convert.ees_house import Window, WindowNoSpec, WindowSpec
from heat_load_calc.convert.ees_house import EarthfloorPerimeter, EarthfloorPerimeterNoSpec, EarthfloorPerimeterSpec
from heat_load_calc.convert.ees_house import EarthfloorCenter, EarthfloorCenterNoSpec, EarthfloorCenterSpec
from heat_load_calc.convert.ees_house import EesHouse
from heat_load_calc.external.factor_nu import Direction


def convert_spec(d: Dict):

    common = d['common']

    region = common['region']
    house_type = common['house_type']
    a_f_total = common['total_floor_area']

    envelope = d['envelope']

    a_env_total = envelope['total_area']
    indices = envelope['indices']

    u_a = indices['u_a']
    eta_a_h = indices['eta_a_h']
    eta_a_c = indices['eta_a_c']

    # 窓の開口部比率は10.0%とする。
    r_open = 0.1

    # 戸建住戸の場合は床断熱で浴室は基礎断熱とする。
    floor_ins_type, bath_ins_type = {
        'detached': ('floor', 'base'),
        'attached': (None, None)
    }[house_type]

    model_house_shape = model_house.calc_area(
        house_type=house_type, a_f_total=a_f_total, r_open=r_open,
        floor_ins_type=floor_ins_type, bath_ins_type=bath_ins_type, a_env_input=a_env_total
    )

    gps, ws, ds, eps, ecs = model_house.get_model_house_no_spec(**model_house_shape)

    u_psi, eta_d, eta_d_h, eta_d_c = get_u_and_eta.calc_parts_spec(
        region=region,
        u_a_target=u_a,
        eta_a_h_target=eta_a_h,
        eta_a_c_target=eta_a_c,
        gps=gps,
        ds=ds,
        ws=ws,
        eps=eps,
        ecs=ecs
    )

    gps_spec = add_spec_gps(gps, u_psi)

    ws_spec = add_spec_ws(ws, u_psi, eta_d, eta_d_c, eta_d_h)

    ds_spec = add_spec_ds(ds, u_psi)

    eps_spec = add_spec_eps(eps, u_psi)

    ecs_spec = add_spec_ecs(ecs)

    return {
        'input_method': 'detail_without_room_usage',
        'general_parts': [s.get_as_dict() for s in gps_spec],
        'windows': [s.get_as_dict() for s in ws_spec],
        'doors': [s.get_as_dict() for s in ds_spec],
        'earthfloor_perimeters': [s.get_as_dict() for s in eps_spec],
        'earthfloor_centers': [s.get_as_dict() for s in ecs_spec],
        'heat_bridges': []
    }


def add_spec_gps(gps: List[GeneralPartNoSpec], u: get_u_and_eta.PartType) -> List[GeneralPart]:
    """

    Args:
        gps:
        u: U値を格納した辞書
    Returns:
        gps:
    """
    gps_spec = [
        GeneralPart(
            name=s.name,
            general_part_type=s.general_part_type,
            next_space=s.next_space,
            direction=s.direction,
            area=s.area,
            space_type=s.space_type,
            sunshade=s.sunshade,
            general_part_spec=GeneralPartSpecUValueOther(
                general_part_type=s.general_part_type,
                u_value_other=get_u_and_eta.get_u_psi(u, s.general_part_type.value),
                weight='light'
            )
        )
        for s in gps
    ]
    return gps_spec


def add_spec_ws(
        ws: List[WindowNoSpec], u: get_u_and_eta.PartType, eta_d: float, eta_d_c: float, eta_d_h: float
) -> List[Window]:
    """
    Args:
        ws:
        u: U値を格納した辞書
        eta_d: ηd値
        eta_d_h: ηdh値
        eta_d_c: ηdc値
    Returns:
    """
    ws_spec = [
        Window(
            name=s.name,
            area=s.area,
            next_space=s.next_space,
            direction=s.direction,
            space_type=SpaceType.UNDEFINED,
            sunshade=s.sunshade,
            window_spec=WindowSpec(
                u=get_u_and_eta.get_u_psi(u, 'window'),
                eta_d_h=eta_d_h,
                eta_d_c=eta_d_c,
                glass_type=GlassType.SINGLE,
                flame_type=FlameType.METAL
            )
        )
        for s in ws
    ]
    return ws_spec


def add_spec_ds(ds: List[DoorNoSpec], u: get_u_and_eta) -> List[Door]:
    ds_spec = [
        Door(
            name=s.name,
            next_space=s.next_space,
            direction=s.direction,
            area=s.area,
            space_type=s.space_type,
            sunshade=s.sunshade,
            door_spec=DoorSpec(u_value=get_u_and_eta.get_u_psi(u, 'door'))
        )
        for s in ds
    ]
    return ds_spec


def add_spec_eps(eps: List[EarthfloorPerimeterNoSpec], u: get_u_and_eta) -> List[EarthfloorPerimeter]:
    eps_spec = [
        EarthfloorPerimeter(
            name=ep.name,
            next_space=ep.next_space,
            length=ep.length,
            space_type=ep.space_type,
            earthfloor_perimeter_spec=EarthfloorPerimeterSpec(
                psi_value=get_u_and_eta.get_u_psi(u, 'earthfloor_perimeter')
            )
        )
        for ep in eps
    ]
    return eps_spec


def add_spec_ecs(ecs: List[EarthfloorCenterNoSpec]) -> List[EarthfloorCenter]:
    """

    Args:
        ecs:

    Returns:

    """
    ecs_spec = [
        EarthfloorCenter(
            name=s.name,
            area=s.area,
            space_type=s.space_type,
            earthfloor_center_spec=EarthfloorCenterSpec(
                layers=[]
            )
        )
        for s in ecs
    ]
    return ecs_spec


def print_result(checked_u_a, checked_eta_a_h, checked_eta_a_c):

    print('計算UA値：' + str(checked_u_a))
    print('計算ηAH値：' + str(checked_eta_a_h))
    print('計算ηAC値：' + str(checked_eta_a_c))


if __name__ == '__main__':

    input_data_1 = {
        'common': {
            'region': 6,
            'house_type': 'detached',
            'main_occupant_room_floor_area': 30.0,
            'other_occupant_room_floor_area': 30.0,
            'total_floor_area': 90.0,
        },
        'envelope': {
            'input_method': 'index',
            'total_area': 266.0962919879752,
            'indices': {
                'u_a': 0.87,
                'eta_a_h': 2.8,
                'eta_a_c': 1.4,
            },
        }
    }

    result1 = convert_spec(d=input_data_1)

    checked_u_a1, checked_eta_a_h1, checked_eta_a_c1 = cue.check_u_a_and_eta_a(
        region=input_data_1['common']['region'], model_house_envelope=result1)

    print_result(checked_u_a=checked_u_a1, checked_eta_a_h=checked_eta_a_h1, checked_eta_a_c=checked_eta_a_c1)

    print(result1)
