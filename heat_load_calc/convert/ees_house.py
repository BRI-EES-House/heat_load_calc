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


class Structure:

    def __init__(self, d: Dict):
        self._d = d
        self._d_spec = d['spec']

    @property
    def d(self):
        return self._d

    @property
    def d_spec(self):
        return self._d_spec


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


class GeneralPart(Structure, IArea, IGetQ, IGetM):

    def __init__(self, d: Dict, area: float, next_space: str, direction: str, general_part_spec: GeneralPartSpec):
        """

        Args:
            d:
            area: 面積, m2
            next_space: 隣接する空間の種類
            direction: 方位
            general_part_spec: 仕様
        """

        super().__init__(d=d)
        self._area = area
        self._next_space = next_space
        self._direction = direction
        self._general_part_spec = general_part_spec

    @classmethod
    def make_general_part(cls, d: Dict):
        return GeneralPart(
            d=d,
            area=d['area'],
            next_space=d['next_space'],
            direction=d['direction'],
            general_part_spec=GeneralPartSpec.make_general_part_spec(d=d['spec'])
        )

    @classmethod
    def make_general_parts(cls, ds: List[Dict]):
        return [GeneralPart.make_general_part(d) for d in ds]

    @property
    def area(self) -> float:
        return self._area

    def get_h(self, region) -> float:
        return factor_h.get_h(region=region, next_space=self._next_space)

    def get_u(self) -> float:
        return self._general_part_spec.get_u()

    def get_q(self, region: int) -> float:
        return self.area * self.get_u() * self.get_h(region=region)

    def get_eta(self) -> float:
        return self._general_part_spec.get_eta()

    def get_nu(self, region: int, season: str):
        if self._next_space == 'outdoor':
            return factor_nu.get_nu(region=region, season=season, direction=self._direction)
        else:
            return 0.0

    def get_m(self, region: int, season: str) -> float:
        return self._area * self.get_eta() * self.get_nu(region=region, season=season)


class WindowSpec:

    def __init__(
            self,
            window_type: str,
            windows: List[Dict],
            attachment_type,
            is_windbreak_room_attached,
            is_sunshade_input,
            sunshade
    ):

        self._window_type = window_type
        self._windows = windows
        self._attachment_type = attachment_type
        self._is_windbreak_room_attached = is_windbreak_room_attached
        self._is_sunshade_input = is_sunshade_input
        self._sunshade = sunshade

    @classmethod
    def make_window_spec(cls, d: Dict):

        return WindowSpec(
            window_type=d['window_type'],
            windows=d['windows'],
            attachment_type=d['attachment_type'],
            is_windbreak_room_attached=d['is_windbreak_room_attached'],
            is_sunshade_input=d['is_sunshade_input'],
            sunshade=factor_f.Sunshade.make_sunshade(
                is_sunshade_input=d['is_sunshade_input'],
                d=d['sunshade']
            )
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

    def get_f(self, region: int, season: str, direction: str) -> float:
        """
        日射熱取得補正係数を計算する。
        Args:
            region: 地域の区分
            season: 期間
            direction: 方位
        Returns:
            日射熱取得補正係数
        """

        return factor_f.get_f(season=season, region=region, direction=direction, sunshade=self._sunshade)


class Window(Structure, IArea, IGetQ, IGetM):

    def __init__(self, d: Dict, area: float, next_space: str, direction: str, window_spec: WindowSpec):
        """

        Args:
            d:
            area: 面積, m2
            next_space: 隣接する空間の種類
            direction: 方位
            window_spec: 仕様
        """

        super().__init__(d=d)
        self._area = area
        self._next_space = next_space
        self._direction = direction
        self._window_spec = window_spec

    @classmethod
    def make_window(cls, d: Dict):
        return Window(
            d=d,
            area=d['area'],
            next_space=d['next_space'],
            direction=d['direction'],
            window_spec=WindowSpec.make_window_spec(d=d['spec'])
        )

    @classmethod
    def make_windows(cls, ds: List[Dict]):
        return [Window.make_window(d) for d in ds]

    @property
    def area(self):
        return self._area

    def get_h(self, region: int):
        return factor_h.get_h(region=region, next_space=self._next_space)

    def get_u(self):
        return self._window_spec.get_u()

    def get_q(self, region: int):
        return self.area * self.get_u() * self.get_h(region=region)

    def get_eta_d(self, season: str):
        return self._window_spec.get_eta_d(season=season)

    def get_nu(self, region: int, season: str):

        if self._next_space == 'outdoor':
            return factor_nu.get_nu(season=season, region=region, direction=self._direction)
        else:
            return 0.0

    def get_f(self, region: int, season: str) -> float:
        """
        日射熱取得補正係数を計算する。
        Args:
            region: 地域の区分
            season: 期間
        Returns:
            日射熱取得補正係数
        """

        return self._window_spec.get_f(region=region, season=season, direction=self._direction)

    def get_m(self, region: int, season: str) -> float:
        return self.get_eta_d(season=season) \
               * self.area \
               * self.get_f(region=region, season=season) \
               * self.get_nu(region=region, season=season)


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


class Door(Structure, IArea, IGetQ, IGetM):

    def __init__(self, d: Dict, area: float, next_space: str, direction: str, door_spec: DoorSpec):
        """

        Args:
            d:
            area: 面積, m2
            next_space: 隣接する空間の種類
            door_spec: 仕様
        """

        super().__init__(d=d)
        self._area = area
        self._next_space = next_space
        self._direction = direction
        self._door_spec = door_spec

    @classmethod
    def make_door(cls, d: Dict):
        return Door(
            d=d,
            area=d['area'],
            next_space=d['next_space'],
            direction=d['direction'],
            door_spec=DoorSpec.make_door_spec(d=d['spec'])
        )

    @classmethod
    def make_doors(cls, ds: List[Dict]):
        return [Door.make_door(d) for d in ds]

    @property
    def area(self):
        return self._area

    def get_h(self, region: int):
        return factor_h.get_h(region=region, next_space=self._next_space)

    def get_u(self):
        return self._door_spec.get_u()

    def get_q(self, region: int):
        return self.area * self.get_u() * self.get_h(region=region)

    def get_eta(self):
        return self._door_spec.get_eta()

    def get_nu(self, region: int, season: str):
        if self._next_space == 'outdoor':
            return factor_nu.get_nu(region=region, season=season, direction=self._direction)
        else:
            return 0.0

    def get_m(self, region: int, season: str) -> float:
        return self.area * self.get_eta() * self.get_nu(region=region, season=season)


class EarthfloorPerimeterSpec:

    def __init__(self, psi_value: float):

        self._psi_value = psi_value

    @classmethod
    def make_earthfloor_spec(cls, d: Dict):

        return EarthfloorPerimeterSpec(psi_value=d['psi_value'])

    def get_psi(self):
        return self._psi_value


class EarthfloorPerimeter(Structure, IGetQ):

    def __init__(self, d: Dict, length: float, next_space: str, earthfloor_perimeter_spec: EarthfloorPerimeterSpec):
        """

        Args:
            d:
            length: 長さ, m
            next_space: 隣接する空間の種類
            earthfloor_perimeter_spec: 仕様
        """

        super().__init__(d=d)
        self._length = length
        self._next_space = next_space
        self._earthfloor_perimeter_spec = earthfloor_perimeter_spec

    @classmethod
    def make_earthfloor_perimeter(cls, d: Dict):
        return EarthfloorPerimeter(
            d=d,
            length=d['length'],
            next_space=d['next_space'],
            earthfloor_perimeter_spec=EarthfloorPerimeterSpec.make_earthfloor_spec(d['spec'])
        )

    @classmethod
    def make_earthfloor_perimeters(cls, ds: List[Dict]):
        return [EarthfloorPerimeter.make_earthfloor_perimeter(d) for d in ds]

    @property
    def length(self):
        return self._length

    def get_h(self, region: int):
        return factor_h.get_h(region=region, next_space=self._next_space)

    def get_psi(self):
        return self._earthfloor_perimeter_spec.get_psi()

    def get_q(self, region: int):
        return self.length * self.get_psi() * self.get_h(region=region)


class EarthfloorCenter(Structure, IArea):

    def __init__(self, d: Dict, area: float):
        """

        Args:
            d:
            area: 面積, m2
        """

        super().__init__(d=d)
        self._area = area

    @classmethod
    def make_earthfloor_center(cls, d: Dict):
        return EarthfloorCenter(d=d, area=d['area'])

    @classmethod
    def make_earthfloor_centers(cls, ds: List[Dict]):
        return [EarthfloorCenter.make_earthfloor_center(d) for d in ds]

    @property
    def area(self):
        return self._area
