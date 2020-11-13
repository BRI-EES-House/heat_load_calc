from typing import Dict
import abc

# ⽇射取得率補正係数
# ガラスの仕様の区分は、区分1（単板ガラス）を想定する。
# ⽅位が北・北東・東・南東・南・南⻄・⻄・北⻄の窓については、⽇除け下端から窓上端までの垂直⽅向の
# 距離︓窓の開口高さ寸法：壁面からの日よけの張り出し寸法＝3:0:1とする。
# 8地域の暖房期は、8地域の冷房期で代用。
# 平成28年省エネルギー基準に準拠したエネルギー消費性能の評価に関する技術情報（住宅）
# 2.エネルギー消費性能の算定⽅法
# 2.2 算定⽅法
# 第三章 暖冷房負荷と外皮性能
# 第四節 日射熱取得
# 付録 B 大部分がガラスで構成されている窓等の開口部における取得日射熱補正係数
# データ「取得日射熱補正係数」 表 1(a) 屋根又は屋根の直下の天井に設置されている開口部の暖房期の取得日
# 射熱補正係数 表 1(b) 屋根又は屋根の直下の天井に設置されている開口部の冷房期の取得日射熱補正係数


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

    def get_f_sh(self, region: int, season: str):

        raise NotImplementedError()

    def get_as_dict(self):

        return {
            'x1': self._x1,
            'x2': self._x2,
            'x3': self._x3,
            'y1': self._y1,
            'y2': self._y2,
            'y3': self._y3,
            'z_x_pls': self._z_x_pls,
            'z_x_mns': self._z_x_mns,
            'z_y_pls': self._z_y_pls,
            'z_y_mns': self._z_y_mns
        }

    @classmethod
    def make_sunshade_complex(cls, d: Dict):

        return SunshadeComplexKernel(
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
    def get_f_sh(self, region: int, season: str):
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
                    sunshade_complex=SunshadeComplexKernel.make_sunshade_complex(d=d)
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

    def get_f_sh(self, region: int, season: str):

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

    def get_f_sh(self, region: int, season: str):

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

    def __init__(self, sunshade_complex: SunshadeComplexKernel):

        self._sunshade_complex = sunshade_complex

    def get_f_sh(self, region: int, season: str):

        return self._sunshade_complex.get_f_sh(region=region, season=season)

    def get_as_dict(self):

        return {
            'is_defined': True,
            'input': 'complex',
            'spec': self._sunshade_complex.get_as_dict()
        }

    def make_initializer_dict(self):
        return {
            'existence': True,
            'input_method': 'detailed',
            'x1': self._sunshade_complex.x1,
            'x2': self._sunshade_complex.x2,
            'x3': self._sunshade_complex.x3,
            'y1': self._sunshade_complex.y1,
            'y2': self._sunshade_complex.y2,
            'y3': self._sunshade_complex.y3,
            'z_x_pls': self._sunshade_complex.z_x_pls,
            'z_x_mns': self._sunshade_complex.z_x_mns,
            'z_y_pls': self._sunshade_complex.z_y_pls,
            'z_y_mns': self._sunshade_complex.z_y_mns
        }


class SunshadeTransient:

    @abc.abstractmethod
    def get_f(self, region: int, season: str, direction: str):
        pass

    @abc.abstractmethod
    def get_as_dict(self):
        pass

    @classmethod
    def make_sunshade_transient(cls, d: Dict):

        if d['is_defined']:
            if d['input'] == 'not_input':
                return SunshadeTransientNotInput()
            elif d['input'] == 'not_exist':
                raise NotImplementedError
            elif d['input'] == 'simple':
                return SunshadeTransientExistSimple(depth=d['depth'], d_h=d['d_h'], d_e=d['d_e'])
            elif d['input'] == 'complex':
                raise NotImplementedError
            else:
                raise KeyError()
        else:
            return SunshadeTransientNotDefined()


class SunshadeTransientNotDefined(SunshadeTransient):

    def __init__(self):

        pass

    def get_f(self, region: int, season: str, direction: str):

        raise Exception('日よけが未定義にも関わらず日よけ効果係数の計算が呼び出されました。')

    def get_as_dict(self):

        return {
            'is_defined': False
        }


class SunshadeTransientNotInput(SunshadeTransient):

    def __init__(self):

        pass

    def get_f(self, region: int, season: str, direction: str):

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


# class SunshadeTransientNotExist


class SunshadeTransientExistSimple(SunshadeTransient):

    def __init__(self, depth, d_h, d_e):

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

    def get_f(self, region: int, season: str, direction: str):
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
                if direction == 'sw' or direction == 's' or direction == 'se':
                    return min(0.01 * (5 + 20 * (3 * self._d_e + self._d_h)/self._depth), 0.72)
                elif (direction == 'n' or direction == 'ne' or direction == 'e'
                      or direction == 'nw' or direction == 'w'):
                    return min(0.01 * (10 + 15 * (2 * self._d_e + self._d_h) / self._depth), 0.72)
                elif direction == 'top':
                    return 1.0
                elif direction == 'bottom':
                    return 0.0
                else:
                    raise ValueError()
        elif season == 'cooling':
            if region == 8:
                if direction == 'sw' or direction == 's' or direction == 'se':
                    return min(0.01 * (16 + 19 * (2 * self._d_e + self._d_h) / self._depth), 0.93)
                elif (direction == 'n' or direction == 'ne' or direction == 'e'
                      or direction == 'nw' or direction == 'w'):
                    return min(0.01 * (16 + 24 * (2 * self._d_e + self._d_h) / self._depth), 0.93)
                elif direction == 'top':
                    return 1.0
                elif direction == 'bottom':
                    return 0.0
                else:
                    raise ValueError()
            else:
                if direction == 's':
                    return min(0.01 * (24 + 9 * (3 * self._d_e + self._d_h) / self._depth), 0.93)
                elif (direction == 'n' or direction == 'ne' or direction == 'e' or direction == 'se'
                      or direction == 'nw' or direction == 'w' or direction == 'sw'):
                    return min(0.01 * (16 + 24 * (2 * self._d_e + self._d_h) / self._depth), 0.93)
                elif direction == 'top':
                    return 1.0
                elif direction == 'bottom':
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
