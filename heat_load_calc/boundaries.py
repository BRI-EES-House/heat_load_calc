import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

from heat_load_calc import response_factor, transmission_solar_radiation, shape_factor
from heat_load_calc.weather import Weather
from heat_load_calc.response_factor import ResponseFactor
from heat_load_calc.direction import Direction
from heat_load_calc.solar_shading import SolarShading
from heat_load_calc import outside_eqv_temp
from heat_load_calc import transmission_solar_radiation
from heat_load_calc import window
from heat_load_calc.window import Window


class BoundaryType(Enum):
    """
    境界の種類
    """

    # 'internal': 間仕切り
    INTERNAL = 'internal'

    # 'external_general_part': 外皮_一般部位
    EXTERNAL_GENERAL_PART = 'external_general_part'

    # 'external_transparent_part': 外皮_透明な開口部
    EXTERNAL_TRANSPARENT_PART = 'external_transparent_part'

    # 'external_opaque_part': 外皮_不透明な開口部
    EXTERNAL_OPAQUE_PART = 'external_opaque_part'

    # 'ground': 地盤
    GROUND = 'ground'


@dataclass
class Boundary:

    # ID
    id: int

    # 名称
    name: str

    # 副名称
    sub_name: str

    # 境界の種類
    t_b: BoundaryType

    # 面積, m2
    a_s: float

    # 温度差係数
    k_eo: float

    # 床か否か
    b_floor: bool

    # 室内侵入日射吸収の有無
    b_sol_abs: bool

    # 相当外気温度, ℃, [8760 * 4]
    theta_o_eqv_nspls: np.ndarray

    # 透過日射熱取得, W, [8760*4]
    q_trs_sol_nplus: np.ndarray

    # 応答係数データクラス
    rf: response_factor.ResponseFactor

    # 裏面温度に他の境界 j の等価室温が与える影響, [j, j]
    k_ei_js: List

    # 裏面温度に室の空気温度が与える影響
    k_s_r: float


class Boundaries:

    def __init__(self, id_r_is: np.ndarray, ds: List[Dict], w: Weather):
        """

        Args:
            id_r_is: 室のID, [i, 1]
            ds: 境界に関する辞書
            w: Weather クラス
        Notes:
            本来であれば Boundaries クラスにおいて境界に関する入力用辞書から読み込みを境界個別に行う。
            しかし、室内側表面放射熱伝達は室内側の形態係数によって値が決まり、ある室に接する境界の面積の組み合わせで決定されるため、
            境界個別に値を決めることはできない。（すべての境界の情報が必要である。）
            一方で、境界の集約を行うためには、応答係数を Boundary クラス生成時に求める必要があり、
            さらに応答係数の計算には裏面の表面放射・対流熱伝達率の値が必要となるため、
            Boundary クラスを生成する前に、予め室内側表面放射・対流熱伝達率を計算しておき、
            Boundary クラスを生成する時に必要な情報としておく。
        """

        # number of boundaries
        n_b = len(ds)

        # boundary id, [J]
        id_js = np.array([int(d['id']) for d in ds]).reshape(-1, 1)

        # connected foom id, [J]
        connected_room_id_js = np.array([b['connected_room_id'] for b in ds])

        # coefficient of relation between room i and boundary j / 室iと境界jの関係を表す係数（境界jから室iへの変換）, [I, J]
        p_is_js = _get_p_is_js(id_r_is=id_r_is, connected_room_id_js=connected_room_id_js)

        # surface area of boundary j / 境界jの面積, m2, [J, 1]
        a_s_js = np.array([_read_a_s(d=d, id=id_j) for (d, id_j) in zip(ds, id_js)]).reshape(-1, 1)

        # indoor surface radiant heat transfer coefficient of boundary j / 境界jの室内側表面放射熱伝達率, W/m2K, [J, 1]
        h_s_r_js = shape_factor.get_h_s_r_js(a_s_js=a_s_js, p_is_js=p_is_js)

        # indoor surface convection heat transfer coefficient of boundary j / 境界jの室内側表面対流熱伝達率, W/m2K, [J, 1]
        h_s_c_js = np.array([b['h_c'] for b in ds]).reshape(-1, 1)

        # 境界 j, [J]
        bss = [self._get_boundary(d=d, h_s_c_js=h_s_c_js, h_s_r_js=h_s_r_js, w=w, id_js=id_js) for d in ds]

        # GOUND の数
        n_ground =sum(bs.t_b == BoundaryType.GROUND for bs in bss)

        # id of boundary j, [J, 1]
        id_js = np.array([bs.id for bs in bss]).reshape(-1, 1)

        # name of boundary j, [J, 1]
        name_js = np.array([bs.name for bs in bss]).reshape(-1, 1)

        # sub name of boundary j, [J, 1]
        sub_name_js = np.array([bs.sub_name for bs in bss]).reshape(-1, 1)

        # is the boundary j floor ?, [J, 1]
        b_floor_js = np.array([bs.b_floor for bs in bss]).reshape(-1, 1)

        # is the boundary j ground ?, [J, 1]
        b_ground_js = np.array([bs.t_b == BoundaryType.GROUND for bs in bss]).reshape(-1, 1)

        # coefficient representing the effect of equivalent room temperature of other boundary j to the rear temperature of boundary j
        # 裏面温度に他の境界 j の等価室温が与える影響, [J, J]
        k_ei_js_js = np.array([bs.k_ei_js for bs in bss])

        # temperature difference coefficient of boundary j / 温度差係数, [J]
        k_eo_js = np.array([bs.k_eo for bs in bss]).reshape(-1, 1)

        # coefficient representing the effect of room air temperature i to the rear temperature of boundary j / 裏面温度に室の空気温度が与える影響, [J, I]
        k_s_r_js = np.array([bs.k_s_r for bs in bss])
        k_s_r_js_is = p_is_js.T * k_s_r_js[:, np.newaxis]

        # is inside solar radiation absorbed of boundary j / 室内侵入日射吸収の有無 (True:吸収する/False:吸収しない) 
        b_sol_abs_js = np.array([bs.b_sol_abs for bs in bss]).reshape(-1, 1)

        # the resistance from the inside surface of boundary j to the outside air, m2K/W, [J, 1]
        r_total_js = np.array([bs.rf.r_total for bs in bss]).reshape(-1, 1)

        # thermal transmittance coefficient of boundary j, W/m2K, [J, 1]
        u_js = 1.0 / (1.0 / (h_s_c_js + h_s_r_js) + r_total_js)

        # response factor of boundary j, [J, 1] or [J, M]
        phi_a0_js = np.array([bs.rf.rfa0 for bs in bss]).reshape(-1, 1)
        phi_a1_js_ms = np.array([bs.rf.rfa1 for bs in bss])
        phi_t0_js = np.array([bs.rf.rft0 for bs in bss]).reshape(-1, 1)
        phi_t1_js_ms = np.array([bs.rf.rft1 for bs in bss])
        r_js_ms = np.array([bs.rf.row for bs in bss])

        # outside equivalent temperature of boundary j, degree C, [J, N+1]
        theta_o_eqv_js_nspls = np.array([bs.theta_o_eqv_nspls for bs in bss])

        # transmitted solar radiation of boundary j, W, [J, N+1]
        q_trs_sol_js_nspls = np.array([bs.q_trs_sol_nplus for bs in bss])

        self._n_b = n_b
        self._connected_room_id_js = connected_room_id_js
        self._p_is_js = p_is_js
        self._p_js_is = p_is_js.T
        self._a_s_js = a_s_js
        self._h_s_r_js = h_s_r_js
        self._h_s_c_js = h_s_c_js
        self._n_ground = n_ground
        self._id_js = id_js
        self._name_js = name_js
        self._sub_name_js = sub_name_js
        self._b_floor_js = b_floor_js
        self._b_ground_js = b_ground_js
        self._k_ei_js_js = k_ei_js_js
        self._k_eo_js = k_eo_js
        self._k_s_r_js_is = k_s_r_js_is
        self._b_s_sol_abs_js = b_sol_abs_js
        self._u_js = u_js
        self._phi_a0_js = phi_a0_js
        self._phi_a1_js_ms = phi_a1_js_ms
        self._phi_t0_js = phi_t0_js
        self._phi_t1_js_ms = phi_t1_js_ms
        self._r_js_ms = r_js_ms
        self._theta_o_eqv_js_nspls = theta_o_eqv_js_nspls
        self._q_trs_sol_js_nspls = q_trs_sol_js_nspls

    @staticmethod
    def _get_boundary(d: Dict, h_s_c_js: np.ndarray, h_s_r_js: np.ndarray, w: Weather, id_js: np.ndarray) -> Boundary:
        """

        Args:
            d: dictionary of boundary j
            h_s_c_js: 境界jの室内側表面対流熱伝達率, W/m2K, [J, 1]
            h_s_r_js: 境界jの室内側表面放射熱伝達率, W/m2K, [J, 1]
            w: Weather クラス
            id_js: id of boundaries, [J]

        Returns:
            Boundary クラス
        """

        # ID of boundary j
        id_j = int(d['id'])

        # name of boundary j / 名前
        name_j = str(d['name'])

        # sub name of boundary j / 副名称
        sub_name_j = str(d['sub_name'])

        # type of boundary j / 境界の種類
        t_b_j = BoundaryType(d['boundary_type'])

        # surface area of boundary j/ 面積, m2
        a_s_j = _read_a_s(d=d, id=id_j)

        # temperature difference coefficient of boundary j / 温度差係数
        k_eo_j = _read_k_eo(d=d, id=id_j, t_b=t_b_j)

        # rear boundary index of boundary j
        j_rear_j = _read_j_rear(b=d, id=id_j, t_b=t_b_j, id_js=id_js)

        # is inside solar radiation absorbed of boundary j / 室内侵入日射吸収の有無 (True:吸収する/False:吸収しない)
        b_sol_abs_j = bool(d['is_solar_absorbed_inside'])

        # is boundary j floor / 床か否か(True:床/False:床以外)
        b_floor_j = bool(d['is_floor'])

        # is the sun striked to outside of boundary j / 外気側に日射が当たるか否か
        b_sun_strkd_out_j = _read_b_sun_strkd_out(d=d, id=id_j, t_b=t_b_j)
        
        # direction of boundary j / 方位
        t_drct_j = _read_t_drct(d=d, b_sun_strkd_out=b_sun_strkd_out_j)
        
        # solar shading of boundary j / 日よけ        
        ssp_j = _read_ssp(ssp_dict=d['solar_shading_part'], b_sun_strkd_out=b_sun_strkd_out_j, t_drct=t_drct_j)

        # solar absorption ratio at outside surface of boundary j / 境界jの室外側表面日射吸収率, -
        a_sol_j = _read_a_sol(d=d, id=id_j, t_b=t_b_j)

        # outside heat transfer resistance of boundary j / 室外側熱伝達抵抗, m2 K / W
        r_s_o_j = _read_r_s_o(d=d, id=id_j, t_b=t_b_j)

        # long wavelength emissivity at outside surface of boundary j, -
        eps_r_o_j = _read_eps_r_o(d=d, id=id_j, t_b=t_b_j)

        # standard heat transmittance coefficient (u value) of boundary j, W / ( m2 K )
        u_w_std_j = _get_u_std(d=d, id=id_j, t_b=t_b_j)

        # standard solar gain coefficient (eta value) of boundary j, -
        eta_w_std_j = _read_eta_std(d=d, id=id_j, t_b=t_b_j)

        # grazing area ratio fo boundary j, -
        r_a_w_g_j = _read_r_a_w_g(d=d, id=id_j, t_b=t_b_j)

        # grazing type of boundary j/ グレージングの種類
        t_glz_j = _read_t_glz(d=d, id=id_j, t_b=t_b_j)

        # window class of boundary j
        window_j = _get_window_class_j(t_b_j=t_b_j, u_w_std_j=u_w_std_j, eta_w_std_j=eta_w_std_j, t_glz_j=t_glz_j, r_a_w_g_j=r_a_w_g_j)

        # equivalent outside temperature of boundary i at step n, degree C, [N+1]
        theta_o_eqv_j_nspls = _get_theta_o_eqv_j_ns(t_b_j=t_b_j, w=w, b_sun_strkd_out_j=b_sun_strkd_out_j, t_drct_j=t_drct_j, a_sol_j=a_sol_j, eps_r_o_j=eps_r_o_j, r_s_o_j=r_s_o_j, ssp_j=ssp_j, u_w_std_j=u_w_std_j, window_j=window_j)

        # transmitted solar radiation of boundary j at step n, W, [N+1]
        q_trs_sol_j_nspls = _get_q_trs_sol_j_ns(t_b_j=t_b_j, w=w, b_sun_strkd_out_j=b_sun_strkd_out_j, t_drct_j=t_drct_j, a_s_j=a_s_j, ssp_j=ssp_j, window_j=window_j)

        # response factor of boundary j
        rf = _get_response_factor(d=d, h_s_c_js=h_s_c_js, h_s_r_js=h_s_r_js, id_j=id_j, t_b_j=t_b_j, j_rear_j=j_rear_j, r_s_o_j=r_s_o_j, u_w_std_j=u_w_std_j)
        
        # coefficient representing the effect of equivalent room temperature of other boundary j to the rear temperature of boundary j
        # 裏面温度に他の境界 j の等価室温が与える影響, [J]
        k_ei_js_j = _get_k_ei_js_j(id_js=id_js, t_b_j=t_b_j, j_rear_j=j_rear_j)

        # coefficient representing the effect of room air temperature to the rear temperature of boundary j / 裏面温度に室の空気温度が与える影響
        k_s_r_j = _get_k_s_r_j(t_b_j=t_b_j, k_eo_j=k_eo_j)


        return Boundary(
            id=id_j,
            name=name_j,
            sub_name=sub_name_j,
            t_b=t_b_j,
            a_s=a_s_j,
            k_eo=k_eo_j,
            b_floor=b_floor_j,
            b_sol_abs=b_sol_abs_j,
            theta_o_eqv_nspls=theta_o_eqv_j_nspls,
            q_trs_sol_nplus=q_trs_sol_j_nspls,
            rf=rf,
            k_ei_js=k_ei_js_j,
            k_s_r=k_s_r_j
        )


    @property
    def n_b(self) -> int:
        """number of boundaries / 境界の数"""
        return self._n_b

    @property
    def n_ground(self) -> int:
        """地盤の数"""
        return self._n_ground

    @property
    def id_js(self) -> np.ndarray:
        """境界jのID, [j, 1]"""
        return self._id_js

    @property
    def name_js(self) -> np.ndarray:
        """境界jの名前, [j, 1]"""
        return self._name_js

    @property
    def sub_name_js(self) -> np.ndarray:
        """境界jの名前2, [j, 1]"""
        return self._sub_name_js

    @property
    def p_is_js(self) -> np.ndarray:
        """coefficient of relation between room i and boundary j / 室iと境界jの関係を表す係数（境界jから室iへの変換）, [i, j]
        Notes:
            室iと境界jの関係を表す係数（境界jから室iへの変換）
            [[p_0_0 ... ... p_0_j]
             [ ...  ... ...  ... ]
             [p_i_0 ... ... p_i_j]]
        """
        return self._p_is_js

    @property
    def p_js_is(self) -> np.ndarray:
        """coefficient of relation between room i and boundary j / 室iと境界jの関係を表す係数（室iから境界jへの変換）
        Notes:
            [[p_0_0 ... p_0_i]
             [ ...  ...  ... ]
             [ ...  ...  ... ]
             [p_j_0 ... p_j_i]]
        """
        return self._p_js_is

    @property
    def b_floor_js(self) -> np.ndarray:
        """境界jが床かどうか, [j, 1]"""
        return self._b_floor_js

    @property
    def b_ground_js(self) -> np.ndarray:
        """境界jが地盤かどうか, [j, 1]"""
        return self._b_ground_js

    @property
    def k_ei_js_js(self) -> np.ndarray:
        """境界jの裏面温度に他の境界の等価室温が与える影響, [j, j]"""
        return self._k_ei_js_js
        
    @property
    def k_eo_js(self) -> np.ndarray:
        """境界jの裏面温度に外気温度が与える影響（温度差係数）, [j, 1]"""
        return self._k_eo_js

    @property
    def k_s_r_js_is(self) -> np.ndarray:
        """境界jの裏面温度に室温が与える影響, [j, i]"""
        return self._k_s_r_js_is

    @property
    def b_s_sol_abs_js(self) -> np.ndarray:
        """境界jの日射吸収の有無, [j, 1]"""
        return self._b_s_sol_abs_js

    @property
    def h_s_r_js(self) -> np.ndarray:
        """境界jの室内側表面放射熱伝達率, W/m2K, [j, 1]"""
        return self._h_s_r_js

    @property
    def h_s_c_js(self) -> np.ndarray:
        """境界jの室内側表面対流熱伝達率, W/m2K, [j, 1]"""
        return self._h_s_c_js

    @property
    def u_js(self) -> np.ndarray:
        """境界jにおけるシミュレーションに用いる表面熱伝達抵抗での熱貫流率, W/m2K, [j,1]"""
        return self._u_js

    @property
    def a_s_js(self) -> np.ndarray:
        """境界jの面積, m2, [j, 1]"""
        return self._a_s_js

    @property
    def phi_a0_js(self) -> np.ndarray:
        """境界jの吸熱応答係数の初項, m2K/W, [j, 1]"""
        return self._phi_a0_js

    @property
    def phi_a1_js_ms(self) -> np.ndarray:
        """境界jの項別公比法における項mの吸熱応答係数の第一項 , m2K/W, [j, 12]"""
        return self._phi_a1_js_ms

    @property
    def phi_t0_js(self) -> np.ndarray:
        """境界jの貫流応答係数の初項, [j, 1]"""
        return self._phi_t0_js

    @property
    def phi_t1_js_ms(self) -> np.ndarray:
        """境界jの項別公比法における項mの貫流応答係数の第一項, [j, 12]"""
        return self._phi_t1_js_ms

    @property
    def r_js_ms(self) -> np.ndarray:
        """境界jの項別公比法における項mの公比, [j, 12]"""
        return self._r_js_ms

    @property
    def theta_o_eqv_js_nspls(self) -> np.ndarray:
        """ステップ n の境界 j における相当外気温度, ℃, [J, N+1]"""
        return self._theta_o_eqv_js_nspls

    # TODO: 一部のテストを通すためだけに、後から上書きできる機能を作成した。将来的には消すこと。
    def set_theta_o_eqv_js_nspls(self, theta_o_eqv_js_nspls):
        self._theta_o_eqv_js_nspls = theta_o_eqv_js_nspls

    @property
    def q_trs_sol_js_nspls(self) -> np.ndarray:
        """transmitted solar heat gain of boundary j at step n, ステップnにおける境界jの透過日射熱取得, W, [J, N+1]"""
        return self._q_trs_sol_js_nspls

    def get_room_id_by_boundary_id(self, boundary_id: int):

        room_id = self._connected_room_id_js[self._get_index_by_id(boundary_id=boundary_id)]
    
        return room_id

    def _get_index_by_id(self, boundary_id: int) -> int:

        indices = [i for (i, id_b_j) in enumerate(self.id_js) if id_b_j == boundary_id]

        if len(indices) == 0:
            raise Exception("指定された boundary_id に一致する boundary が見つかりませんでした。")
        if len(indices) >1:
            raise Exception("指定された boundary_id に一致する boundary が複数見つかりました。")
        
        return indices[0]



def _get_p_is_js(id_r_is, connected_room_id_js):
    # 室iと境界jの関係を表す係数（境界jから室iへの変換）
    # [[p_0_0 ... ... p_0_j]
    #  [ ...  ... ...  ... ]
    #  [p_i_0 ... ... p_i_j]]

    p_is_js = [
        _get_p_is_j(id_r_is=id_r_is, connected_room_id_j=connected_room_id_j)
        for connected_room_id_j in connected_room_id_js
    ]

    p_is_js = np.array(p_is_js).T
    
    return p_is_js


def _get_p_is_j(id_r_is: np.ndarray, connected_room_id_j: int):

    p_is_j = np.zeros(id_r_is.size, dtype=int)
    p_is_j[_get_room_index(id_r_is=id_r_is, id=connected_room_id_j)] = 1
    return p_is_j


def _get_room_index(id_r_is: np.ndarray, id: int):
    """Get the index of rooms matched to the specify id.

    Args:
        id_r_is: list of the indices of rooms
        id: specified room id

    Raises:
        ValueError: There is no room index corresponding to the specified index.
        ValueError: Multiple indices were found corresponding to the specified index.

    Returns:
        the index of the room
    """

    matched_indices = [index for (index, id_r_i) in enumerate(id_r_is) if id_r_i == id]

    if len(matched_indices) == 0:
        raise ValueError("Boundary が接続する room のIDが存在しませんでした。")
    if len(matched_indices) > 1:
        raise ValueError("Boundary が接続する room のIDが複数存在しました。")
    
    return matched_indices[0]


def _read_j_rear(b: Dict, id: int, t_b: BoundaryType, id_js: np.ndarray) -> int:
    """Get the rear surface boundary index.

    Args:
        b: dictionary of boundries
        id: boundary id
        t_b: boundary type
        id_js: list of the boundaries, [J]

    Returns:
        rear surface boundary index
    Notes:
        This index is defined only in case of INTERNAL as type of boundary.
    """

    if t_b == BoundaryType.INTERNAL:
        rear_surface_boundary_id = int(b['rear_surface_boundary_id'])
        rear_boundary_index = _get_boundary_index(id_js=id_js, rear_surface_boundary_id=rear_surface_boundary_id, id=id)
        return rear_boundary_index
    else:
        return None


def _get_boundary_index(id_js: np.ndarray, rear_surface_boundary_id: int, id: int) -> int:
    """Get the boundary index matched to the specify id.

    Args:
        id_js: list of the indices of boundaries
        rear_surface_boundary_id: specified boundary id as rear surface
        id: id of this boundary

    Raises:
        ValueError: There is no boundary index corresponding to the specified index.
        ValueError: Multiple indices were found corresponding to the specified index.

    Returns:
        the boundary index
    """

    matched_indices = [index for (index, id_j) in enumerate(id_js) if id_j == rear_surface_boundary_id]

    if len(matched_indices) == 0:
        raise ValueError("境界(ID=" + str(id) + ")(間仕切りの場合)の裏面のIDとして指定する boundary ID 存在しませんでした。")
    if len(matched_indices) > 1:
        raise ValueError("境界(ID=" + str(id) + ")(間仕切りの場合)の裏面のIDとして指定する boundary ID が複数存在しました。")
    
    return matched_indices[0]


def _read_a_s(d: Dict, id: int) -> float:
    """Read the surface area.

    Args:
        d: dictionary of boundary
        id: boundary id
    Regurns:
        surface area, m2
    """

    # surface area / 表面積, m2
    a_s = float(d['area'])

    if a_s <= 0.0:
        raise ValueError("境界(ID=" + str(id) + ")の面積で0以下の値が指定されました。")
    
    return a_s


def _read_k_eo(d: Dict, id: int, t_b: BoundaryType) -> float:
    """Read the temperature difference coefficient.

    Args:
        d: dictionary of boundary
        id: boundary id
        t_b: boundary type

    Returns:
        temperature difference coefficient
    """

    if t_b in [
        BoundaryType.EXTERNAL_GENERAL_PART,
        BoundaryType.EXTERNAL_TRANSPARENT_PART,
        BoundaryType.EXTERNAL_OPAQUE_PART
    ]:
        k_eo = float(d['temp_dif_coef'])
    elif t_b == BoundaryType.GROUND:
        k_eo = 1.0
    elif t_b == BoundaryType.INTERNAL:
        k_eo = 0.0
    else:
        raise Exception()

    if k_eo > 1.0:
        raise ValueError("境界(ID=" + str(id) + ")の温度差係数で1.0を超える値が指定されました。")

    if k_eo < 0.0:
        raise ValueError("境界(ID=" + str(id) + ")の温度差係数で0.0を下回る値が指定されました。")
    
    return k_eo


def _read_b_sun_strkd_out(d: Dict, id: int, t_b: BoundaryType) -> bool:

    if t_b in [
        BoundaryType.EXTERNAL_GENERAL_PART,
        BoundaryType.EXTERNAL_TRANSPARENT_PART,
        BoundaryType.EXTERNAL_OPAQUE_PART
    ]:
        return bool(d['is_sun_striked_outside'])
    elif t_b in [
        BoundaryType.INTERNAL,
        BoundaryType.GROUND
    ]:
        return False
    else:
        raise Exception()


def _read_t_drct(d: Dict, b_sun_strkd_out: bool) -> Optional[Direction]:

    if b_sun_strkd_out:
        return Direction(d['direction'])
    else:
        return None


def _read_ssp(ssp_dict: Dict, b_sun_strkd_out: bool, t_drct: Direction) -> SolarShading:
    
    if b_sun_strkd_out:
        return SolarShading.create(ssp_dict=ssp_dict, direction=t_drct)
    else:
        return None


def _read_a_sol(d: Dict, id: int, t_b: BoundaryType) -> Optional[float]:
    """Get the solar absorption ratio at the outside surface of boundary j.

    Args:
        d: dictionary of boundary
        id: boundary id
        t_b: boundary type

    Returns:
        solar absorption ratio at outside surface of boundary
    """

    if t_b in [BoundaryType.EXTERNAL_GENERAL_PART, BoundaryType.EXTERNAL_OPAQUE_PART]:

        a_sol = float(d['outside_solar_absorption'])

        if a_sol < 0.0:
            raise ValueError("境界(ID=" + str(id) + ")の日射吸収率で0.0未満の値が指定されました。")

        if a_sol > 1.0:
            raise ValueError("境界(ID=" + str(id) + ")の日射吸収率で1.0より大の値が指定されました。")

        return a_sol

    elif t_b in [BoundaryType.INTERNAL, BoundaryType.EXTERNAL_TRANSPARENT_PART, BoundaryType.GROUND]:

        return None

    else:
        raise Exception()
        

def _read_r_s_o(d: Dict, id: int, t_b: BoundaryType) -> Optional[float]:
    """Get the outside heat transfer resistance.

    Args:
        d: dictionary of boundary
        id: boundary id
        t_b: boundary type

    Returns:
        outside heat transfer resistance, m2 K / W
    """

    if t_b in [BoundaryType.INTERNAL, BoundaryType.GROUND]:

        return None

    elif t_b in [BoundaryType.EXTERNAL_GENERAL_PART, BoundaryType.EXTERNAL_TRANSPARENT_PART, BoundaryType.EXTERNAL_OPAQUE_PART]:

        r_s_o = float(d['outside_heat_transfer_resistance'])

        if r_s_o <= 0.0:
            raise ValueError("境界(ID=" + str(id) + ")の室外側熱伝達抵抗で0.0以下の値が指定されました。")

        return r_s_o

    else:

        raise Exception()


def _read_eps_r_o(d: Dict, id: int, t_b: BoundaryType) -> Optional[float]:
    """Get the long wavelength emissivity at the outside surface of boundary j.

    Args:
        d: dictionary of boundary
        id: boundary id
        t_b: boundary type

    Returns:
        long wavelength emissivity at outside surface of boundary
    """
    
    if t_b in [BoundaryType.INTERNAL, BoundaryType.GROUND]:
    
        return None
    
    elif t_b in [BoundaryType.EXTERNAL_GENERAL_PART, BoundaryType.EXTERNAL_TRANSPARENT_PART, BoundaryType.EXTERNAL_OPAQUE_PART]:
    
        eps_r = float(d['outside_emissivity'])

        if eps_r > 1.0:
            raise ValueError("境界(ID=" + str(id) + ")の室外側長波長放射率で1.0を超える値が指定されました。")

        if eps_r < 0.0:
            raise ValueError("境界(ID=" + str(id) + ")の室外側長波長放射率で0.0を下回る値が指定されました。")

        return eps_r
    
    else:
    
        raise Exception()


def _get_u_std(d: Dict, id: int, t_b: BoundaryType) -> Optional[float]:
    """Get the standard u value of boundary.

    Args:
        d: dictionary of boundary
        id: boundary id
        t_b: boundary type

    Returns:
        standard u value of boundary
    """

    if t_b in [BoundaryType.EXTERNAL_TRANSPARENT_PART, BoundaryType.EXTERNAL_OPAQUE_PART]:

        u_nmnl = float(d['u_value'])

        if u_nmnl <= 0.0:
            raise ValueError("境界(ID=" + str(id) + ")の熱貫流率で0.0以下の値が指定されました。")
        
        return u_nmnl
    
    elif t_b in [BoundaryType.EXTERNAL_GENERAL_PART, BoundaryType.INTERNAL, BoundaryType.GROUND]:
        
        return None
        
    else:
        raise Exception()


def _read_eta_std(d: Dict, id: int, t_b: BoundaryType) -> Optional[float]:
    """Get the standard eta value of the boundary.

    Args:
        d: dictionary of boundary
        id: boundary id
        t_b: boundary type

    Returns:
        standard eta value of boundary
    """

    if t_b == BoundaryType.EXTERNAL_TRANSPARENT_PART:

        eta_value = float(d['eta_value'])

        if eta_value <= 0.0:
            raise ValueError("境界(ID=" + str(id) + ")の日射熱取得率で0.0以下の値が指定されました。")

        return eta_value

    elif t_b in [BoundaryType.EXTERNAL_GENERAL_PART, BoundaryType.EXTERNAL_OPAQUE_PART, BoundaryType.INTERNAL, BoundaryType.GROUND]:

        return None

    else:
        raise Exception()

        
def _read_r_a_w_g(d: Dict, id: int, t_b: BoundaryType) -> Optional[float]:
    """Get the ratio of the grazing area to the opening area.

    Args:
        d: dictionary of boundary
        id: boundary id
        t_b: boundary type

    Returns:
        ratio of the grazing area to the opening area
    """
    
    if t_b == BoundaryType.EXTERNAL_TRANSPARENT_PART:

        # 開口部の面積に対するグレージングの面積の比率
        r_a_w_g = d['glass_area_ratio']
        
        if r_a_w_g < 0.0:
            raise ValueError("境界(ID=" + str(id) + ")の開口部の面積に対するグレージング面積の比率で0.0未満の値が指定されました。")
        
        if r_a_w_g > 1.0:
            raise ValueError("境界(ID=" + str(id) + ")の開口部の面積に対するグレージング面積の比率で1.0より大の値が指定されました。")
        
        return r_a_w_g
    
    elif t_b in [BoundaryType.EXTERNAL_GENERAL_PART, BoundaryType.EXTERNAL_OPAQUE_PART, BoundaryType.INTERNAL, BoundaryType.GROUND]:

        return None


def _read_t_glz(d: Dict, id: int, t_b: BoundaryType) -> Optional[window.GlassType]:
    """Get the type of the grazing of the boundary.

    Args:
        d: dictionary of boundary
        id: boundary id
        t_b: boundary type

    Returns:
        type of grazing of boundary
    """

    if t_b == BoundaryType.EXTERNAL_TRANSPARENT_PART:

        return window.GlassType(d['incident_angle_characteristics'])
    
    elif t_b in [BoundaryType.EXTERNAL_GENERAL_PART, BoundaryType.EXTERNAL_OPAQUE_PART, BoundaryType.INTERNAL, BoundaryType.GROUND]:
        
        return None
    else:

        raise Exception()


def _get_window_class_j(t_b_j: BoundaryType, u_w_std_j: Optional[float], eta_w_std_j: Optional[float], t_glz_j: Optional[window.GlassType], r_a_w_g_j: Optional[float]) -> Optional[Window]:

    if t_b_j in [BoundaryType.EXTERNAL_GENERAL_PART, BoundaryType.EXTERNAL_OPAQUE_PART, BoundaryType.INTERNAL, BoundaryType.GROUND]:
        
        return None
    
    elif t_b_j == BoundaryType.EXTERNAL_TRANSPARENT_PART:
    
        return Window(u_w_std_j=u_w_std_j, eta_w_std_j=eta_w_std_j, t_glz_j=t_glz_j, r_a_w_g_j=r_a_w_g_j)

    else:

        raise Exception()


def _get_theta_o_eqv_j_ns(
    t_b_j: BoundaryType,
    w: Weather,
    b_sun_strkd_out_j: Optional[bool],
    t_drct_j: Optional[Direction],
    a_sol_j: Optional[float],
    eps_r_o_j: Optional[float],
    r_s_o_j: Optional[float],
    ssp_j: Optional[SolarShading],
    u_w_std_j: Optional[float],
    window_j: Optional[Window]
) -> np.ndarray:
    """Calculate the equivalent outside temperature of boundary j at step n.

    Args:
        t_b_j: type of boundary j
        w: weather class
        b_sun_strkd_out_j: is the sun striked to boundary j
        t_drct_j: direction of boundary j
        a_sol_j: solar absorption ratio of boundary j, -
        eps_r_o_j: long wavelength emissivity of boundary j, -
        r_s_o_j: thermal resistance at the outside surface of boundary j, m2 K / W
        ssp_j: solar shading part class of boundary j
        u_w_std_j: standard heat transmittance coefficient (U value) of boundary j, W / m2 K
        window_j: window class of boundary j

    Returns:
        equivalent outside temperature of boundary j at step n, degree C, [N+1]
    """
    
    if t_b_j == BoundaryType.INTERNAL:

        return outside_eqv_temp.get_theta_o_eqv_j_ns_for_internal(w=w)

    elif t_b_j in [BoundaryType.EXTERNAL_GENERAL_PART, BoundaryType.EXTERNAL_OPAQUE_PART]:

        if b_sun_strkd_out_j:
        
            return outside_eqv_temp.get_theta_o_eqv_j_ns_for_external_general_part_and_external_opaque_part(
                t_drct_j=t_drct_j, a_sol_j=a_sol_j, eps_r_o_j=eps_r_o_j, r_s_o_j=r_s_o_j, ssp_j=ssp_j, w=w
            )

        else:

            return outside_eqv_temp.get_theta_o_eqv_j_ns_for_external_not_sun_striked(w=w)  

    elif t_b_j == BoundaryType.EXTERNAL_TRANSPARENT_PART:

        if b_sun_strkd_out_j:

            return outside_eqv_temp.get_theta_o_eqv_j_ns_for_external_transparent_part(
                t_drct_j=t_drct_j, eps_r_o_j=eps_r_o_j, r_s_o_j=r_s_o_j, u_w_std_j=u_w_std_j, ssp_j=ssp_j, window_j=window_j, w=w
            )

        else:

            return outside_eqv_temp.get_theta_o_eqv_j_ns_for_external_not_sun_striked(w=w)

    elif t_b_j == BoundaryType.GROUND:

        return outside_eqv_temp.get_theta_o_eqv_j_ns_for_ground(w=w)

    else:

        raise Exception()


def _get_q_trs_sol_j_ns(t_b_j: BoundaryType, w: Weather, b_sun_strkd_out_j: Optional[bool], t_drct_j: Optional[Direction], a_s_j: float, ssp_j: Optional[SolarShading], window_j: Optional[Window]) -> np.ndarray:
    """Calculate the transmitted solar radiation of boundary j at step n

    Args:
        t_b_j: type of boundary j
        w: weather class
        b_sun_strkd_out_j: is the sun striked at boundary j
        t_drct_j: direction of boundary j
        a_s_j: solar absorption ratio of boundary j
        ssp_j: solar shading part class of boundary j
        window_j: window class of boundary j

    Returns:
        transmitted solar radiation of boundary j at step n, W, [N+1]
    """

    if t_b_j in [BoundaryType.INTERNAL, BoundaryType.EXTERNAL_GENERAL_PART, BoundaryType.EXTERNAL_OPAQUE_PART, BoundaryType.GROUND]:

        return transmission_solar_radiation.get_q_trs_sol_j_ns_for_not(w=w)

    elif t_b_j == BoundaryType.EXTERNAL_TRANSPARENT_PART:

        if b_sun_strkd_out_j:

            return transmission_solar_radiation.get_q_trs_sol_j_ns_for_transparent_sun_striked(
                t_drct_j=t_drct_j, a_s_j=a_s_j, ssp_j=ssp_j, window_j=window_j, w=w
            )
    
        else:

            return transmission_solar_radiation.get_q_trs_sol_j_ns_for_not(w=w)
    
    else:

        raise Exception()


def _read_r_i_std_j(d: Dict, boundary_id: int) -> float:
    """
    室内側熱伝達抵抗を取得する。
    Args:
        d: 境界の辞書
        boundary_id: 境界のID

    Returns:
        室内側熱伝達抵抗, m2K/W

    """

    # 室内側熱伝達抵抗, m2K/W
    r_i = float(d['inside_heat_transfer_resistance'])

    if r_i <= 0.0:
        raise ValueError("境界(ID=" + str(boundary_id) + ")の室内側熱伝達抵抗で0.0以下の値が指定されました。")

    return r_i


def _get_response_factor(d: Dict, h_s_c_js: np.ndarray, h_s_r_js: np.ndarray, id_j: int, t_b_j: BoundaryType, j_rear_j: Optional[int], r_s_o_j: Optional[float], u_w_std_j: Optional[float]) -> ResponseFactor:
    """Get response factor of boundary j.

    Args:
        d: dictionary of boundary j
        h_s_c_js: indoor surface convection heat transfer coefficient of boundary j, W/m2K, [J, 1]
        h_s_r_js: indoor surface radiation heat transfer coefficient of boundary j, W/m2K, [J, 1]
        id_j: id of boundary j
        t_b_j: typoe of boundary j
        j_rear_j: boundary index j of the rear side of boundary j
        r_s_o_j: outside heat transfer resistance of boundary j, m2 K / W
        u_w_std_j: standard heat transmittance coefficient (U value) of boundary j, W/m2K

    Returns:
        response factor class
    """


    if t_b_j == BoundaryType.INTERNAL:

        c_j_ls = np.array([_read_cs_j_l(layer=layer, id=id, layer_id=l) for (l, layer) in enumerate(d['layers'])])
        r_j_ls = np.array([_read_rs_j_l(layer=layer, id=id, layer_id=l) for (l, layer) in enumerate(d['layers'])])

        h_s_c_rear_j = h_s_c_js[j_rear_j, 0]
        h_s_r_rear_j = h_s_r_js[j_rear_j, 0]

        r_rear_j = 1.0 / (h_s_c_rear_j + h_s_r_rear_j)

        return ResponseFactor.create_for_unsteady_not_ground(cs=c_j_ls, rs=r_j_ls, r_o=r_rear_j)

    elif t_b_j == BoundaryType.EXTERNAL_GENERAL_PART:

        c_j_ls = np.array([_read_cs_j_l(layer=layer, id=id, layer_id=l) for (l, layer) in enumerate(d['layers'])])
        r_j_ls = np.array([_read_rs_j_l(layer=layer, id=id, layer_id=l) for (l, layer) in enumerate(d['layers'])])

        return ResponseFactor.create_for_unsteady_not_ground(cs=c_j_ls, rs=r_j_ls, r_o=r_s_o_j)

    elif t_b_j in [BoundaryType.EXTERNAL_TRANSPARENT_PART, BoundaryType.EXTERNAL_OPAQUE_PART]:

        r_i_std_j = _read_r_i_std_j(d=d, boundary_id=id_j)

        return ResponseFactor.create_for_steady(u_w=u_w_std_j, r_i=r_i_std_j)

    elif t_b_j == BoundaryType.GROUND:

        c_j_ls = np.array([_read_cs_j_l(layer=layer, id=id, layer_id=l) for (l, layer) in enumerate(d['layers'])])
        r_j_ls = np.array([_read_rs_j_l(layer=layer, id=id, layer_id=l) for (l, layer) in enumerate(d['layers'])])

        return ResponseFactor.create_for_unsteady_ground(cs=c_j_ls, rs=r_j_ls)

    else:

        raise KeyError()


def _read_cs_j_l(layer: Dict, id: int, layer_id: int) -> float:

    cs_j_l = float(layer['thermal_capacity'])

    if cs_j_l < 0.0:
        raise ValueError("境界(ID=" + str(id) + ")の層(ID=" + str(layer_id) + ")の熱容量で0.0未満の値が指定されました。")

    return cs_j_l


def _read_rs_j_l(layer: Dict, id: int, layer_id: int) -> float: 

    rs_j_l = float(layer['thermal_resistance'])

    if rs_j_l <= 0.0:
        raise ValueError("境界(ID=" + str(id) + ")の層(ID=" + str(layer_id) + ")の熱抵抗で0.0以下の値が指定されました。")

    return rs_j_l


def _get_k_ei_js_j(id_js: np.ndarray, t_b_j: BoundaryType, j_rear_j: Optional[int]) -> np.ndarray:

    k_ei_js_j = np.zeros_like(id_js, dtype=float).flatten()

    if t_b_j in [
        BoundaryType.EXTERNAL_OPAQUE_PART,
        BoundaryType.EXTERNAL_TRANSPARENT_PART,
        BoundaryType.EXTERNAL_GENERAL_PART,
        BoundaryType.GROUND
    ]:
        pass

    elif t_b_j == BoundaryType.INTERNAL:
        # 室内壁の場合にk_ei_jsを登録する。
        k_ei_js_j[j_rear_j] = 1.0

    else:
        raise Exception()
    
    return k_ei_js_j


def _get_k_s_r_j(t_b_j: BoundaryType, k_eo_j: Optional[float]) -> Optional[float]:
    """Get the coefficient representing the effect of the room air temperature to the rear temperature of boundary j.

    Args:
        t_b_j: type of boundary j
        k_eo_j: temperature difference coefficient of oundary j

    Returns:
        coefficient representing the effect of room air temperature to rear temperature of boundary j
    """

    if t_b_j in [
        BoundaryType.EXTERNAL_OPAQUE_PART,
        BoundaryType.EXTERNAL_TRANSPARENT_PART,
        BoundaryType.EXTERNAL_GENERAL_PART
    ]:
        
        return round(1.0 - k_eo_j, 2)

    elif t_b_j in [BoundaryType.INTERNAL, BoundaryType.GROUND]:

        return 0.0

    else:
        raise Exception()
