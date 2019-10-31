
# general_part_type: 一般部位の種類を表し、以下の値をとる
#   ceiling: 天井
#   roof: 屋根
#   wall: 壁
#   floor: 床
#   boundary_wall: 界壁
#   upward_boundary_floor: 上界側界床
#   downward_boundary_floor: 下界側界床

# next_space: 隣接空間の種類を表し、以下の値をとる
#   outdoor: 外気
#   open_space: 外気に通じる空間
#   closed_space: 外気に通じていない空間
#   open_underfloor: 外気に通じる床裏
#   air_conditioned: 住戸及び住戸と同様の熱的環境の空間
#   closed_underfloor: 外気に通じていない床裏


def get_r_surf(general_part_type: str, next_space: str) -> (float, float):
    """
    表面熱伝達抵抗を取得する。

    Args:
        general_part_type: 一般部位の種類
        next_space: 隣接空間の種類

    Returns:
        表面熱伝達抵抗, m2K/W
            (1) 室内側
            (2) 室外側
    """

    if general_part_type == 'roof':

        if next_space == 'outdoor':
            return 0.09, 0.04
        else:
            return 0.09, 0.09

    elif general_part_type == 'ceiling':

        if next_space == 'outdoor':
            raise ValueError('「部位の種類」が「天井」の場合に「外気の種類」として「外気」は選択できません。')
        else:
            return 0.09, 0.09

    elif general_part_type == 'wall':

        if next_space == 'outdoor':
            return 0.11, 0.04
        else:
            return 0.11, 0.11

    elif general_part_type == 'floor':

        if next_space == 'outdoor':
            return 0.15, 0.04
        else:
            return 0.15, 0.15

    elif general_part_type == 'boundary_wall':

        if next_space == 'air_conditioned':
            return 0.11, 0.11
        else:
            raise ValueError('「部位の種類」が「界壁」の場合は「外気の種類」に「住戸及び住戸と同様の熱的環境の空間」を指定する必要があります。')

    elif general_part_type == 'upward_boundary_floor':

        if next_space == 'air_conditioned':
            return 0.09, 0.09
        else:
            raise ValueError('「部位の種類」が「上階側界床」の場合は「外気の種類」に「住戸及び住戸と同様の熱的環境の空間」を指定する必要があります。')

    elif general_part_type == 'downward_boundary_floor':

        if next_space == 'air_conditioned':
            return 0.15, 0.15
        else:
            raise ValueError('「部位の種類」が「下界側界床」の場合は「外気の種類」に「住戸及び住戸と同様の熱的環境の空間」を指定する必要があります。')
    else:

        raise ValueError()