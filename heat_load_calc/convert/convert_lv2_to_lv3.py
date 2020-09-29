import copy
from typing import Dict, Callable, List


def get_separated_areas(a_evlp_i: float, a_f_mr: float, a_f_or: float, a_f_total: float) -> (float, float, float):
    """
    面積を「主たる居室」「その他の居室」「非居室」の床面積に応じて按分する。
    Args:
        a_evlp_i: 面積, m2
        a_f_mr: 主たる居室の床面積, m2
        a_f_or: その他の居室の床面積, m2
        a_f_total: 床面積の合計, m2
    Returns:
        按分された以下に対応する面積のタプル。
            (1) 主たる居室
            (2) その他の居室
            (3) 非居室
    """

    a_evlp_mr_i = a_f_mr / a_f_total * a_evlp_i
    a_evlp_or_i = a_f_or / a_f_total * a_evlp_i
    a_evlp_nr_i = (a_f_total - a_f_mr - a_f_or) / a_f_total * a_evlp_i

    return a_evlp_mr_i, a_evlp_or_i, a_evlp_nr_i


def get_separated_lengths(l_evlp_i: float, a_f_mr: float, a_f_or: float, a_f_total: float) -> (float, float, float):
    """
    長さを「主たる居室」「その他の居室」「非居室」の床面積に応じて按分する。
    Args:
        l_evlp_i: 長さ, m
        a_f_mr: 主たる居室の床面積, m2
        a_f_or: その他の居室の床面積, m2
        a_f_total: 床面積の合計, m2
    Returns:
        按分された以下に対応する長さのタプル。
            (1) 主たる居室
            (2) その他の居室
            (3) 非居室
    """

    l_evlp_mr_i = a_f_mr / a_f_total * l_evlp_i
    l_evlp_or_i = a_f_or / a_f_total * l_evlp_i
    l_evlp_nr_i = (a_f_total - a_f_mr - a_f_or) / a_f_total * l_evlp_i

    return l_evlp_mr_i, l_evlp_or_i, l_evlp_nr_i


def get_evlps_lv3_area(a_f_mr: float, a_f_or: float, a_f_total: float,
        envelope: List[Dict], make_evlp_lv3: Callable[[Dict, str, float], Dict]) -> List[Dict]:

    result = []

    for evlp_lv2 in envelope:

        a_evlp_mr, a_evlp_or, a_evlp_nr = get_separated_areas(
            a_evlp_i=evlp_lv2['area'], a_f_mr=a_f_mr, a_f_or=a_f_or, a_f_total=a_f_total)

        result.append(make_evlp_lv3(evlp_lv2, 'main_occupant_room', a_evlp_mr))
        result.append(make_evlp_lv3(evlp_lv2, 'other_occupant_room', a_evlp_or))
        result.append(make_evlp_lv3(evlp_lv2, 'non_occupant_room', a_evlp_nr))

    return result


def get_evlps_lv3_length(a_f_mr: float, a_f_or: float, a_f_total: float,
        envelope: List[Dict], make_evlp_lv3: Callable[[Dict, str, float], Dict]) -> List[Dict]:

    result = []

    for evlp_lv2 in envelope:

        l_evlp_mr, l_evlp_or, l_evlp_nr = get_separated_lengths(
            l_evlp_i=evlp_lv2['length'],
            a_f_mr=a_f_mr,
            a_f_or=a_f_or,
            a_f_total=a_f_total
        )

        result.append(make_evlp_lv3(evlp_lv2, 'main_occupant_room', l_evlp_mr))
        result.append(make_evlp_lv3(evlp_lv2, 'other_occupant_room', l_evlp_or))
        result.append(make_evlp_lv3(evlp_lv2, 'non_occupant_room', l_evlp_nr))

    return result


def get_general_parts(a_f_mr: float, a_f_or: float, a_f_total: float, general_parts: List[Dict]) -> List[Dict]:

    def make_general_part_lv3(envelope, space_type, a_evlp):

        return {
            'name': envelope['name'] + '_' + space_type,
            'general_part_type': envelope['general_part_type'],
            'next_space': envelope['next_space'],
            'direction': envelope['direction'],
            'area': a_evlp,
            'space_type': space_type,
            'spec': copy.deepcopy(envelope['spec'])
        }

    return get_evlps_lv3_area(
        a_f_mr=a_f_mr,
        a_f_or=a_f_or,
        a_f_total=a_f_total,
        envelope=general_parts,
        make_evlp_lv3=make_general_part_lv3
    )


def get_windows(a_f_mr: float, a_f_or: float, a_f_total: float, windows: List[Dict]) -> List[Dict]:

    def make_window_lv3(envelope, space_type, a_evlp):

        return {
            'name': envelope['name'] + '_' + space_type,
            'next_space': envelope['next_space'],
            'direction': envelope['direction'],
            'area': a_evlp,
            'space_type': space_type,
            'spec': copy.deepcopy(envelope['spec'])
        }

    return get_evlps_lv3_area(
        a_f_mr=a_f_mr,
        a_f_or=a_f_or,
        a_f_total=a_f_total,
        envelope=windows,
        make_evlp_lv3=make_window_lv3
    )


def get_doors(a_f_mr: float, a_f_or: float, a_f_total: float, doors: List[Dict]) -> List[Dict]:

    def make_door_lv3(envelope, space_type, a_evlp):

        return {
            'name': envelope['name'] + '_' + space_type,
            'next_space': envelope['next_space'],
            'direction': envelope['direction'],
            'area': a_evlp,
            'space_type': space_type,
            'spec': copy.deepcopy(envelope['spec'])
        }

    return get_evlps_lv3_area(
        a_f_mr=a_f_mr,
        a_f_or=a_f_or,
        a_f_total=a_f_total,
        envelope=doors,
        make_evlp_lv3=make_door_lv3
    )


def get_heatbridges(a_f_mr: float, a_f_or: float, a_f_total: float, heatbridges: List[Dict]) -> List[Dict]:

    def make_heatbridge_lv3(heatbridge_lv2, space_type, l_evlp):

        return {
            'name': heatbridge_lv2['name'] + '_' + space_type,
            'next_space': heatbridge_lv2['next_space'],
            'direction': heatbridge_lv2['direction'],
            'space_type': space_type,
            'length': l_evlp,
            'spec': copy.deepcopy(heatbridge_lv2['spec']),
        }

    return get_evlps_lv3_length(
        a_f_mr=a_f_mr,
        a_f_or=a_f_or,
        a_f_total=a_f_total,
        envelope=heatbridges,
        make_evlp_lv3=make_heatbridge_lv3
    )


def get_earthfloor_perimeters(earthfloor_perimeters: List[Dict]) -> List[Dict]:

    return [
        {
            'name': p['name'],
            'next_space': p['next_space'],
            'direction': p['direction'],
            'length': p['length'],
            'space_type': 'underfloor',
            'spec': copy.deepcopy(p['spec']),
        }
        for p in earthfloor_perimeters]


def get_earthfloor_centers(earthfloor_centers: List[Dict]) -> List[Dict]:

    return [
        {
            'name': p['name'],
            'area': p['area'],
            'space_type': 'underfloor'
        }
        for p in earthfloor_centers]


def convert_spec(common, envelope):

    result = {
        'input_method': 'detail_with_room_usage'
    }

    if 'general_parts' in envelope:
        result['general_parts'] = get_general_parts(
            a_f_mr=common['main_occupant_room_floor_area'],
            a_f_or=common['other_occupant_room_floor_area'],
            a_f_total=common['total_floor_area'],
            general_parts=envelope['general_parts']
        )

    if 'windows' in envelope:
        result['windows'] = get_windows(
            a_f_mr=common['main_occupant_room_floor_area'],
            a_f_or=common['other_occupant_room_floor_area'],
            a_f_total=common['total_floor_area'],
            windows=envelope['windows']
        )

    if 'doors' in envelope:
        result['doors'] = get_doors(
            a_f_mr=common['main_occupant_room_floor_area'],
            a_f_or=common['other_occupant_room_floor_area'],
            a_f_total=common['total_floor_area'],
            doors=envelope['doors']
        )

    if 'heatbridges' in envelope:
        result['heatbridges'] = get_heatbridges(
            a_f_mr=common['main_occupant_room_floor_area'],
            a_f_or=common['other_occupant_room_floor_area'],
            a_f_total=common['total_floor_area'],
            heatbridges=envelope['heatbridges']
        )

    if 'earthfloor_perimeters' in envelope:
        result['earthfloor_perimeters'] = get_earthfloor_perimeters(envelope['earthfloor_perimeters'])

    if 'earthfloor_centers' in envelope:
        result['earthfloor_centers'] = get_earthfloor_centers(envelope['earthfloor_centers'])

    return result

