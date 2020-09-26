"""
省エネ基準に基づく住宅情報を保持するクラス
"""

from typing import Dict, List
import abc

from heat_load_calc.external import factor_h
from heat_load_calc.external import factor_nu
from heat_load_calc.convert import factor_f


class EesHouse:

    def __init__(self):
        pass

    @classmethod
    def make_ees_house(cls, d: Dict):
        pass


class IArea(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def area(self):
        pass


class IGetQ(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_q(self, region: int):
        pass


class IGetM(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_m(self, region: int, season: str):
        pass


class GeneralPartSpec:

    def __init__(self, structure: str, u_value_other=None):

        self._structure = structure
        self._u_value_other = u_value_other

    @classmethod
    def make_general_part_spec(cls, d: Dict):

        structure = d['structure']

        if structure == 'other':
            return GeneralPartSpec(structure=d['structure'], u_value_other=d['u_value_other'])
        else:
            return GeneralPartSpec(structure=d['structure'])

    def get_u(self):

        if self._structure == 'other':
            return self._u_value_other
        else:
            raise NotImplementedError()

    def get_eta(self):

        return 0.034 * self.get_u()

    def get_as_dict(self):

        if self._structure == 'other':
            return {
                'structure': self._structure,
                'u_value_other': self._u_value_other
            }
        else:
            raise NotImplementedError()


class GeneralPartNoSpec(IArea):
    """
    「部位の仕様」情報を保持しない一般部位クラス
    """

    def __init__(
            self,
            name: str,
            general_part_type: str,
            next_space: str,
            direction: str,
            area: float,
            space_type: str,
            sunshade: factor_f.SunshadeOpaque
    ):
        """
        Args:
            name: 名称
            general_part_type: 種類
            next_space: 隣接する空間の種類
            direction: 方位
            area: 面積, m2
            space_type: 接する室の用途
            sunshade: 日よけ
        """

        self._name = name
        self._general_part_type = general_part_type
        self._next_space = next_space
        self._direction = direction
        self._area = area
        self._space_type = space_type
        self._sunshade = sunshade

    @property
    def name(self) -> str:
        """
        名前を取得する。
        Returns:
            名前
        """
        return self._name

    @property
    def general_part_type(self) -> str:
        """
        種類を取得する。
        Returns:
            種類
        """

        return self._general_part_type

    @property
    def next_space(self) -> str:
        """
        隣接する空間の種類を取得する。
        Returns:
            隣接する空間の種類
        """

        return self._next_space

    @property
    def direction(self) -> str:
        """
        方位を取得する。
        Returns:
            方位
        """

        return self._direction

    @property
    def area(self) -> float:
        """
        面積を取得する。
        Returns:
            面積, m2
        """

        return self._area

    @property
    def space_type(self) -> str:
        """
        接する室の用途を取得する。
        Returns:
            接する室の用途
        """

        return self._space_type

    @property
    def sunshade(self) -> factor_f.SunshadeOpaque:
        """
        日よけ（不透明部位）を取得する。
        Returns:
            日よけ（不透明部位）
        """
        return self._sunshade

    def get_h(self, region) -> float:
        """
        温度差係数を取得する。
        Args:
            region: 地域の区分
        Returns:
            温度差係数
        """

        return factor_h.get_h(region=region, next_space=self._next_space)

    def get_nu(self, region: int, season: str):
        """
        方位係数を取得する。
        Args:
            region: 地域の区分
            season: 期間
        Returns:
            方位係数
        """

        if self._next_space == 'outdoor':
            return factor_nu.get_nu(region=region, season=season, direction=self._direction)
        else:
            return 0.0


class GeneralPart(GeneralPartNoSpec, IArea, IGetQ, IGetM):
    """
    一般部位
    """

    def __init__(
            self,
            name: str,
            general_part_type: str,
            next_space: str,
            direction: str,
            area: float,
            space_type: str,
            sunshade: factor_f.SunshadeOpaque,
            general_part_spec: GeneralPartSpec
    ):
        """
        Args:
            name: 名称
            general_part_type: 種類
            next_space: 隣接する空間の種類
            direction: 方位
            area: 面積, m2
            space_type: 接する室の用途
            sunshade: 日よけ
            general_part_spec: 仕様
        """

        super().__init__(
            name=name,
            general_part_type=general_part_type,
            next_space=next_space,
            direction=direction,
            area=area,
            space_type=space_type,
            sunshade=sunshade
        )
        self._general_part_spec = general_part_spec

    @classmethod
    def make_general_part(cls, d: Dict):
        """
        一般部位に関する辞書からGeneralPartクラスをインスタンス化する。
        Args:
            d: 一般部位に関する辞書
        Returns:
            GeneralPart クラス
        """

        return GeneralPart(
            name=d['name'],
            general_part_type=d['general_part_type'],
            next_space=d['next_space'],
            direction=d['direction'],
            area=d['area'],
            space_type=d['space_type'],
            sunshade=factor_f.SunshadeOpaque.make_sunshade_opaque(d=d['sunshade']),
            general_part_spec=GeneralPartSpec.make_general_part_spec(d=d['spec'])
        )

    @classmethod
    def make_general_parts(cls, ds: List[Dict]):
        """
        一般部位に関する辞書のリストからGeneralPartクラスのリストをインスタンス化する。
        Args:
            ds: 一般部位に関する辞書のリスト
        Returns:
            GeneralPart クラスのリスト
        """

        return [GeneralPart.make_general_part(d) for d in ds]

    def get_u(self) -> float:
        """
        U値を取得する。
        Returns:
            U値, W/m2K
        """

        return self._general_part_spec.get_u()

    def get_q(self, region: int) -> float:
        """
        q値を取得する。
        Args:
            region: 地域の区分
        Returns:
            q値, W/K
        """

        return self.area * self.get_u() * self.get_h(region=region)

    def get_eta(self) -> float:
        """
        η値を取得する。
        Returns:
            η値, (W/m2)/(W/m2)
        """

        return self._general_part_spec.get_eta()

    def get_m(self, region: int, season: str) -> float:
        """
        m値を取得する。
        Args:
            region: 地域の区分
            season: 期間
        Returns:
            m値, W/(W/m2)
        """

        return self._area * self.get_eta() * self.get_nu(region=region, season=season)

    def get_as_dict(self):

        return {
            'name': self._name,
            'general_part_type': self._general_part_type,
            'next_space': self._next_space,
            'direction': self._direction,
            'area': self._area,
            'space_type': self.space_type,
            'spec': self._general_part_spec.get_as_dict(),
            'sunshade': self.sunshade.get_as_dict()
        }


class WindowSpec:

    def __init__(
            self,
            window_type: str,
            windows: List[Dict],
            attachment_type: str,
            is_windbreak_room_attached,
            is_sunshade_input
    ):

        self._window_type = window_type
        self._windows = windows
        self._attachment_type = attachment_type
        self._is_windbreak_room_attached = is_windbreak_room_attached
        self._is_sunshade_input = is_sunshade_input

    @classmethod
    def make_window_spec(cls, d: Dict):

        return WindowSpec(
            window_type=d['window_type'],
            windows=d['windows'],
            attachment_type=d['attachment_type'],
            is_windbreak_room_attached=d['is_windbreak_room_attached'],
            is_sunshade_input=d['is_sunshade_input']
        )

    def get_u(self):

        if self._window_type == 'single':
            window = self._windows[0]
            if window['u_value_input_method'] == 'u_value_directly':
                return window['u_value']
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

    def get_eta_d(self, season: str):

        if self._window_type == 'single':
            window = self._windows[0]
            if window['eta_value_input_method'] == 'eta_d_value_directly':
                if season == 'heating':
                    return window['eta_d_h_value']
                elif season == 'cooling':
                    return window['eta_d_c_value']
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

    def get_as_dict(self):

        return {
            'window_type': self._window_type,
            'windows': self._windows,
            'attachment_type': self._attachment_type,
            'is_windbreak_room_attached': self._is_windbreak_room_attached,
            'is_sunshade_input': self._is_sunshade_input
        }


class WindowNoSpec(IArea):
    """
    「部位の仕様」情報を保持しない大部分がガラスで構成される窓等の開口部
    """

    def __init__(
            self,
            name: str,
            next_space: str,
            direction: str,
            area: float,
            space_type: str,
            sunshade: factor_f.SunshadeTransient
    ):
        """
        Args:
            name: 名称
            next_space: 隣接する空間の種類
            direction: 方位
            area: 面積, m2
            space_type: 接する室の用途
            sunshade: 日よけ
        """

        self._name = name
        self._next_space = next_space
        self._direction = direction
        self._area = area
        self._space_type = space_type
        self._sunshade = sunshade

    @property
    def name(self) -> str:
        """
        名前を取得する。
        Returns:
            名前
        """
        return self._name

    @property
    def next_space(self) -> str:
        """
        隣接する空間の種類を取得する。
        Returns:
            隣接する空間の種類
        """

        return self._next_space

    @property
    def direction(self) -> str:
        """
        方位を取得する。
        Returns:
            方位
        """

        return self._direction

    @property
    def area(self) -> float:
        """
        面積を取得する。
        Returns:
            面積, m2
        """

        return self._area

    @property
    def space_type(self) -> str:
        """
        接する室の用途を取得する。
        Returns:
            接する室の用途
        """

        return self._space_type

    @property
    def sunshade(self) -> factor_f.SunshadeTransient:
        """
        日よけ（不透明部位）を取得する。
        Returns:
            日よけ（不透明部位）
        """
        return self._sunshade

    def get_h(self, region: int):
        """
        温度差係数を取得する。
        Args:
            region: 地域の区分
        Returns:
            温度差係数
        """

        return factor_h.get_h(region=region, next_space=self._next_space)

    def get_nu(self, region: int, season: str):
        """
        方位係数を取得する。
        Args:
            region: 地域の区分
            season: 期間
        Returns:
            方位係数
        """

        if self._next_space == 'outdoor':
            return factor_nu.get_nu(season=season, region=region, direction=self._direction)
        else:
            return 0.0

    def get_f(self, region: int, season: str):
        """
        日射熱取得補正係数を計算する。
        Args:
            region: 地域の区分
            season: 期間
        Returns:
            日射熱取得補正係数
        """
        return self._sunshade.get_f(region=region, season=season, direction=self._direction)


class Window(WindowNoSpec, IArea, IGetQ, IGetM):
    """
    大部分がガラスで構成される窓等の開口部
    """

    def __init__(
            self,
            name: str,
            area: float,
            next_space: str,
            direction: str,
            space_type: str,
            sunshade: factor_f.SunshadeTransient,
            window_spec: WindowSpec
    ):
        """
        Args:
            name: 名称
            area: 面積, m2
            next_space: 隣接する空間の種類
            direction: 方位
            window_spec: 仕様
        """

        super().__init__(
            name=name,
            next_space=next_space,
            direction=direction,
            area=area,
            space_type=space_type,
            sunshade=sunshade
        )

        self._window_spec = window_spec

    @classmethod
    def make_window(cls, d: Dict):
        """
        大部分がガラスで構成される窓等の開口部に関する辞書からWindowクラスをインスタンス化する。
        Args:
            d: 大部分がガラスで構成される窓等の開口部に関する辞書
        Returns:
            Window クラス
        """

        return Window(
            name=d['name'],
            area=d['area'],
            next_space=d['next_space'],
            direction=d['direction'],
            space_type=d['space_type'],
            sunshade=factor_f.SunshadeTransient.make_sunshade_transient(d=d['sunshade']),
            window_spec=WindowSpec.make_window_spec(d=d['spec'])
        )

    @classmethod
    def make_windows(cls, ds: List[Dict]):
        """
        大部分がガラスで構成される窓等の開口部に関する辞書のリストからWindowクラスのリストをインスタンス化する。
        Args:
            ds: 大部分がガラスで構成される窓等の開口部に関する辞書のリスト
        Returns:
            Window クラスのリスト
        """

        return [Window.make_window(d) for d in ds]

    def get_u(self):
        return self._window_spec.get_u()

    def get_q(self, region: int):
        return self.area * self.get_u() * self.get_h(region=region)

    def get_eta_d(self, season: str):
        return self._window_spec.get_eta_d(season=season)

    def get_m(self, region: int, season: str) -> float:
        return self.get_eta_d(season=season) \
               * self.area \
               * self.get_f(region=region, season=season) \
               * self.get_nu(region=region, season=season)

    def get_as_dict(self):

        return {
            'name': self._name,
            'next_space': self._next_space,
            'direction': self._direction,
            'area': self._area,
            'space_type': self.space_type,
            'sunshade': self.sunshade.get_as_dict(),
            'spec': self._window_spec.get_as_dict()
        }


class DoorSpec:

    def __init__(self, u_value: float):

        self._u_value = u_value

    @classmethod
    def make_door_spec(cls, d: dict):

        return DoorSpec(u_value=d['u_value'])

    def get_u(self):
        return self._u_value

    def get_eta(self):

        return 0.034 * self.get_u()

    def get_as_dict(self):

        return {
            'u_value': self._u_value
        }


class DoorNoSpec(IArea):
    """
    「部位の仕様」情報を保持しない大部分がガラスで構成されないドア等の開口部
    """

    def __init__(
            self,
            name: str,
            next_space: str,
            direction: str,
            area: float,
            space_type: str,
            sunshade: factor_f.SunshadeOpaque
    ):
        """
        Args:
            name: 名称
            next_space: 隣接する空間の種類
            direction: 方位
            area: 面積, m2
            space_type: 接する室の用途
            sunshade: 日よけ
        """

        self._name = name
        self._next_space = next_space
        self._direction = direction
        self._area = area
        self._space_type = space_type
        self._sunshade = sunshade

    @property
    def name(self) -> str:
        """
        名前を取得する。
        Returns:
            名前
        """
        return self._name

    @property
    def next_space(self) -> str:
        """
        隣接する空間の種類を取得する。
        Returns:
            隣接する空間の種類
        """

        return self._next_space

    @property
    def direction(self) -> str:
        """
        方位を取得する。
        Returns:
            方位
        """

        return self._direction

    @property
    def area(self) -> float:
        """
        面積を取得する。
        Returns:
            面積, m2
        """

        return self._area

    @property
    def space_type(self) -> str:
        """
        接する室の用途を取得する。
        Returns:
            接する室の用途
        """

        return self._space_type

    @property
    def sunshade(self) -> factor_f.SunshadeOpaque:
        """
        日よけ（不透明部位）を取得する。
        Returns:
            日よけ（不透明部位）
        """
        return self._sunshade

    def get_h(self, region: int):
        """
        温度差係数を取得する。
        Args:
            region: 地域の区分
        Returns:
            温度差係数
        """
        return factor_h.get_h(region=region, next_space=self._next_space)

    def get_nu(self, region: int, season: str):
        """
        方位係数を取得する。
        Args:
            region: 地域の区分
            season: 期間
        Returns:
            方位係数
        """

        if self._next_space == 'outdoor':
            return factor_nu.get_nu(region=region, season=season, direction=self._direction)
        else:
            return 0.0


class Door(DoorNoSpec, IArea, IGetQ, IGetM):
    """
    大部分がガラスで構成されないドア等の開口部
    """

    def __init__(
            self,
            name: str,
            next_space: str,
            direction: str,
            area: float,
            space_type: str,
            sunshade: factor_f.SunshadeOpaque,
            door_spec: DoorSpec
    ):
        """
        Args:
            name: 名称
            next_space: 隣接する空間の種類
            direction: 方位
            area: 面積, m2
            space_type: 接する室の用途
            sunshade: 日よけ
            door_spec: 仕様
        """

        super().__init__(
            name=name,
            next_space=next_space,
            direction=direction,
            area=area,
            sunshade=sunshade,
            space_type=space_type
        )
        self._door_spec = door_spec

    @classmethod
    def make_door(cls, d: Dict):
        """
        大部分がガラスで構成されないドア等の開口部に関する辞書からDoorクラスをインスタンス化する。
        Args:
            d: 大部分がガラスで構成されないドア等の開口部に関する辞書
        Returns:
            Door クラス
        """

        return Door(
            name=d['name'],
            next_space=d['next_space'],
            direction=d['direction'],
            area=d['area'],
            space_type=d['space_type'],
            sunshade=factor_f.SunshadeOpaque.make_sunshade_opaque(d=d['sunshade']),
            door_spec=DoorSpec.make_door_spec(d=d['spec'])
        )

    @classmethod
    def make_doors(cls, ds: List[Dict]):
        """
        大部分がガラスで構成されないドア等の開口部に関する辞書からDoorクラスのリストをインスタンス化する。
        Args:
            ds: 大部分がガラスで構成されないドア等の開口部に関する辞書のリスト
        Returns:
            Doors クラスのリスト
        """
        return [Door.make_door(d) for d in ds]

    def get_u(self):
        return self._door_spec.get_u()

    def get_q(self, region: int):
        return self.area * self.get_u() * self.get_h(region=region)

    def get_eta(self):
        return self._door_spec.get_eta()

    def get_m(self, region: int, season: str) -> float:
        return self.area * self.get_eta() * self.get_nu(region=region, season=season)

    def get_as_dict(self):

        return {
            'name': self.name,
            'next_space': self.next_space,
            'direction': self.direction,
            'area': self.area,
            'space_type': self.space_type,
            'sunshade': self.sunshade.get_as_dict(),
            'spec': self._door_spec.get_as_dict()
        }


class EarthfloorPerimeterSpec:

    def __init__(self, psi_value: float):

        self._psi_value = psi_value

    @classmethod
    def make_earthfloor_spec(cls, d: Dict):

        return EarthfloorPerimeterSpec(psi_value=d['psi_value'])

    def get_psi(self):
        return self._psi_value

    def get_as_dict(self):

        return {
            'psi_value': self._psi_value
        }


class EarthfloorPerimeterNoSpec:

    def __init__(self, name: str, next_space: str, length: float, space_type: str):
        """
        Args:
            name: 名称
            next_space: 隣接する空間の種類
            length: 長さ, m
            space_type: 接する室の名称
            earthfloor_perimeter_spec: 仕様
        """
        self._name = name
        self._next_space = next_space
        self._length = length
        self._space_type = space_type

    @property
    def name(self):
        return self._name

    @property
    def next_space(self):
        return self._next_space

    @property
    def length(self):
        return self._length

    @property
    def space_type(self):
        return self._space_type

    def get_h(self, region: int):
        return factor_h.get_h(region=region, next_space=self._next_space)


class EarthfloorPerimeter(EarthfloorPerimeterNoSpec, IGetQ):

    def __init__(
            self,
            name: str,
            next_space: str,
            length: float,
            space_type: str,
            earthfloor_perimeter_spec: EarthfloorPerimeterSpec):
        """
        Args:
            name: 名称
            next_space: 隣接する空間の種類
            length: 長さ, m
            space_type: 接する室の名称
            earthfloor_perimeter_spec: 仕様
        """

        super().__init__(name=name, next_space=next_space, length=length, space_type=space_type)
        self._earthfloor_perimeter_spec = earthfloor_perimeter_spec

    @classmethod
    def make_earthfloor_perimeter(cls, d: Dict):
        return EarthfloorPerimeter(
            name=d['name'],
            next_space=d['next_space'],
            length=d['length'],
            space_type=d['space_type'],
            earthfloor_perimeter_spec=EarthfloorPerimeterSpec.make_earthfloor_spec(d['spec'])
        )

    @classmethod
    def make_earthfloor_perimeters(cls, ds: List[Dict]):
        return [EarthfloorPerimeter.make_earthfloor_perimeter(d) for d in ds]

    def get_psi(self):
        return self._earthfloor_perimeter_spec.get_psi()

    def get_q(self, region: int):
        return self.length * self.get_psi() * self.get_h(region=region)

    def get_as_dict(self):

        return {
            'name': self._name,
            'next_space': self._next_space,
            'length': self._length,
            'space_type': self._space_type,
            'spec': self._earthfloor_perimeter_spec.get_as_dict()
        }


class EarthfloorCenterSpec:

    def __init__(self, layers: List[dict]):

        self._layers = layers

    @classmethod
    def make_earthfloor_center_spec(cls, d: dict):

        return EarthfloorCenterSpec(layers=d['layers'])

    @property
    def layers(self):
        return self._layers

    def get_as_dict(self):

        return {
            'layers': self._layers
        }


class EarthfloorCenterNoSpec(IArea):

    def __init__(self, name: str, area: float, space_type: str):
        self._name = name
        self._area = area
        self._space_type = space_type

    @property
    def name(self) -> str:
        """
        名前を取得する。
        Returns:
            名前
        """
        return self._name

    @property
    def area(self):
        """
        面積を取得する。
        Returns:
            面積, m2
        """

        return self._area

    @property
    def space_type(self) -> str:
        """
        接する室の用途を取得する。
        Returns:
            接する室の用途
        """

        return self._space_type


class EarthfloorCenter(EarthfloorCenterNoSpec, IArea):

    def __init__(self, name: str, area: float, space_type: str, spec: EarthfloorCenterSpec):
        """

        Args:
            name: 名称
            area: 面積, m2
            space_type: 接する室の用途
            spec:
        """

        super().__init__(name=name, area=area, space_type=space_type)
        self._earthfloor_center_spec = spec

    @classmethod
    def make_earthfloor_center(cls, d: Dict):
        return EarthfloorCenter(
            name=d['name'],
            area=d['area'],
            space_type=d['space_type'],
            spec=EarthfloorCenterSpec.make_earthfloor_center_spec(d=d['spec'])
        )

    @classmethod
    def make_earthfloor_centers(cls, ds: List[Dict]):
        return [EarthfloorCenter.make_earthfloor_center(d) for d in ds]

    def get_as_dict(self):

        return {
            'name': self.name,
            'area': self.area,
            'space_type': self.space_type,
            'spec': self._earthfloor_center_spec.get_as_dict()
        }
