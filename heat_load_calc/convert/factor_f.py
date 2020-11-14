"""
日よけに関して定義する。
日よけには、
    ・壁やドアなどの不透明部位にかかる日よけ（軒・アマハジなど）
    ・窓などの透明部位にかかる日よけ（ひさし）
に大別される。

＜壁やドアなどの不透明部位にかかる日よけ＞
壁やドアなどの不透明部位にかかる日よけは、
    ・間仕切り壁などの外気に面さない（日射のあたらない）不透明部位の外皮に見られるように日よけの有無が定義されない場合
    ・外気に面する壁ではあるが日よけの有無や形状を指定しない（入力を省略する）場合
    ・日よけの形状をきちんと入力する場合
に大別され、それぞれ、
    ・SunshadeOpaqueNotDefined
    ・SunshadeOpaqueNotInput
    ・SunshadeOpaqueInput
で定義される。
各クラスは、SunshadeOpaqueクラスで引数である辞書の内容に応じてデシリアライズ化される。
各々のクラスは必ず以下の関数を持つ。
    ・日よけ効果係数の計算 = get_f_sh
    ・辞書形式にシリアライズ化 = get_as_dict
    ・initializer用辞書形式にシリアライズ化 = make_initializer_dict
ただし、SunshadeOpaqueNotDefined クラスにおいて、get_f_sh 関数が呼び出された場合は、
日よけの効果係数は定義できないため必ずエラーが返る。

＜窓などの透明部位にかかる日よけ＞
窓などの透明部位にかかる日よけは、
    ・共用部廊下に面した窓など外気に面さない（日射のあたらない）と東映部位の外皮に見られるように日よけの有無が定義されない場合
    ・外気に面する窓ではあるが日よけの有無や形状を指定しない（入力を省略する）場合
    ・外気に面する窓ではあり日よけが存在しない場合
    ・日よけの形状をきちんと入力する場合で簡易法を用いる場合
    ・日よけの形状をきちんと入力する場合で詳細法を用いる場合
に大別され、それぞれ、
    ・SunshadeTransientNotDefined
    ・SunshadeTransientNotInput
    ・SunshadeTransientExist
    ・SunshadeTransientExistSimple
    ・SunshadeTransientExistComplex
で定義される。
各クラスは、SunshadeTransientクラスで引数である辞書の内容に応じてデシリアライズ化される。
各々のクラスは必ず以下の関数を持つ。
    ・日射熱取得補正係数の計算 = get_f
    ・辞書形式にシリアライズ化 = get_as_dict
    ・initializer用辞書形式にシリアライズ化 = make_initializer_dict
ただし、SunshadeOpaqueNotDefined クラスにおいて、get_f 関数が呼び出された場合は、
日射熱取得補正係数は定義できないため必ずエラーが返る。
なお、日射熱取得補正係数は、日よけの効果係数とガラスの斜入射特性の補正係数の積である。
"""

from typing import Dict
import abc
from heat_load_calc.external.factor_nu import Direction


class SunshadeComplexKernel:

    def __init__(
            self,
            x1: float,
            x2: float,
            x3: float,
            y1: float,
            y2: float,
            y3: float,
            z_x_pls: float,
            z_x_mns: float,
            z_y_pls: float,
            z_y_mns: float
    ):

        self._x1 = x1
        self._x2 = x2
        self._x3 = x3
        self._y1 = y1
        self._y2 = y2
        self._y3 = y3
        self._z_x_pls = z_x_pls
        self._z_x_mns = z_x_mns
        self._z_y_pls = z_y_pls
        self._z_y_mns = z_y_mns

    def get_f_sh(self, region: int, season: str, direction: Direction):

        raise NotImplementedError()

    @property
    def x1(self):
        return self._x1

    @property
    def x2(self):
        return self._x2

    @property
    def x3(self):
        return self._x3

    @property
    def y1(self):
        return self._y1

    @property
    def y2(self):
        return self._y2

    @property
    def y3(self):
        return self._y3

    @property
    def z_x_pls(self):
        return self._z_x_pls

    @property
    def z_x_mns(self):
        return self._z_x_mns

    @property
    def z_y_pls(self):
        return self._z_y_pls

    @property
    def z_y_mns(self):
        return self._z_y_mns


class SunshadeOpaque:

    @abc.abstractmethod
    def get_f_sh(self, region: int, season: str, direction: Direction):
        pass

    @abc.abstractmethod
    def get_as_dict(self):
        pass

    @classmethod
    def make_sunshade_opaque(cls, d: Dict):

        if d['is_defined']:
            if d['input'] == 'not_input':
                return SunshadeOpaqueNotInput()
            elif d['input'] == 'complex':
                return SunshadeOpaqueInput(
                    x1=d['x1'],
                    x2=d['x2'],
                    x3=d['x3'],
                    y1=d['y1'],
                    y2=d['y2'],
                    y3=d['y3'],
                    z_x_pls=d['z_x_pls'],
                    z_x_mns=d['z_x_mns'],
                    z_y_pls=d['z_y_pls'],
                    z_y_mns=d['z_y_mns']
                )
            else:
                raise ValueError('不透明部位における日よけの入力方法（input）に間違った値が指定されました。')
        else:
            return SunshadeOpaqueNotDefined()

    @abc.abstractmethod
    def make_initializer_dict(self):
        pass


class SunshadeOpaqueNotDefined(SunshadeOpaque):

    def __init__(self):

        pass

    def get_f_sh(self, region: int, season: str, direction: Direction):

        raise Exception('日よけが未定義にも関わらず日よけ効果係数の計算が呼び出されました。')

    def get_as_dict(self):

        return {
            'is_defined': False
        }

    def make_initializer_dict(self):

        return {
            'existence': False
        }


class SunshadeOpaqueNotInput(SunshadeOpaque):

    def __init__(self):

        pass

    def get_f_sh(self, region: int, season: str, direction: Direction):

        return 1.0

    def get_as_dict(self):

        return {
            'is_defined': True,
            'input': 'not_input'
        }

    def make_initializer_dict(self):
        return {
            'existence': False
        }


class SunshadeOpaqueInput(SunshadeOpaque):

    def __init__(
            self,
            x1: float, x2: float, x3: float,
            y1: float, y2: float, y3: float,
            z_x_pls: float, z_x_mns: float,
            z_y_pls: float, z_y_mns: float
    ):

        self._sunshade_complex_kernel = SunshadeComplexKernel(
            x1=x1,
            x2=x2,
            x3=x3,
            y1=y1,
            y2=y2,
            y3=y3,
            z_x_pls=z_x_pls,
            z_x_mns=z_x_mns,
            z_y_pls=z_y_pls,
            z_y_mns=z_y_mns
        )

    def get_f_sh(self, region: int, season: str, direction: Direction):

        return self._sunshade_complex_kernel.get_f_sh(region=region, season=season, direction=direction)

    def get_as_dict(self):

        return {
            'is_defined': True,
            'input': 'complex',
            'spec': {
                'x1': self._sunshade_complex_kernel.x1,
                'x2': self._sunshade_complex_kernel.x2,
                'x3': self._sunshade_complex_kernel.x3,
                'y1': self._sunshade_complex_kernel.y1,
                'y2': self._sunshade_complex_kernel.y2,
                'y3': self._sunshade_complex_kernel.y3,
                'z_x_pls': self._sunshade_complex_kernel.z_x_pls,
                'z_x_mns': self._sunshade_complex_kernel.z_x_mns,
                'z_y_pls': self._sunshade_complex_kernel.z_y_pls,
                'z_y_mns': self._sunshade_complex_kernel.z_y_mns
            }
        }

    def make_initializer_dict(self):
        return {
            'existence': True,
            'input_method': 'detailed',
            'x1': self._sunshade_complex_kernel.x1,
            'x2': self._sunshade_complex_kernel.x2,
            'x3': self._sunshade_complex_kernel.x3,
            'y1': self._sunshade_complex_kernel.y1,
            'y2': self._sunshade_complex_kernel.y2,
            'y3': self._sunshade_complex_kernel.y3,
            'z_x_pls': self._sunshade_complex_kernel.z_x_pls,
            'z_x_mns': self._sunshade_complex_kernel.z_x_mns,
            'z_y_pls': self._sunshade_complex_kernel.z_y_pls,
            'z_y_mns': self._sunshade_complex_kernel.z_y_mns
        }


class SunshadeTransient:

    @abc.abstractmethod
    def get_f(self, region: int, season: str, direction: Direction):
        pass

    @abc.abstractmethod
    def get_as_dict(self):
        pass

    @abc.abstractmethod
    def make_initializer_dict(self):
        pass

    @classmethod
    def make_sunshade_transient(cls, d: Dict):

        if d['is_defined']:
            if d['input'] == 'not_input':
                return SunshadeTransientNotInput()
            elif d['input'] == 'not_exist':
                raise SunshadeTransientNotExist()
            elif d['input'] == 'simple':
                return SunshadeTransientExistSimple(depth=d['depth'], d_h=d['d_h'], d_e=d['d_e'])
            elif d['input'] == 'complex':
                raise SunshadeTransientExistDetail(
                    x1=d['x1'],
                    x2=d['x2'],
                    x3=d['x3'],
                    y1=d['y1'],
                    y2=d['y2'],
                    y3=d['y3'],
                    z_x_pls=d['z_x_pls'],
                    z_x_mns=d['z_x_mns'],
                    z_y_pls=d['z_y_pls'],
                    z_y_mns=d['z_y_mns']
                )
            else:
                raise KeyError()
        else:
            return SunshadeTransientNotDefined()


class SunshadeTransientNotDefined(SunshadeTransient):

    def __init__(self):

        pass

    def get_f(self, region: int, season: str, direction: Direction):

        raise Exception('日よけが未定義にも関わらず日よけ効果係数の計算が呼び出されました。')

    def get_as_dict(self):

        return {
            'is_defined': False
        }

    def make_initializer_dict(self):

        return {
            'existence': False
        }


class SunshadeTransientNotInput(SunshadeTransient):

    def __init__(self):

        pass

    def get_f(self, region: int, season: str, direction: Direction):

        if season == 'heating':
            if region == 8:
                raise Exception('8地域における暖房期間が定義されていません。')
            else:
                return 0.51
        elif season == 'cooling':
            return 0.93
        else:
            raise ValueError()

    def get_as_dict(self):

        return {
            'is_defined': True,
            'input': 'not_input'
        }

    def make_initializer_dict(self):

        return {
            'existence': True,
            'input_method': 'default'
        }


class SunshadeTransientNotExist(SunshadeTransient):

    def __init__(self):
        pass

    def get_f(self, region: int, season: str, direction: Direction):
        raise NotImplementedError()

    def get_as_dict(self):
        return {
            'is_defined': True,
            'input': 'not_exist'
        }

    def make_initializer_dict(self):

        return {
            'existence': False
        }


class SunshadeTransientExistSimple(SunshadeTransient):

    def __init__(self, depth: float, d_h: float, d_e: float):

        self._depth = depth
        self._d_h = d_h
        self._d_e = d_e

    @property
    def depth(self):
        return self._depth

    @property
    def d_h(self):
        return self._d_h

    @property
    def d_e(self):
        return self._d_e

    def get_f(self, region: int, season: str, direction: Direction):
        """

        Args:
            region: 地域の区分
            season: 期間
            direction: 方位
        Returns:
            f値
        """

        if season == 'heating':
            if region == 8:
                raise Exception('8地域における暖房期間が定義されていません。')
            else:
                if direction in [Direction.SW, Direction.S, Direction.SE]:
                    return min(0.01 * (5 + 20 * (3 * self._d_e + self._d_h)/self._depth), 0.72)
                elif direction in [Direction.N, Direction.NE, Direction.E, Direction.NW, Direction.W]:
                    return min(0.01 * (10 + 15 * (2 * self._d_e + self._d_h) / self._depth), 0.72)
                elif direction == Direction.TOP:
                    return 1.0
                elif direction == Direction.BOTTOM:
                    return 0.0
                else:
                    raise ValueError()
        elif season == 'cooling':
            if region == 8:
                if direction in [Direction.SW, Direction.S, Direction.SE]:
                    return min(0.01 * (16 + 19 * (2 * self._d_e + self._d_h) / self._depth), 0.93)
                elif direction in [Direction.N, Direction.NE, Direction.E, Direction.NW, Direction.W]:
                    return min(0.01 * (16 + 24 * (2 * self._d_e + self._d_h) / self._depth), 0.93)
                elif direction == Direction.TOP:
                    return 1.0
                elif direction == Direction.BOTTOM:
                    return 0.0
                else:
                    raise ValueError()
            else:
                if direction == Direction.S:
                    return min(0.01 * (24 + 9 * (3 * self._d_e + self._d_h) / self._depth), 0.93)
                elif direction in [Direction.N, Direction.NE, Direction.E, Direction.SE,
                                   Direction.NW, Direction.W, Direction.SW]:
                    return min(0.01 * (16 + 24 * (2 * self._d_e + self._d_h) / self._depth), 0.93)
                elif direction == Direction.TOP:
                    return 1.0
                elif direction == Direction.BOTTOM:
                    return 0.0
                else:
                    raise ValueError()
        else:
            raise ValueError()

    def get_as_dict(self):

        return {
            'is_defined': True,
            'input': 'simple',
            'depth': self._depth,
            'd_h': self._d_h,
            'd_e': self._d_e
        }

    def make_initializer_dict(self):

        return {
            'existence': True,
            'input_method': 'simple',
            'depth': self._depth,
            'd_h': self._d_h,
            'd_e': self._d_e
        }


class SunshadeTransientExistDetail(SunshadeTransient):

    def __init__(
            self,
            x1: float, x2: float, x3: float,
            y1: float, y2: float, y3: float,
            z_x_pls: float, z_x_mns: float,
            z_y_pls: float, z_y_mns: float
    ):

        self._sunshade_complex_kernel = SunshadeComplexKernel(
            x1=x1,
            x2=x2,
            x3=x3,
            y1=y1,
            y2=y2,
            y3=y3,
            z_x_pls=z_x_pls,
            z_x_mns=z_x_mns,
            z_y_pls=z_y_pls,
            z_y_mns=z_y_mns
        )

    def get_f(self, region: int, season: str, direction: str):
        """

        Args:
            region: 地域の区分
            season: 期間
            direction: 方位
        Returns:
            f値
        """

        return self._sunshade_complex_kernel.get_f_sh(region=region, season=season)

    def get_as_dict(self):

        return {
            'is_defined': True,
            'input': 'complex',
            'spec': {
                'x1': self._sunshade_complex_kernel.x1,
                'x2': self._sunshade_complex_kernel.x2,
                'x3': self._sunshade_complex_kernel.x3,
                'y1': self._sunshade_complex_kernel.y1,
                'y2': self._sunshade_complex_kernel.y2,
                'y3': self._sunshade_complex_kernel.y3,
                'z_x_pls': self._sunshade_complex_kernel.z_x_pls,
                'z_x_mns': self._sunshade_complex_kernel.z_x_mns,
                'z_y_pls': self._sunshade_complex_kernel.z_y_pls,
                'z_y_mns': self._sunshade_complex_kernel.z_y_mns
            }
        }

    def make_initializer_dict(self):

        return {
            'existence': True,
            'input_method': 'detailed',
            'x1': self._sunshade_complex_kernel.x1,
            'x2': self._sunshade_complex_kernel.x2,
            'x3': self._sunshade_complex_kernel.x3,
            'y1': self._sunshade_complex_kernel.y1,
            'y2': self._sunshade_complex_kernel.y2,
            'y3': self._sunshade_complex_kernel.y3,
            'z_x_pls': self._sunshade_complex_kernel.z_x_pls,
            'z_x_mns': self._sunshade_complex_kernel.z_x_mns,
            'z_y_pls': self._sunshade_complex_kernel.z_y_pls,
            'z_y_mns': self._sunshade_complex_kernel.z_y_mns
        }
