"""
省エネ基準に基づく住宅情報を保持するクラス
"""

from typing import Dict, List, Union
import abc
from enum import Enum
from copy import deepcopy

from heat_load_calc.external import factor_h
from heat_load_calc.external import factor_nu
from heat_load_calc.convert import factor_f


class HeatResistanceInputMethod(Enum):
    CONDUCTIVITY = 'conductivity'
    RESISTANCE = 'resistance'


class GeneralPartType(Enum):
    # 屋根
    ROOF = 'roof'
    # 天井
    CEILING = 'ceiling'
    # 壁
    WALL = 'wall'
    # 床
    FLOOR = 'floor'
    # 戸境壁
    BOUNDARY_WALL = 'boundary_wall'
    # 戸境床（上階側）
    UPWARD_BOUNDARY_FLOOR = 'upward_boundary_floor'
    # 戸境床（下界側）
    DOWNWARD_BOUNDARY_FLOOR = 'downward_boundary_floor'


class GlassType(Enum):
    """
    ガラスの層の数
    """

    # 単層
    SINGLE = 'single'
    # 2層複層
    DOUBLE = 'double'
    # 3層以上複層
    TRIPLE_AND_MORE = 'triple_and_more'
    # 不明
    UNKNOWN = 'unknown'


class FlameType(Enum):
    """
    建具の種類
    """

    # 木製建具
    WOOD = 'wood'
    # 樹脂製建具
    RESIN = 'resin'
    # 金属製建具
    METAL = 'metal'
    # 木と金属の複合材料製建具
    WOOD_AND_METAL = 'wood_and_metal'
    # 樹脂と金属の複合材料製建具
    RESIN_AND_METAL = 'resin_and_metal'
    # 不明
    UNKNOWN = 'unknown'


class EesHouse:

    def __init__(self):
        pass

    @classmethod
    def make_ees_house(cls, d: Dict):
        pass


class Material:
    """
    物性値を持つクラス。
    熱伝導率や熱容量をもつ。厚さのプロパティは持たない。
    """

    def __init__(
            self,
            material_name: str,
            volumetric_specific_heat: float,
            thermal_conductivity: float = 0.0
    ):
        """
        Args:
            material_name: 物性値の名称
            volumetric_specific_heat: 容積比熱, J/LK
            thermal_conductivity: 熱伝導率, W/mK
        """

        self._material_name = material_name
        self._volumetric_specific_heat = volumetric_specific_heat
        self._thermal_conductivity = thermal_conductivity

    @property
    def material_name(self):
        """
        物性値の名称を取得する。
        Returns:
            物性値の名称
        """
        return self._material_name

    @property
    def volumetric_specific_heat(self):
        """
        容積比熱を取得する。
        Returns:
            容積比熱, J/LK
        """
        return self._volumetric_specific_heat

    @property
    def thermal_conductivity(self):
        """
        熱伝導率を取得する。
        Returns:
            thermal_conductivity: 熱伝導率, W/mK
        """
        return self._thermal_conductivity


class Layer:
    """
    外皮・間仕切りを構成する場合の層を持つクラス。
    Materialクラスの物性値に加えて、厚さのプロパティを持つ。
    """

    def __init__(
            self,
            name: str,
            heat_resistance_input_method: HeatResistanceInputMethod,
            thickness: float,
            volumetric_specific_heat: float,
            thermal_conductivity: float = 0.0,
            thermal_resistance: float = 0.0
    ):
        """
        Args:
            name: レイヤーの名称
            heat_resistance_input_method: 熱抵抗の入力方法
            thickness: 厚さ, m
            volumetric_specific_heat: 容積比熱, J/LK
            thermal_conductivity: 熱伝導率, W/mK
            thermal_resistance: 熱抵抗, m2K/W
        """

        self._name = name
        self._heat_resistance_input_method = heat_resistance_input_method
        self._thickness = thickness
        self._volumetric_specific_heat = volumetric_specific_heat
        self._thermal_conductivity = thermal_conductivity
        self._thermal_resistance = thermal_resistance

    @property
    def name(self) -> str:
        """
        名称を取得する。
        Returns:
            名称
        """
        return self._name

    @property
    def heat_resistance_input_method(self) -> HeatResistanceInputMethod:
        """
        熱抵抗の入力方法を取得する。
        Returns:
            熱抵抗の入力方法
        """
        return self._heat_resistance_input_method

    @property
    def thickness(self) -> float:
        """
        厚さを取得する。
        Returns:
            厚さ, m
        """
        return self._thickness

    @property
    def volumetric_specific_heat(self) -> float:
        """
        容積比熱を取得する。
        Returns:
            容積比熱, J/LK
        """
        return self._volumetric_specific_heat

    @property
    def thermal_conductivity(self) -> float:
        """
        熱伝導率を取得する。
        Returns:
            熱伝導率, W/mK
        """
        return self._thermal_conductivity

    @property
    def thermal_resistance(self) -> float:
        """
        熱抵抗を取得する。
        Returns:
            熱抵抗, m2K/W
        """
        return self._thermal_resistance

    @property
    def r(self) -> float:
        """
        熱抵抗を取得する。
        Returns:
            熱抵抗, m2K/W
        """

        if self._heat_resistance_input_method == HeatResistanceInputMethod.CONDUCTIVITY:
            return self._thickness / self._thermal_conductivity
        elif self._heat_resistance_input_method == HeatResistanceInputMethod.RESISTANCE:
            return self._thermal_resistance
        else:
            raise KeyError()

    @property
    def c(self) -> float:
        """
        比熱を取得する
        Returns:
            比熱, kJ/m2K
        """
        return self._thickness * self._volumetric_specific_heat

    @classmethod
    def make_layer(cls, d: Dict):
        """
        辞書からクラス Layer を生成する。
        Args:
            d: Layer を表す辞書。
        Returns:
            Layer クラス
        """

        hri = HeatResistanceInputMethod(d['heat_resistance_input_method'])
        if hri == HeatResistanceInputMethod.CONDUCTIVITY:
            return Layer(
                name=d['name'],
                heat_resistance_input_method=hri,
                thickness=d['thickness'],
                volumetric_specific_heat=d['volumetric_specific_heat'],
                thermal_conductivity=d['thermal_conductivity']
            )
        elif hri == HeatResistanceInputMethod.RESISTANCE:
            return Layer(
                name=d['name'],
                heat_resistance_input_method=hri,
                thickness=d['thickness'],
                volumetric_specific_heat=d['volumetric_specific_heat'],
                thermal_resistance=d['thermal_resistance']
            )
        else:
            raise KeyError()

    @classmethod
    def make_layers(cls, ds: List[Dict]):
        """
        Layer クラスのリストを作成する。
        Args:
            ds: Layer クラスを表す辞書のリスト
        Returns:
            Layer クラスのリスト
        """
        return [Layer.make_layer(d) for d in ds]

    def get_as_dict(self) -> Dict:
        """
        プロパティを辞書化する。
        Returns:
            辞書
        """

        if self._heat_resistance_input_method == HeatResistanceInputMethod.CONDUCTIVITY:
            return {
                'name': self._name,
                'heat_resistance_input_method': self._heat_resistance_input_method.value,
                'thickness': self._thickness,
                'volumetric_specific_heat': self._volumetric_specific_heat,
                'thermal_conductivity': self._thermal_conductivity
            }
        elif self._heat_resistance_input_method == HeatResistanceInputMethod.RESISTANCE:
            return {
                'name': self._name,
                'heat_resistance_input_method': self._heat_resistance_input_method.value,
                'thickness': self._thickness,
                'volumetric_specific_heat': self._volumetric_specific_heat,
                'thermal_resistance': self._thermal_resistance
            }
        else:
            raise Exception()

    def make_initializer_dict(self, r_res_sub: float) -> Dict:
        """
        initializer用の辞書を作成する。
        Args:
            r_res_sub: 熱抵抗割引率(0.0~1.0)
        Returns:
            initializer用辞書
        Notes:
            熱抵抗割引率とは、S造における面的な熱橋、および、S造・RC造における構造熱橋ψによる熱貫流率の減少分を反映させるための係数。
            本layer構成が持っているR値（もともとのR値）と増加分のR値を用いて、
            割増率 = ( もともとのR値 - 割引されるR値 ) / もともとのR値
            で表される。
        """
        return {
            'name': self._name,
            'thermal_resistance': self.r * r_res_sub,
            'thermal_capacity': self.c
        }


class GeneralPartPart:

    def __init__(self, name: str, part_area_ratio: float, layers: List[Layer]):
        """
        Args:
            name: 名称
            part_area_ratio: 部分の面積比率（0.0～1.0）
            layers: 層（リスト）
        """

        self._name = name
        self._part_area_ratio = part_area_ratio
        self._layers = layers

    @classmethod
    def make_general_part_part(cls, d: Dict):
        """
        GeneralPartPart クラスを表す辞書から GeneralPartPart クラスを作成する。
        Args:
            d: GeneralPartPart クラスを表す辞書
        Returns:
            GeneralPartPart クラス
        """

        return GeneralPartPart(
            name=d['name'],
            part_area_ratio=d['part_area_ratio'],
            layers=Layer.make_layers(ds=d['layers'])
        )

    @classmethod
    def make_general_part_parts(cls, ds: List[Dict]):
        """
        GeneralPartPart クラスを表す辞書のリストから GeneralPartPart クラスのリストを作成する。
        Args:
            ds: GeneralPartPart クラスを表す辞書のリスト
        Returns:
            GeneralPartPart クラスのリスト
        """

        # part_area_ratio の合計値が1.0になるかどうかの確認
        total_ratio = sum([d['part_area_ratio'] for d in ds])
        if abs(total_ratio - 1.0) > 0.000001:
            raise Exception('part_area_ratio の値は合計で1.0になるように設定してください。')

        return [GeneralPartPart.make_general_part_part(d=d) for d in ds]

    @property
    def name(self) -> str:
        """
        部分の名称を取得する。
        Returns:
            部分の名称
        """
        return self._name

    @property
    def part_area_ratio(self) -> float:
        """
        部分の面積比率を取得する。
        Returns:
            部分の面積比率
        Notes:
            部分の面積比率は0.0から1.0の間の値をとる。
        """
        return self._part_area_ratio

    @property
    def layers(self) -> List[Layer]:
        """
        レイヤーのリストを取得する。
        Returns:
            レイヤーのリスト
        """
        return self._layers

    def get_r_total(self) -> float:
        """
        熱抵抗の合計値を取得する。
        Returns:
            熱抵抗, m2K/W
        """

        return sum([layer.r for layer in self._layers])

    def get_as_dict(self) -> Dict:

        return {
            'name': self.name,
            'part_area_ratio': self.part_area_ratio,
            'layers': [layer.get_as_dict() for layer in self.layers]
        }

    def make_initializer_dict(
            self,
            general_part_name: str,
            general_part_area: float,
            r_res_sub: float
    ) -> Dict:
        """
        initializer用の辞書を作成する。
        Args:
            general_part_name: 一般部位の名称
            general_part_area: 一般部位の面積, m2
            r_res_sub: 熱抵抗割引率(0.0~1.0)
        Returns:
            initializer用辞書
        Notes:
            熱抵抗割引率とは、S造における面的な熱橋、および、S造・RC造における構造熱橋ψによる熱貫流率の減少分を反映させるための係数。
            本layer構成が持っているR値（もともとのR値）と増加分のR値を用いて、
            割増率 = ( もともとのR値 - 割引されるR値 ) / もともとのR値
            で表される。
        """
        return {
            'name': general_part_name + '_' + self.name,
            'area': general_part_area * self.part_area_ratio,
            'layers': [layer.make_initializer_dict(r_res_sub=r_res_sub) for layer in self.layers]
        }


class GeneralPartSpec:

    def __init__(self):

        pass

    @classmethod
    def make_general_part_spec(cls, d: Dict, general_part_type: GeneralPartType):
        """
        GeneralPartSpec クラスを表す辞書から GeneralPartSpec クラスを作成する。
        Args:
            d: GeneralPartSpec クラスを表す辞書
            general_part_type: 一般部位の種類
        Returns:
            GeneralPartSpec クラスを継承した以下のクラス
                - GeneralPartSpecDetailWood
                - GeneralPartSpecDetailRC
                - GeneralPartSpecDetailSteel
                - GeneralPartSpecUValueOther
        """

        structure = d['structure']

        if structure == 'wood':
            return GeneralPartSpecDetailWood.make_from_dict(d=d)
        elif structure == 'rc':
            return GeneralPartSpecDetailRC.make_from_dict(d=d)
        elif structure == 'steel':
            return GeneralPartSpecDetailSteel.make_from_dict(d=d)
        elif structure == 'other':
            return GeneralPartSpecUValueOther.make_from_dict(general_part_type=general_part_type, d=d)
        else:
            raise NotImplementedError()

    @property
    @abc.abstractmethod
    def r_srf_in(self) -> float:
        """
        室内側熱伝達抵抗を取得する。
        Returns:
            室内側熱伝達抵抗, m2K/W
        """

        pass

    @property
    @abc.abstractmethod
    def r_srf_ex(self) -> float:
        """
        室外側熱伝達抵抗を取得する。
        Returns:
            室外側熱伝達抵抗, m2K/W
        """

        pass

    @abc.abstractmethod
    def get_u(self) -> float:
        """
        U値を取得する。
        Returns:
            U値, W/m2K
        """

        pass

    def get_eta(self) -> float:
        """
        η値を取得する。
        Returns:
            η値, -
        """

        return 0.034 * self.get_u()

    @abc.abstractmethod
    def get_as_dict(self):

        pass

    @abc.abstractmethod
    def make_initializer_dict(self, name: str, area: float, u_add: float) -> List[Dict]:
        pass


class GeneralPartSpecDetail(GeneralPartSpec):

    def __init__(
            self,
            r_srf_in: float,
            r_srf_ex: float,
            parts: List[GeneralPartPart]
    ):
        """

        Args:
            r_srf_in: 室内側熱伝達抵抗, m2K/W
            r_srf_ex: 室外側熱伝達抵抗, m2K/W
            parts: 部分（リスト）
        """

        super().__init__()
        self._r_srf_in = r_srf_in
        self._r_srf_ex = r_srf_ex
        self._parts = parts

    @property
    def r_srf_in(self) -> float:
        """
        室内側熱伝達抵抗を取得する。
        Returns:
            室内側熱伝達抵抗, m2K/W
        """
        return self._r_srf_in

    @property
    def r_srf_ex(self) -> float:
        """
        室外側熱伝達抵抗を取得する。
        Returns:
            室外側熱伝達抵抗, m2K/W
        """
        return self._r_srf_ex

    @property
    def parts(self) -> List[GeneralPartPart]:
        return self._parts

    def get_u_general_part(self) -> float:
        """
        U値を取得する。
        Returns:
            U値, W/m2K
        Notes:
            面的なU値を取得する。
            木造・RC造についてはこの値がU値である。
            S造についてはこの値に補正熱貫流率を加える。
        """

        return sum([p.part_area_ratio / (self.r_srf_in + p.get_r_total() + self.r_srf_ex) for p in self._parts])

    @abc.abstractmethod
    def get_as_dict(self):
        pass

    def make_initializer_dict(self, name: str, area: float, u_add: float) -> List[Dict]:
        """
        U値増加分を考慮した補正後のinitializer用のレイヤーのリストを辞書形式で取得する。
        Args:
            name: 名称
            area: 面積, m2
            u_add: U値増加分, W/m2K
        Returns:
            initializer用レイヤーのリスト
        """

        # part ごとのU値, W/m2K
        us = [1 / (self.r_srf_in + p.get_r_total() + self.r_srf_ex) for p in self._parts]

        # 補正したU値, W/m2K
        us_dash = [u + u_add for u in us]

        # 補正したR値（室外側熱伝達抵抗・室内側熱伝達抵抗を除く）, m2K/W
        rs_dash = [1 / u_dash - self.r_srf_in - self.r_srf_ex for u_dash in us_dash]

        # 熱抵抗割引率
        rs_res_sub = [r_dash / p.get_r_total() for p, r_dash in zip(self._parts, rs_dash)]

        ds = [
            part.make_initializer_dict(
                general_part_name=name,
                general_part_area=area,
                r_res_sub=r_res_sub
            ) for part, r_res_sub in zip(self.parts, rs_res_sub)
        ]

        for d in ds:
            d.update(
                inside_heat_transfer_resistance=self.r_srf_in,
                outside_heat_transfer_resistance=self.r_srf_ex
            )

        return ds


class GeneralPartSpecDetailWood(GeneralPartSpecDetail):

    def __init__(self, r_srf_in: float, r_srf_ex: float, parts: List[GeneralPartPart]):

        super().__init__(r_srf_in=r_srf_in, r_srf_ex=r_srf_ex, parts=parts)

    @classmethod
    def make_from_dict(cls, d: Dict):

        return GeneralPartSpecDetailWood(
            r_srf_in=d['r_srf_in'],
            r_srf_ex=d['r_srf_ex'],
            parts=GeneralPartPart.make_general_part_parts(ds=d['parts'])
        )

    def get_u(self) -> float:
        """
        U値を取得する。
        Returns:
            U値, W/m2K
        """

        return self.get_u_general_part()

    def get_as_dict(self):

        return {
            'structure': 'wood',
            'r_srf_in': self.r_srf_in,
            'r_srf_ex': self.r_srf_ex,
            'parts': [part.get_as_dict() for part in self.parts]
        }

    def make_initializer_dict(self, name: str, area: float, u_add: float) -> List[Dict]:
        """
        U値増加分を考慮した補正後のinitializer用のレイヤーのリストを辞書形式で取得する。
        Args:
            name: 名称
            area: 面積, m2
            u_add: U値増加分, W/m2K
        Returns:
            initializer用レイヤーのリスト
        """

        return super().make_initializer_dict(name=name, area=area, u_add=u_add)


class GeneralPartSpecDetailRC(GeneralPartSpecDetail):

    def __init__(self, r_srf_in: float, r_srf_ex: float, parts: List[GeneralPartPart]):

        super().__init__(r_srf_in=r_srf_in, r_srf_ex=r_srf_ex, parts=parts)

    @classmethod
    def make_from_dict(cls, d: Dict):

        return GeneralPartSpecDetailRC(
            r_srf_in=d['r_srf_in'],
            r_srf_ex=d['r_srf_ex'],
            parts=GeneralPartPart.make_general_part_parts(ds=d['parts'])
        )

    def get_u(self) -> float:
        """
        U値を取得する。
        Returns:
            U値, W/m2K
        """

        return self.get_u_general_part()

    def get_as_dict(self):
        return {
            'structure': 'rc',
            'r_srf_in': self.r_srf_in,
            'r_srf_ex': self.r_srf_ex,
            'parts': [part.get_as_dict() for part in self.parts]
        }

    def make_initializer_dict(self, name: str, area: float, u_add: float) -> List[Dict]:
        """
        U値増加分を考慮した補正後のinitializer用のレイヤーのリストを辞書形式で取得する。
        Args:
            name: 名称
            area: 面積, m2
            u_add: U値増加分, W/m2K
        Returns:
            initializer用レイヤーのリスト
        """

        return super().make_initializer_dict(name=name, area=area, u_add=u_add)


class GeneralPartSpecDetailSteel(GeneralPartSpecDetail):

    def __init__(self, u_r_value_steel: float, r_srf_in: float, r_srf_ex: float, parts: List[GeneralPartPart]):
        """
        Args:
            u_r_value_steel: 補正熱貫流率, W/m2K
            r_srf_in: 室内側熱伝達抵抗, m2K/W
            r_srf_ex: 室外側熱伝達抵抗, m2K/W
            parts:　部分（リスト）
        """

        super().__init__(r_srf_in=r_srf_in, r_srf_ex=r_srf_ex, parts=parts)
        self._u_r_value_steel = u_r_value_steel

    @classmethod
    def make_from_dict(cls, d: Dict):

        return GeneralPartSpecDetailSteel(
            u_r_value_steel=d['u_r_value_steel'],
            r_srf_in=d['r_srf_in'],
            r_srf_ex=d['r_srf_ex'],
            parts=GeneralPartPart.make_general_part_parts(ds=d['parts'])
        )

    def get_u(self) -> float:
        """
        U値を取得する。
        Returns:
            U値, W/m2K
        """

        return self.get_u_general_part() + self._u_r_value_steel

    def get_as_dict(self):
        return {
            'structure': 'steel',
            'u_r_value_steel': self._u_r_value_steel,
            'r_srf_in': self.r_srf_in,
            'r_srf_ex': self.r_srf_ex,
            'parts': [part.get_as_dict() for part in self.parts]
        }

    def make_initializer_dict(self, name: str, area: float, u_add: float) -> List[Dict]:
        """
        U値増加分を考慮した補正後のinitializer用のレイヤーのリストを辞書形式で取得する。
        Args:
            name: 名称
            area: 面積, m2
            u_add: U値増加分, W/m2K
        Returns:
            initializer用レイヤーのリスト
        """

        return super().make_initializer_dict(name=name, area=area, u_add=u_add + self._u_r_value_steel)


class GeneralPartSpecUValue(GeneralPartSpec):

    def __init__(self, general_part_type: GeneralPartType, u_value: float, weight: str):

        super().__init__()
        self._u_value = u_value
        self._weight = weight

        # 室外側熱伝達抵抗を計算する際に使用するために GeneralPartSpec クラスでこのプロパティを保持しておく。
        # get_as_dict には書き出さない。
        self._general_part_type = general_part_type

    @property
    def general_part_type(self) -> GeneralPartType:
        return self._general_part_type

    def get_u(self) -> float:
        """
        U値を取得する。
        Returns:
            U値, W/m2K
        """

        return self._u_value

    @property
    def r_srf_in(self) -> float:
        """
        室内側熱伝達抵抗を取得する。
        Returns:
            室内側熱伝達抵抗, m2K/W
        """

        return {
            GeneralPartType.ROOF: 0.09,
            GeneralPartType.CEILING: 0.09,
            GeneralPartType.WALL: 0.11,
            GeneralPartType.FLOOR: 0.15,
            GeneralPartType.BOUNDARY_WALL: 0.11,
            GeneralPartType.UPWARD_BOUNDARY_FLOOR: 0.09,
            GeneralPartType.DOWNWARD_BOUNDARY_FLOOR: 0.15
        }[self.general_part_type]

    @property
    def r_srf_ex(self) -> float:
        """
        室外側熱伝達抵抗を取得する。
        Returns:
            室外側熱伝達抵抗, m2K/W
        """

        return {
            GeneralPartType.ROOF: 0.04,
            GeneralPartType.CEILING: 0.09,
            GeneralPartType.WALL: 0.04,
            GeneralPartType.FLOOR: 0.15,
            GeneralPartType.BOUNDARY_WALL: 0.11,
            GeneralPartType.UPWARD_BOUNDARY_FLOOR: 0.09,
            GeneralPartType.DOWNWARD_BOUNDARY_FLOOR: 0.15
        }[self.general_part_type]

    @abc.abstractmethod
    def get_as_dict(self) -> Dict:

        pass

    def make_initializer_dict(self, name: str, area: float, u_add: float) -> List[Dict]:

        # GeneralPartSpecDetail
        gpsd = self._convert_to_general_part_spec_detail()

        return gpsd.make_initializer_dict(name=name, area=area, u_add=u_add)

    def _convert_to_general_part_spec_detail(self) -> GeneralPartSpecDetail:

        gypsum_board9_5 = Layer(
            name='gypsum_board',
            heat_resistance_input_method=HeatResistanceInputMethod.CONDUCTIVITY,
            thickness=0.0095,
            volumetric_specific_heat=830.0,
            thermal_conductivity=0.221
        )

        plywood12 = Layer(
            name='plywood',
            heat_resistance_input_method=HeatResistanceInputMethod.CONDUCTIVITY,
            thickness=0.012,
            volumetric_specific_heat=720.0,
            thermal_conductivity=0.16
        )

        plywood24 = Layer(
            name='plywood',
            heat_resistance_input_method=HeatResistanceInputMethod.CONDUCTIVITY,
            thickness=0.024,
            volumetric_specific_heat=720.0,
            thermal_conductivity=0.16
        )

        concrete120 = Layer(
            name='concrete',
            heat_resistance_input_method=HeatResistanceInputMethod.CONDUCTIVITY,
            thickness=0.120,
            volumetric_specific_heat=2000.0,
            thermal_conductivity=1.6
        )

        insulation = Material(
            material_name='default_insulation',
            volumetric_specific_heat=13.0,
            thermal_conductivity=0.045
        )

        default_layers = {
            'light': {
                # 屋根の場合：せっこうボード9.5mm + 断熱材
                GeneralPartType.ROOF: [gypsum_board9_5, insulation],
                # 天井の場合：せっこうボード9.5mm + 断熱材
                GeneralPartType.CEILING: [gypsum_board9_5, insulation],
                # 壁の場合：せっこうボード9.5mm + 断熱材 + 合板12mm
                GeneralPartType.WALL: [gypsum_board9_5, insulation, plywood12],
                # 床の場合：合板24mm + 断熱材
                GeneralPartType.FLOOR: [plywood24, insulation],
                # 間仕切り壁の場合：せっこうボード9.5mm + 断熱材 + せっこうボード9.5mm
                GeneralPartType.BOUNDARY_WALL: [gypsum_board9_5, insulation, gypsum_board9_5],
                # 間仕切り天井の場合：せっこうボード9.5mm + 断熱材 + 合板24mm
                GeneralPartType.UPWARD_BOUNDARY_FLOOR: [gypsum_board9_5, insulation, plywood24],
                # 間仕切り床の場合： 合板24mm + 断熱材 + せっこうボード9.5mm
                GeneralPartType.DOWNWARD_BOUNDARY_FLOOR: [plywood24, insulation, gypsum_board9_5]
            }[self.general_part_type],
            'heavy': {
                # 屋根の場合：せっこうボード9.5mm + 断熱材 + コンクリート120mm
                GeneralPartType.ROOF: [gypsum_board9_5, insulation, concrete120],
                # 天井の場合：せっこうボード9.5mm + 断熱材 + コンクリート120mm
                GeneralPartType.CEILING: [gypsum_board9_5, insulation, concrete120],
                # 壁の場合：せっこうボード9.5mm + 断熱材 + コンクリート120mm
                GeneralPartType.WALL: [gypsum_board9_5, insulation, concrete120],
                # 床の場合：合板24mm + 断熱材 + コンクリート120mm
                GeneralPartType.FLOOR: [plywood24, insulation, concrete120],
                # 間仕切り壁の場合：せっこうボード9.5mm + 断熱材 + 合板12mm
                GeneralPartType.BOUNDARY_WALL: [gypsum_board9_5, insulation, gypsum_board9_5],
                # 間仕切り天井の場合：せっこうボード9.5mm + コンクリート120mm + 断熱材 + 合板24mm
                GeneralPartType.UPWARD_BOUNDARY_FLOOR: [gypsum_board9_5, concrete120, insulation, plywood24],
                # 間仕切り床の場合： 合板24mm + 断熱材 + コンクリート120mm + せっこうボード9.5mm
                GeneralPartType.DOWNWARD_BOUNDARY_FLOOR: [plywood24, insulation, concrete120, gypsum_board9_5]
            }[self.general_part_type]
        }[self._weight]

        # 断熱材以外の熱抵抗の合計, m2K/W
        # リスト要素がLayerクラスの場合に熱抵抗を合計する。
        r_other = sum([layer.r for layer in default_layers if type(layer) == Layer])

        # 目標とする層全体の熱抵抗（表面熱伝達抵抗を含む）, m2K/W
        # 目標U値の逆数から目標R値をだす。
        r_target = 1 / self._u_value

        # 目標とする断熱材の熱抵抗, m2K/W
        # 次に室内側と室外側の熱伝達抵抗、および断熱材を除く層の熱抵抗を減じ、目標とする断熱材の熱抵抗をだす。
        # もし目標とする断熱材の熱抵抗値が0を下回っている場合は、目標とする断熱材の熱抵抗値を0とする。
        # この場合、無断熱になることを意味する。
        # また、目標とするU値を満たさないことになる。
        r_ins_target = max(r_target - self.r_srf_ex - r_other - self.r_srf_in, 0.0)

        # 断熱材の層は必ず1つであることを確認する。
        if len([layer for layer in default_layers if type(layer) == Material]) != 1:
            raise Exception

        # 目標とする断熱材の厚さ, m
        # 目標とする断熱材の熱抵抗(m2K/W)に熱伝導率(W/mK)を乗じて目標とする厚さ(m)をだす。
        t_target = r_ins_target * insulation.thermal_conductivity

        gps = GeneralPartSpecDetail(
            r_srf_in=self.r_srf_in,
            r_srf_ex=self.r_srf_ex,
            parts=[
                GeneralPartPart(
                    name='sole_part',
                    part_area_ratio=1.0,
                    layers=[
                        self._make_layers_from_default_layers(
                            layer=layer,
                            t_target=t_target
                        ) for layer in default_layers
                    ]
                )
            ]
        )

        return gps

    @staticmethod
    def _make_layers_from_default_layers(layer: Union[Layer, Material], t_target: float):

        if type(layer) == Layer:
            return deepcopy(layer)
        elif type(layer) == Material:
            return Layer(
                name=layer.material_name,
                heat_resistance_input_method=HeatResistanceInputMethod.CONDUCTIVITY,
                thickness=t_target,
                volumetric_specific_heat=layer.volumetric_specific_heat,
                thermal_conductivity=layer.thermal_conductivity
            )
        else:
            raise Exception()


class GeneralPartSpecUValueOther(GeneralPartSpecUValue):

    def __init__(self, general_part_type: GeneralPartType, u_value_other: float, weight: str):

        super().__init__(
            general_part_type=general_part_type,
            u_value=u_value_other,
            weight=weight
        )

    @classmethod
    def make_from_dict(cls, general_part_type: GeneralPartType, d: Dict):

        return GeneralPartSpecUValueOther(
            general_part_type=general_part_type,
            u_value_other=d['u_value_other'],
            weight=d['weight']
        )

    def get_as_dict(self):

        return {
            'structure': 'other',
            'u_value_other': self._u_value,
            'weight': self._weight
            }


class IArea(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def area(self) -> float:
        pass


class UpperArealEnvelope(IArea):

    def __init__(self, name: str, next_space: str, direction: str, area: float, space_type: str):
        """

        Args:
            name: 名称
            next_space: 隣接する空間の種類
            direction: 方位
            area: 面積, m2
            space_type: 接する室の用途
        """

        self._name = name
        self._next_space = next_space
        self._direction = direction
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

    def get_h(self, region) -> float:
        """
        温度差係数を取得する。
        Args:
            region: 地域の区分
        Returns:
            温度差係数
        """

        return factor_h.get_h(region=region, next_space=self.next_space)

    def get_nu(self, region: int, season: str) -> float:
        """
        方位係数を取得する。
        Args:
            region: 地域の区分
            season: 期間
        Returns:
            方位係数
        """

        if self.next_space == 'outdoor':
            return factor_nu.get_nu(region=region, season=season, direction=self._direction)
        else:
            return 0.0


class IGetQ(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_q(self, region: int) -> float:
        pass


class IGetM(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_m(self, region: int, season: str) -> float:
        pass


class GeneralPartNoSpec(UpperArealEnvelope):
    """
    「部位の仕様」情報を保持しない一般部位クラス
    """

    def __init__(
            self,
            name: str,
            general_part_type: GeneralPartType,
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

        super().__init__(name=name, next_space=next_space, direction=direction, area=area, space_type=space_type)
        self._general_part_type = general_part_type
        self._sunshade = sunshade

    @property
    def general_part_type(self) -> GeneralPartType:
        """
        種類を取得する。
        Returns:
            種類
        """

        return self._general_part_type

    @property
    def sunshade(self) -> factor_f.SunshadeOpaque:
        """
        日よけ（不透明部位）を取得する。
        Returns:
            日よけ（不透明部位）
        """
        return self._sunshade


class GeneralPart(GeneralPartNoSpec, IGetQ, IGetM):
    """
    一般部位
    """

    def __init__(
            self,
            name: str,
            general_part_type: GeneralPartType,
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

        general_part_type = GeneralPartType(d['general_part_type'])

        return GeneralPart(
            name=d['name'],
            general_part_type=general_part_type,
            next_space=d['next_space'],
            direction=d['direction'],
            area=d['area'],
            space_type=d['space_type'],
            sunshade=factor_f.SunshadeOpaque.make_sunshade_opaque(d=d['sunshade']),
            general_part_spec=GeneralPartSpec.make_general_part_spec(
                d=d['spec'],
                general_part_type=general_part_type
            )
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

    @property
    def general_part_spec(self):
        return self._general_part_spec

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

        if self.next_space == 'outdoor':
            return self.area * self.get_eta() * self.get_nu(region=region, season=season) \
                   * self.sunshade.get_f_sh(region=region, season=season)
        else:
            return 0.0

    def get_as_dict(self) -> Dict:

        return {
            'name': self._name,
            'general_part_type': self.general_part_type.value,
            'next_space': self.next_space,
            'direction': self.direction,
            'area': self.area,
            'space_type': self.space_type,
            'spec': self.general_part_spec.get_as_dict(),
            'sunshade': self.sunshade.get_as_dict()
        }

    def make_initializer_dict(self, u_add: float, region: int) -> List[Dict]:

        gps_dicts = self.general_part_spec.make_initializer_dict(name=self.name, area=self.area, u_add=u_add)

        connected_room_id = {
            'main_occupant_room': 0,
            'other_occupant_room': 1,
            'non_occupant_room': 2,
            'underfloor': 3
        }[self.space_type]

        is_sun_striked_outside = {
            'outdoor': True,
            'open_space': False,
            'closed_space': False,
            'open_underfloor': False,
            'air_conditioned': False,
            'closed_underfloor': False
        }[self.next_space]

        is_solar_absorbed_inside = {
            GeneralPartType.ROOF: False,
            GeneralPartType.CEILING: False,
            GeneralPartType.WALL: False,
            GeneralPartType.FLOOR: True,
            GeneralPartType.BOUNDARY_WALL: False,
            GeneralPartType.UPWARD_BOUNDARY_FLOOR: False,
            GeneralPartType.DOWNWARD_BOUNDARY_FLOOR: True
        }[self.general_part_type]

        # TODO: ここに　is_floor を新規追加し、仕様書（csv）の方も対応させて変更する。

        solar_shading_part = self.sunshade.make_initializer_dict()

        gp_dicts = []

        for gps_dict in gps_dicts:

            d = {
                'name': gps_dict['name'],
                'connected_room_id': connected_room_id,
                'boundary_type': 'external_general_part',
                'area': gps_dict['area'],
                'is_sun_striked_outside': is_sun_striked_outside,
                'temp_dif_coef': self.get_h(region=region),
                'is_solar_absorbed_inside': is_solar_absorbed_inside,
                'inside_heat_transfer_resistance': gps_dict['inside_heat_transfer_resistance'],
                'outside_heat_transfer_resistance': gps_dict['outside_heat_transfer_resistance'],
                'outside_emissivity': 0.9,
                'outside_solar_absorption': 0.8,
                'layers': gps_dict['layers'],
                'solar_shading_part': solar_shading_part
            }

            if is_sun_striked_outside:
                d.update(direction=self.direction)

            gp_dicts.append(d)

        return gp_dicts


class WindowSpec:

    def __init__(
            self,
            u: float,
            eta_d_h: float,
            eta_d_c: float,
            glass_type: GlassType,
            flame_type: FlameType
    ):
        """
        Args:
            u: U値, W/m2K
            eta_d_h: 暖房期のηd値, (W/m2)/(W/m2)
            eta_d_c: 冷房期のηd値, (W/m2)/(W/m2)
            glass_type: ガラスの層数
            flame_type: 建具の種類
        """

        self._u = u
        self._eta_d_h = eta_d_h
        self._eta_d_c = eta_d_c
        self._glass_type = glass_type
        self._flame_type = flame_type

    @classmethod
    def make_window_spec(cls, d: Dict):
        """
        窓の仕様を表す辞書から WindowSpec クラスを作成する。
        Args:
            d: 窓の仕様を表す辞書
        Returns:
            WindowSpec クラス
        """

        return WindowSpec(
            u=d['u_value'],
            eta_d_h=d['eta_d_h_value'],
            eta_d_c=d['eta_d_c_value'],
            glass_type=GlassType(d['glass_type']),
            flame_type=FlameType(d['flame_type'])
        )

    def get_eta_d(self, season: str):
        """
        ηd値を取得する。
        Args:
            season: 暖冷房期間
        Returns:
            ηd値, (W/m2)/(W/m2)
        """

        if season == 'heating':
            return self._eta_d_h
        elif season == 'cooling':
            return self._eta_d_c
        else:
            raise Exception

    def get_as_dict(self) -> Dict:

        return {
            'u_value': self._u,
            'eta_d_h_value': self._eta_d_h,
            'eta_d_c_value': self._eta_d_c,
            'glass_type': self._glass_type.value,
            'flame_type': self._flame_type.value
        }

    @property
    def u(self) -> float:
        """
        U値を取得する。
        Returns:
            U値, W/m2K
        """
        return self._u

    @property
    def eta_d_h(self) -> float:
        """
        ηd_h値を取得する。
        Returns:
            ηd_h値, (W/m2)/(W/m2)
        """
        return self._eta_d_h

    @property
    def eta_d_c(self) -> float:
        """
        ηd_c値を取得する。
        Returns:
            ηd_c値, (W/m2)/(W/m2)
        """
        return self._eta_d_c

    @property
    def glass_type(self) -> GlassType:
        """
        ガラスの種類（枚数）を取得する。
        Returns:
            ガラスの種類（枚数）
        """
        return self._glass_type

    @property
    def flame_type(self) -> FlameType:
        """
        建具の種類を取得する。
        Returns:
            建具の種類
        """
        return self._flame_type


class WindowNoSpec(UpperArealEnvelope):
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

        super().__init__(name=name, next_space=next_space, direction=direction, area=area, space_type=space_type)
        self._sunshade = sunshade

    @property
    def sunshade(self) -> factor_f.SunshadeTransient:
        """
        日よけ（不透明部位）を取得する。
        Returns:
            日よけ（不透明部位）
        """
        return self._sunshade

    def get_f(self, region: int, season: str):
        """
        日射熱取得補正係数を計算する。
        Args:
            region: 地域の区分
            season: 期間
        Returns:
            日射熱取得補正係数
        TODO:
        「指標->LV2」の変換においてガラスの構成が決まらない段階でf値を決定する必要があるため、WindowNoSpecクラスにこの関数を
        おいておくが、本来であれば、ガラスの構成がわかった上でf値を計算するのが望ましい。
        従って、この get_f 関数は、Window クラスでオーバーライドし、引数にガラスの構成を与えるようにすべき。
        """

        return self.sunshade.get_f(region=region, season=season, direction=self.direction)


class Window(WindowNoSpec, IGetQ, IGetM):
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

    @property
    def window_spec(self):
        return self._window_spec

    def get_u(self):
        return self._window_spec.u

    def get_q(self, region: int):
        return self.area * self.get_u() * self.get_h(region=region)

    def get_eta_d(self, season: str):
        """
        ηd値を取得する。
        Args:
            season: 暖冷房期間
        Returns:
            ηd値, (W/m2)/(W/m2)
        """
        return self._window_spec.get_eta_d(season=season)

    def get_m(self, region: int, season: str) -> float:
        return self.get_eta_d(season=season) \
               * self.area \
               * self.sunshade.get_f(region=region, season=season, direction=self.direction) \
               * self.get_nu(region=region, season=season)

    def get_as_dict(self):

        return {
            'name': self.name,
            'next_space': self.next_space,
            'direction': self.direction,
            'area': self.area,
            'space_type': self.space_type,
            'sunshade': self.sunshade.get_as_dict(),
            'spec': self.window_spec.get_as_dict()
        }

    def make_initializer_dict(self):

        return {
            'name': self.name,

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


class DoorNoSpec(UpperArealEnvelope):
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

        super().__init__(name=name, next_space=next_space, direction=direction, area=area, space_type=space_type)
        self._sunshade = sunshade

    @property
    def sunshade(self) -> factor_f.SunshadeOpaque:
        """
        日よけ（不透明部位）を取得する。
        Returns:
            日よけ（不透明部位）
        """
        return self._sunshade


class Door(DoorNoSpec, IGetQ, IGetM):
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

    @property
    def door_spec(self):
        return self._door_spec

    def get_u(self):
        return self._door_spec.get_u()

    def get_q(self, region: int):
        return self.area * self.get_u() * self.get_h(region=region)

    def get_eta(self):
        return self._door_spec.get_eta()

    def get_m(self, region: int, season: str) -> float:

        if self.next_space == 'outdoor':
            return self.area * self.get_eta() * self.get_nu(region=region, season=season) \
                   * self.sunshade.get_f_sh(region=region, season=season)
        else:
            return 0.0

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

    @property
    def earthfloor_perimeter_spec(self):
        return self._earthfloor_perimeter_spec

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


class EarthfloorCenter(EarthfloorCenterNoSpec):

    def __init__(self, name: str, area: float, space_type: str, earthfloor_center_spec: EarthfloorCenterSpec):
        """

        Args:
            name: 名称
            area: 面積, m2
            space_type: 接する室の用途
            earthfloor_center_spec:
        """

        super().__init__(name=name, area=area, space_type=space_type)
        self._earthfloor_center_spec = earthfloor_center_spec

    @classmethod
    def make_earthfloor_center(cls, d: Dict):
        return EarthfloorCenter(
            name=d['name'],
            area=d['area'],
            space_type=d['space_type'],
            earthfloor_center_spec=EarthfloorCenterSpec.make_earthfloor_center_spec(d=d['spec'])
        )

    @classmethod
    def make_earthfloor_centers(cls, ds: List[Dict]):
        return [EarthfloorCenter.make_earthfloor_center(d) for d in ds]

    @property
    def earthfloor_center_spec(self):
        return self._earthfloor_center_spec

    def get_as_dict(self):

        return {
            'name': self.name,
            'area': self.area,
            'space_type': self.space_type,
            'spec': self._earthfloor_center_spec.get_as_dict()
        }


class HeatbridgeSpec:

    def __init__(self, psi_value: float):

        self._psi_value = psi_value

    @classmethod
    def make_heatbridge_spec(cls, d: Dict):

        return HeatbridgeSpec(psi_value=d['psi_value'])

    def get_psi(self):
        return self._psi_value

    def get_eta(self):
        return 0.034 * self.get_psi()

    def get_as_dict(self):

        return {
            'psi_value': self._psi_value
        }


class HeatbridgeNoSpec:

    def __init__(self, name: str, next_spaces: List[str], directions: List[str], length: float, space_type: str):
        """
        Args:
            name: 名称
            next_spaces: 隣接する空間の種類
            directions: 方位
            length: 長さ, m
            space_type: 接する室の名称
        """
        self._name = name
        self._next_spaces = next_spaces
        self._directions = directions
        self._length = length
        self._space_type = space_type

    @property
    def name(self):
        return self._name

    @property
    def next_spaces(self):
        return self._next_spaces

    @property
    def directions(self):
        return self._directions

    @property
    def length(self):
        return self._length

    @property
    def space_type(self):
        return self._space_type

    def get_hs(self, region: int):
        return [factor_h.get_h(region=region, next_space=next_space) for next_space in self._next_spaces]

    def get_nus(self, region: int, season: str) -> List[float]:
        """
        方位係数を取得する。
        Args:
            region: 地域の区分
            season: 期間
        Returns:
            方位係数
        """

        def get_nu(next_space, direction):
            if next_space == 'outdoor':
                return factor_nu.get_nu(region=region, season=season, direction=direction)
            else:
                return 0.0

        return [
            get_nu(next_space=next_space, direction=direction)
            for next_space, direction in zip(self._next_spaces, self._directions)
        ]


class Heatbridge(HeatbridgeNoSpec, IGetQ, IGetM):

    def __init__(
            self,
            name: str,
            next_spaces: List[str],
            directions: List[str],
            length: float,
            space_type: str,
            heatbridge_spec: HeatbridgeSpec
    ):
        """
        Args:
            name: 名称
            next_spaces: 隣接する空間の種類
            directions: 方位
            length: 長さ, m
            space_type: 接する室の名称
            heatbridge_spec: 仕様
        """

        super().__init__(
            name=name,
            next_spaces=next_spaces,
            directions=directions,
            length=length,
            space_type=space_type
        )
        self._heatbridge_spec = heatbridge_spec

    @classmethod
    def make_heatbridge(cls, d: Dict):
        return Heatbridge(
            name=d['name'],
            next_spaces=d['next_spaces'],
            directions=d['directions'],
            length=d['length'],
            space_type=d['space_type'],
            heatbridge_spec=HeatbridgeSpec.make_heatbridge_spec(d=d['spec'])
        )

    @classmethod
    def make_heatbridges(cls, ds: List[Dict]):
        return [Heatbridge.make_heatbridge(d) for d in ds]

    @property
    def heatbridge_spec(self):
        return self._heatbridge_spec

    def get_psi(self):
        return self._heatbridge_spec.get_psi()

    def get_q(self, region: int):
        hs = self.get_hs(region=region)
        h = sum(hs) / len(hs)
        return self.length * self.get_psi() * h

    def get_eta(self) -> float:
        """
        η値を取得する。
        Returns:
            η値, (W/m)/(W/m2)
        """

        return self._heatbridge_spec.get_eta()

    def get_m(self, region: int, season: str) -> float:
        """
        m値を取得する。
        Args:
            region: 地域の区分
            season: 期間
        Returns:
            m値, W/(W/m2)
        """

        nus = self.get_nus(region=region, season=season)
        nu = sum(nus) / len(nus)

        return self.length * self.get_eta() * nu

    def get_as_dict(self):

        return {
            'name': self.name,
            'next_spaces': self.next_spaces,
            'directions': self.directions,
            'length': self.length,
            'space_type': self.space_type,
            'spec': self._heatbridge_spec.get_as_dict()
        }


class InnerFloor:

    def __init__(
            self,
            name: str,
            area: float,
            upper_space_type: str,
            lower_space_type,
            layers: List[Layer]
    ):

        self._name = name
        self._area = area
        self._upper_space_type = upper_space_type
        self._lower_space_type = lower_space_type
        self._layers = layers

    @classmethod
    def make_inner_floor(cls, d: Dict):
        return InnerFloor(
            name=d['name'],
            area=d['area'],
            upper_space_type=d['upper_space_type'],
            lower_space_type=d['lower_space_type'],
            layers=Layer.make_layers(ds=d['spec']['layers'])
        )

    @classmethod
    def make_inner_floors(cls, ds: List[Dict]):
        return [cls.make_inner_floor(d=d) for d in ds]

    @property
    def name(self):
        return self._name

    @property
    def area(self):
        return self._area

    @property
    def upper_space_type(self):
        return self._upper_space_type

    @property
    def lower_space_type(self):
        return self._lower_space_type

    def get_as_dict(self):

        return {
            'name': self.name,
            'area': self.area,
            'upper_space_type': self.upper_space_type,
            'lower_space_type': self.lower_space_type,
            'spec': {
                'layers': [layer.get_as_dict() for layer in self._layers]
            }
        }


class InnerWall:

    def __init__(
            self,
            name: str,
            area: float,
            space_type_1: str,
            space_type_2: str,
            layers: List[Layer]
    ):

        self._name = name
        self._area = area
        self._space_type_1 = space_type_1
        self._space_type_2 = space_type_2
        self._layers = layers

    @classmethod
    def make_inner_wall(cls, d: Dict):
        return InnerWall(
            name=d['name'],
            area=d['area'],
            space_type_1=d['space_type_1'],
            space_type_2=d['space_type_2'],
            layers=Layer.make_layers(ds=d['spec']['layers'])
        )

    @classmethod
    def make_inner_walls(cls, ds: Dict):
        return [cls.make_inner_wall(d=d) for d in ds]

    @property
    def name(self):
        return self._name

    @property
    def area(self):
        return self._area

    @property
    def space_type_1(self):
        return self._space_type_1

    @property
    def space_type_2(self):
        return self._space_type_2

    def get_as_dict(self):

        return {
            'name': self.name,
            'area': self.area,
            'space_type_1': self.space_type_1,
            'space_type_2': self.space_type_2,
            'spec': {
                'layers': [layer.get_as_dict() for layer in self._layers]
            }
        }
