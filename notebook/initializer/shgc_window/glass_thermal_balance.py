""" Evaluation on thermal resistance of float glasses and thermal transmittance of glazing

This module is for evaluation on thermal resistance of float glassess and thermal transmittance of glazing, which is
based on JIS R3107 1988, JIS A2102 2015.

"""

from enum import Enum
from typing import List, Callable
import numpy as np
from scipy import optimize


class GlassDirection(Enum):
    """Direction of the glass

    """
    # Air layer is vertical and heat flow direction is horizontal.
    VERTICAL = 1
    # Air layer is horizontal and heat flow direction is upward.
    HORIZONTAL = 2
    # Air layer faces 45 degree and heat flow direction is upward.
    SLOPE = 3


class AirType(Enum):
    """Type of air

    """

    AIR = 1
    ARGON = 2
    SF6 = 3
    KRYPTON = 4

# region air property functions


def get_interporation_property(temp, v1, v2, v3, v4):
    """
    define the physical property at the designated temperature
        Args:
            temp: temperature, degree C
            v1: the physical property at -10 degree C
            v2: the physical property at 0 degree C
            v3: the physical property at 10 degree C
            v4: the physical property at 20 degree C

        Returns:
            the physical property

    """

    t1 = -10.0
    t2 = 0.0
    t3 = 10.0
    t4 = 20.0

    if temp < t2:
        return v1 * (temp - t2) / (t1 - t2) + v2 * (temp - t1) / (t2 - t1)
    elif temp < t3:
        return v2 * (temp - t3) / (t2 - t3) + v3 * (temp - t2) / (t3 - t2)
    else:
        return v3 * (temp - t4) / (t3 - t4) + v4 * (temp - t3) / (t4 - t3)


def get_rho(temp: float, air_type: AirType) -> float:
    """
    calculate the density of the air

    Args:
        temp: temperature, degree C
        air_type: type of the air

    Returns:
        density, kg/m3
    """

    rho1, rho2, rho3, rho4 = {
        AirType.AIR: (1.326, 1.277, 1.232, 1.189),
        AirType.ARGON: (1.829, 1.762, 1.699, 1.640),
        AirType.SF6: (6.844, 6.602, 6.360, 6.118),
        AirType.KRYPTON: (3.832, 3.690, 3.560, 3.430)
    }[air_type]

    return get_interporation_property(temp, rho1, rho2, rho3, rho4)


def get_mu(temp: float, air_type: AirType) -> float:
    """
    calculate the viscosity(mu value) of the air
    Args:
        temp: temperature, degree C
        air_type: type of the air

    Returns:
        viscosity(mu value), kg/ms
    """

    mu1, mu2, mu3, mu4 = {
        AirType.AIR: (1.661, 1.711, 1.761, 1.811),
        AirType.ARGON: (2.038, 2.101, 2.164, 2.228),
        AirType.SF6: (1.383, 1.421, 1.459, 1.497),
        AirType.KRYPTON: (2.260, 2.330, 2.400, 2.470)
    }[air_type]

    return get_interporation_property(temp, mu1, mu2, mu3, mu4) * 10 ** -5


def get_lambda(temp: float, air_type: AirType) -> float:
    """
    calculate thermal conductivity of the air
    Args:
        temp: temperature, degree C
        air_type: type of the air

    Returns:
        thermal conductivity, W/mK
    """

    lambda1, lambda2, lambda3, lambda4 = {
        AirType.AIR: (2.336, 2.416, 2.496, 2.576),
        AirType.ARGON: (1.584, 1.634, 1.684, 1.734),
        AirType.SF6: (1.119, 1.197, 1.275, 1.354),
        AirType.KRYPTON: (0.842, 0.870, 0.900, 0.926)
    }[air_type]

    return get_interporation_property(temp, lambda1, lambda2, lambda3, lambda4) * 10 ** -2


def get_c_air(air_type: AirType) -> float:
    """
    calculate the specific heat of the air

    Args:
        air_type: type of the air

    Returns:
        specific heat, J/kgK
    """

    return {
        AirType.AIR: 1.008 * 10 ** 3,
        AirType.ARGON: 0.519 * 10 ** 3,
        AirType.SF6: 0.614 * 10 ** 3,
        AirType.KRYPTON: 0.245 * 10 ** 3
    }[air_type]


# endregion


ABSOLUTE_ZERO = 273.15


def get_sigma():
    """
    get Stefan Boltzmann coefficient

    Returns:
        Stefan Boltzmann coefficient
    """

    return 5.67 / 100000000


class Surface:
    """Surface on each side of the glass

    """

    def __init__(self):
        pass

    @property
    def eps(self):
        """get the corrected emissivity

        Returns:
            corrected emissivity

        Notes:
            This method is abstract method and it should be overrided..
        """
        raise NotImplementedError()


class NonLowESurface(Surface):
    """Surface of the glass with non low-E thin film

    """

    def __init__(self):
        super().__init__()

    @property
    def eps(self):
        """get the corrected emissivity

        Returns:
            corrected emissivity

        Notes:
            section 5.2
        """

        return 0.837


class LowESurface(Surface):
    """Surface of the glass with low-E thin film

    """

    def __init__(self, epsilon_n: float):
        """

        Args:
            epsilon_n: vertical emissivity
        """

        self._epsilon_n = epsilon_n
        super().__init__()

    @property
    def epsilon_n(self):
        """

        Returns: vertical emissivity

        """

        return self._epsilon_n

    @property
    def eps(self):
        """get the corrected emissivity

        Returns:
            corrected emissivity

        Notes:
            section 5.2
        """

        x1, y1 = 0.03, 1.22
        x2, y2 = 0.05, 1.18
        x3, y3 = 0.1, 1.14
        x4, y4 = 0.2, 1.1
        x5, y5 = 0.3, 1.06
        x6, y6 = 0.4, 1.03
        x7, y7 = 0.5, 1.0
        x8, y8 = 0.6, 0.98
        x9, y9 = 0.7, 0.96
        x10, y10 = 0.8, 0.95
        x11, y11 = 0.89, 0.94

        # vertical emissivity
        e = self.epsilon_n

        if e < x1:
            raise ValueError()
        elif e < x2:
            c = y1 * (x2 - e) / (x2 - x1) + y2 * (e - x1) / (x2 - x1)
        elif e < x3:
            c = y2 * (x3 - e) / (x3 - x2) + y3 * (e - x2) / (x3 - x2)
        elif e < x4:
            c = y3 * (x4 - e) / (x4 - x3) + y4 * (e - x3) / (x4 - x3)
        elif e < x5:
            c = y4 * (x5 - e) / (x5 - x4) + y5 * (e - x4) / (x5 - x4)
        elif e < x6:
            c = y5 * (x6 - e) / (x6 - x5) + y6 * (e - x5) / (x6 - x5)
        elif e < x7:
            c = y6 * (x7 - e) / (x7 - x6) + y7 * (e - x6) / (x7 - x6)
        elif e < x8:
            c = y7 * (x8 - e) / (x8 - x7) + y8 * (e - x7) / (x8 - x7)
        elif e < x9:
            c = y8 * (x9 - e) / (x9 - x8) + y9 * (e - x8) / (x9 - x8)
        elif e < x10:
            c = y9 * (x10 - e) / (x10 - x9) + y10 * (e - x9) / (x10 - x9)
        elif e < x11:
            c = y10 * (x11 - e) / (x11 - x10) + y11 * (e - x10) / (x11 - x10)
        else:
            raise ValueError()

        return e * c


class MixedAirProperty:
    """Air in the air layer

    """

    def __init__(self, c_air: float, c_argon: float, c_sf6: float, c_krypton):
        """

        Args:
            c_air: volumetric ratio of air, %
            c_argon: volumetric ratio of argon, %
            c_sf6: volumetric ratio of SF6, %
            c_krypton: volumetric ratio of krypton, %
        """

        # confirm that the sum of the volumetric ratio of each air property equals to 100%.
        if c_air + c_argon + c_sf6 + c_krypton != 100.0:
            raise ValueError('気体の容積割合の合計は100.0になる必要があります')

        self._c_air = c_air
        self._c_argon = c_argon
        self._c_sf6 = c_sf6
        self._c_krypton = c_krypton

    def get_mixed_property(self, f: Callable[[AirType], float]) -> float:
        """get the mixed property of the type of 4 gasses

        Args:
            f: the function for getting a specific property of the gas

        Returns:
            a specific property
        """

        return f(AirType.AIR) * self._c_air / 100.0\
            + f(AirType.ARGON) * self._c_argon / 100.0\
            + f(AirType.SF6) * self._c_sf6 / 100.0\
            + f(AirType.KRYPTON) * self._c_krypton / 100.0

    def get_rho(self, temp: float) -> float:
        """
        calculate the density of the air
        Args:
            temp: temperature, degree C

        Returns:
            density, kg/m3
        """

        return self.get_mixed_property(lambda air_type: get_rho(temp, air_type))

    def get_mu(self, temp: float) -> float:
        """
        calculate the viscosity(mu value) of the air
        Args:
            temp: temperature, degree C

        Returns:
            viscosity(mu value), kg/ms
        """

        return self.get_mixed_property(lambda air_type: get_mu(temp, air_type))

    def get_lambda(self, temp: float) -> float:
        """
        calculate thermal conductivity of the air
        Args:
            temp: temperature, degree C

        Returns:
            thermal conductivity, W/mK
        """

        return self.get_mixed_property(lambda air_type: get_lambda(temp, air_type))

    def get_c(self, temp: float) -> float:
        """
        calculate the specific heat of the air
        Args:
            temp: temperature, degree C

        Returns:
            specific heat, J/kgK
        """

        return self.get_mixed_property(lambda air_type: get_c_air(air_type))


class AirLayer:

    def __init__(
            self,
            air_property: MixedAirProperty,
            direction: GlassDirection,
            s: float
    ):
        """

        Args:
            surface1: glass surface 1
            surface2: glass surface 2
            air_property: air property
            direction: direction of the air layer
            s: thickness, m
        """

        self._air_property = air_property
        self._direction = direction
        self._s = s

    def get_a(self) -> float:
        """

        Returns:
            value A

        Notes:
            5.3.1
        """

        return {
            GlassDirection.VERTICAL: 0.035,
            GlassDirection.HORIZONTAL: 0.16,
            GlassDirection.SLOPE: 0.10
        }[self._direction]

    def get_n(self) -> float:
        """

        Returns:
            value n

        Notes:
            5.3.1
        """

        return {
            GlassDirection.VERTICAL: 0.38,
            GlassDirection.HORIZONTAL: 0.28,
            GlassDirection.SLOPE: 0.31
        }[self._direction]

    def get_gr(self, delta_t: float, t_dash_m: float, rho: float, mu_air) -> float:
        """get the Grasshof number

        Args:
            delta_t: temperature difference of the surfaces of the air layer, K
            t_dash_m: average temperature of the air of the air layer, K
            rho: density, kg/m3
            mu_air: viscosity(mu value), kg/ms

        Returns:
            Grasshof number

        Notes:
            equation (7)
        """

        return 9.81 * self._s ** 3 * delta_t * rho ** 2 / t_dash_m / mu_air ** 2

    @staticmethod
    def get_pr(mu_air: float, c_air: float, lambda_air: float) -> float:
        """
        get Prandtl number

        Args:
            mu_air: viscosity(mu value), kg/ms
            c_air: specific heat, J/kgK
            lambda_air: thermal conductivity, W/mK

        Returns:
            Prandtl number

        Notes:
            equation (8)
        """

        return mu_air * c_air / lambda_air

    @staticmethod
    def get_nu(a: float, n: float, gr: float, pr: float) -> float:
        """
        calculate Nusselt value

        Args:
            a: a value
            n: n value
            gr: Grasshof number
            pr: Prandtl number

        Returns:
            Nusselt value

        Notes:
            equation(6)
        """

        return a * (gr * pr) ** n

    @staticmethod
    def get_cc(nu: float) -> float:
        """
        calculate convective effect coefficient

        Args:
            nu: Nusselt number

        Returns:
            convective effect coefficient

        Notes:
            equation (5)
        """

        return max(1.0, nu)

    def get_h_s_with_surfaces_temp(self, theta_f: float, theta_b: float, eps_f: float, eps_b: float) -> float:
        """Calculate the thermal conductance of the air layer between two surfaces.
        The temperatures below are calculated based on the 2 surface temperatures.
            - average of the absolute temperatures at each glass surface of the air layer, K
            - temperature difference of the surfaces of the air layer, K
            - average temperature of the air of the air layer, K
        Args:
            theta_f: surface temperature, degree C
            theta_b: surface temperature, degree C
            eps_f: emissivity of glass surface on the front side
            eps_b: emissivity of glass surface on the back side
        Returns:
            thermal conductance, W/m2k
        Notes:
            theta_f is the temperature of the back side of the front side glass.
            theta_b is the temperature of the front side of the back side glass.
        """

        # average of the absolute temperatures at each glass surface of the air layer, K
        t_m = (theta_f + theta_b) / 2 + ABSOLUTE_ZERO

        # temperature difference of the surfaces of the air layer, K
        delta_t = abs(theta_f - theta_b)

        # average temperature of the air of the air layer, K
        t_dash_m = (theta_f + theta_b) / 2 + ABSOLUTE_ZERO

        # thermal conductance, W/m2k
        h_s = self.get_h_s(t_m=t_m, delta_t=delta_t, t_dash_m=t_dash_m, eps_f=eps_f, eps_b=eps_b)

        return h_s

    def get_h_s(self, t_m: float, delta_t: float, t_dash_m: float, eps_f: float, eps_b: float) -> float:
        """calculate thermal conductance

        Args:
            t_m: average of the absolute temperatures at each glass surface of the air layer, K
            delta_t: temperature difference of the surfaces of the air layer, K
            t_dash_m: average temperature of the air of the air layer, K
            eps_f: emissivity of glass surface on the front side
            eps_b: emissivity of glass surface on the back side
        Returns:
            thermal conductance, W/m2K
        Notes:
            equation (2)
        """

        return self.get_h_r(t_m=t_m, eps_f=eps_f, eps_b=eps_b) + self.get_h_g(delta_t, t_dash_m)

    @staticmethod
    def get_h_r(t_m: float, eps_f: float, eps_b: float) -> float:
        """
        calculate radiative conductance
        Args:
            t_m: average of the absolute temperatures at each glass surface of the air layer, K
            eps_f: emissivity of glass surface on the front side
            eps_b: emissivity of glass surface on the back side
        Returns:
            radiative conductance, W/m2K
        Notes:
            equation (4)
        """

        h_r = 4 * get_sigma() / (1 / eps_f + 1 / eps_b - 1) * t_m ** 3

        return h_r

    def get_h_g(self, delta_t: float, t_dash_m: float) -> float:
        """
        calculate the air conductance
        Args:
            delta_t: temperature difference of the surfaces of the air layer, K
            t_dash_m: average temperature of the air of the air layer, K

        Returns:
            air conductance, W/m2K

        """

        # average temperature of the air of the air layer, degree C
        theta_dash_m = t_dash_m - ABSOLUTE_ZERO

        # a value
        a = self.get_a()

        # n value
        n = self.get_n()

        # density, kg/m3
        rho = self._air_property.get_rho(theta_dash_m)

        # viscosity(mu value), kg/ms
        mu = self._air_property.get_mu(theta_dash_m)

        # specific heat, J/kgK
        c = self._air_property.get_c(theta_dash_m)

        # thermal conductivity, W/mK
        lambda_ = self._air_property.get_lambda(theta_dash_m)

        # Grasshof number
        # Notes: The parameter delta_t should not be negative number.
        gr = self.get_gr(delta_t=abs(delta_t), t_dash_m=t_dash_m, rho=rho, mu_air=mu)

        # Prandtl number
        pr = self.get_pr(mu_air=mu, c_air=c, lambda_air=lambda_)

        # Nusselt value
        nu = self.get_nu(a, n, gr, pr)

        # convective effect coefficient
        cc = self.get_cc(nu)

        # air conductance, W/m2K
        h_g = cc * lambda_ / self._s

        return h_g


class GlassUnit:
    """glass unit class

    This class represents the unit glass.

    Attributes:
        _d (float): thickness, m
        _lmd (float): thermal conductivity, W/mK
    """

    def __init__(self, d: float, lmd: float = 1.0):
        """

        Args:
            d: thickness, m
            lmd: thermal conductivity, W/mK
        Notes:
            The default value of the lambdas is 1.0 W/mK.
        """

        # thickness, m
        self._d = d

        # thermal conductivity, W/mK
        self._lmd = lmd

    @property
    def r(self):
        """get thermal resistance

        Returns:
            thermal resistance, m2K/W
        """

        return self._d / self._lmd


class GlassLayer:
    """glass layer class

    This class represents the unit glass.
    This includes the laminated glass.

    Attributes:
        _gus (List[GlassUnit]): glass units, [number of the glass units]
    """

    def __init__(self, gus: List[GlassUnit], sff: Surface = NonLowESurface(), sfb: Surface = NonLowESurface()):
        """
        Args:
            gus: glass units, [number of the glass units]
        """

        # glass units, [number of the glass units]
        self._gus = gus

        # thermal resistance, m2K/W
        self._r = sum([gu.r for gu in gus])

        # surface
        self._sff = sff
        self._sfb = sfb

    @property
    def r(self):
        """get thermal resistance

        Returns:
            thermal resistance, m2K/W
        """

        return self._r

    @property
    def sff(self):
        return self._sff

    @property
    def sfb(self):
        return self._sfb


class Glass:
    """glass class

    Attributes:
        _gls (GlassLayer): glass layer
        _als (AirLayer): air layer
    """

    def __init__(self, gls: List[GlassLayer], als: List[AirLayer]):
        """

        Args:
            gls: glass layers [number of glass layers]
            als: air layers [number of air layers]
        """

        self._gls = gls
        self._als = als

        n_gl = len(gls)
        n_al = len(als)

        if n_gl - 1 != n_al:
            raise ValueError('The number of air layers and the number of glass layers do not match.')

        # the number of the glass layers.
        self._n_gl = n_gl

    def get_h_e(
            self, surface_method: str = 'JIS_R3107', season: str = '', theta_s: float = None, theta_r_e: float = None):
        """
        Args:
            surface_method: method of the thermal conductance on the surface
                The methods are 'JIS_R3107' or 'JIS_A2103'
            season: the season of the calculation period
            theta_s: external surface temperature, K
            theta_r_e: external radiative temperature, K
        Returns:
            heat transfer coefficient on the outside surface, W/m2 K
        Notes:
            This value is supposed to apply for the vertical glasses.
        """

        if surface_method == 'JIS_A2103':
            t_s = theta_s + ABSOLUTE_ZERO
            t_r_e = theta_r_e + ABSOLUTE_ZERO
            h_r = self._gls[0].sff.eps * get_sigma() * (t_s ** 3 + t_s ** 2 * t_r_e + t_s * t_r_e ** 2 + t_r_e ** 3)
            h_c = {
                'summer': 8.0,
                'winter': 20.0
            }[season]
            return h_r + h_c
        else:
            # section 5.4.2
            return 4.9 * self._gls[0].sff.eps + 16.3

    def get_h_i(
            self, surface_method: str = 'JIS_R3107', season: str = '', theta_s: float = None, theta_r_i: float = None):
        """
        Args:
            surface_method: method of the thermal conductance on the surface
                The methods are 'JIS_R3107' or 'JIS_A2103'
            season: the season of the calculation period
            theta_s: internal surface temperature, K
            theta_r_i: internal radiative temperature, K
        Returns:
            heat transfer coefficient on the inside surface, W/m2 K
        Notes:
            This value is supposed to apply for the vertical glasses.
        """

        if surface_method == 'JIS_A2103':
            t_s = theta_s + ABSOLUTE_ZERO
            t_r_i = theta_r_i + ABSOLUTE_ZERO
            h_r = self._gls[0].sff.eps * get_sigma() * (t_s ** 3 + t_s ** 2 * t_r_i + t_s * t_r_i ** 2 + t_r_i ** 3)
            h_c = {
                'summer': 2.5,
                'winter': 3.6
            }[season]
            return h_r + h_c
        else:
            # section 5.4.2
            return 5.4 * self._gls[-1].sfb.eps + 4.1

    def get_heat_transmittance(self):
        """
        calculate the heat transmittance

        Returns:
            heat transmittance, W/m2K

        Notes:
            equation (3)
        """

        return 1 / np.sum(self.r)

    @property
    def u(self):
        return self.get_heat_transmittance()

    def get_r_qin(self, ia: np.ndarray, reg: np.ndarray):

        # number of glasses
        n = self._n_gl

        n_in = np.array([
            (np.sum(reg[0: 2 * j + 1]) + reg[2 * j + 1] / 2.0) / np.sum(reg)
            for j in range(n)
        ])

        r_qin = np.sum(ia * n_in)

        return r_qin

    def get_temp_and_r(
            self, theta_e: float = 0.0, theta_i: float = 20.0,
            surface_method: str = 'JIS_R3107',
            season: str = 'winter',
            decision_air_layer_temp='fixed',
            ia: np.ndarray = None
    ) -> (np.ndarray, np.ndarray):
        """
            get the heat resistance
            This method is override at the upper class.
        Args:
            theta_e: external temperature, degree C
            theta_i: internal temperature, degree C
            surface_method: method of the thermal conductance on the surface
                The methods are 'JIS_R3107' or 'JIS_A2103'
            season: the season of the calculation period
            decision_air_layer_temp: method for decision of the air layer
            ia: absorbed solar radiation, W/m2
        Returns:
            heat resistance, m2K/W

        Notes:
            The number of the temperatures of the surface of the glasses is,
                2 for single glass,
                4 for double glasses and
                6 for triple glasses.
        """

        # number of glasses
        n = self._n_gl

        # solar radiation, W/m2
        ia2 = np.zeros(n)
        if ia is None:
            pass
        else:
            ia2 = ia

        # absorbed solar radiation on the surface, W/m2
        q_b = ia2.repeat(2) / 2.0

        def get_r(theta: np.ndarray) -> np.ndarray:
            """
                get the heat resistance
                This method is override at the upper class.
            Args:
                theta: temperature, degree C, [number of the temperatures of the surface of the glasses]
            Returns:
                heat resistance, m2K/W

            Notes:
                The number of the temperatures of the surface of the glasses is,
                    2 for single glass,
                    4 for double glasses and
                    6 for triple glasses.
            """

            # the thermal resistance, m2K/W
            r = np.zeros(2 * n + 1)

            if decision_air_layer_temp == 'fixed':

                # section 5.4.1
                # average of the absolute temperatures at each glass surface of the air layer, K
                t_m = 283.0

                # temperature difference of the surfaces of the air layer, K
                delta_t = 15.0

                # average temperature of the air of the air layer, K
                t_dash_m = 283.0

                #   on the exterior surface
                r[0] = 1 / self.get_h_e()

                #   of the glass
                for i in range(self._n_gl):
                    r[2 * i + 1] = self._gls[i].r

                #   of the air layer between the glasses
                for i in range(self._n_gl - 1):
                    r[2 * (i + 1)] = 1 / self._als[i].get_h_s(
                        t_m=t_m,
                        delta_t=delta_t,
                        t_dash_m=t_dash_m,
                        eps_f=self._gls[i].sfb.eps,
                        eps_b=self._gls[i+1].sff.eps
                    )

                #   on the interior surface
                r[2 * self._n_gl] = 1 / self.get_h_i()

            else:

                # thermal resistance on the exterior surface
                r[0] = 1 / self.get_h_e(
                    surface_method=surface_method, season=season, theta_s=theta[0], theta_r_e=theta_e)

                # thermal resistance of the glass
                for i in range(self._n_gl):
                    r[2 * i + 1] = self._gls[i].r

                # thermal resistance of the air layer between the glasses
                for i in range(self._n_gl - 1):
                    r[2 * (i + 1)] = 1 / self._als[i].get_h_s_with_surfaces_temp(
                        theta_f=theta[2 * i + 1],
                        theta_b=theta[2 * (i + 1)],
                        eps_f=self._gls[i].sfb.eps,
                        eps_b=self._gls[i + 1].sff.eps
                    )

                #   on the interior surface
                r[2 * self._n_gl] = 1 / self.get_h_i(
                    surface_method=surface_method, season=season, theta_s=theta[2 * n - 1], theta_r_i=theta_i)

            return r

        def get_heat_flow(theta: np.ndarray):

            r = get_r(theta=theta)

            # 行列式の生成
            ca = np.zeros((2 * n, 2 * n))

            for i in range(2 * n):
                ca[i][i] = 1 / r[i] + 1 / r[i + 1]
            for i in range(2 * n - 1):
                ca[i + 1][i] = - 1 / r[i + 1]
                ca[i][i + 1] = - 1 / r[i + 1]

            cb = np.zeros((2 * n))

            for i in range(2 * n):

                if i == 0:
                    # cb[i] = q_b[i] + te / r[i]
                    cb[i] = q_b[i] + theta_e / r[i]
                elif i == 2 * n - 1:
                    # cb[i] = q_b[i] + ti / r[i + 1]
                    cb[i] = q_b[i] + theta_i / r[i + 1]
                else:
                    # cb[i] = q_b[i]
                    cb[i] = q_b[i]

            return cb - np.dot(ca, theta.reshape(-1, 1)).flatten()

        result = optimize.root(get_heat_flow, np.full(2 * n, (theta_e + theta_i) / 2))

        # surface temperature, degree C, [number of the surface]
        theta_g = result.x

        # thermal registance, m2K/W, [number of the surface + 1]
        reg = get_r(theta_g)

        # inside heat flow of the absorbed solar radiation, W/m2
        r_qin = self.get_r_qin(ia=ia2, reg=reg)

        return theta_g, reg, r_qin

    @property
    def r(self) -> np.ndarray:
        """get the thermal resistances

        Get the thermal resistances of
            the surface of inside and outside,
            glasses and
            air layer between the surfaces of the glasses.
        The list of the resistances are stored in order from indoor to outdoor.

        Returns:
            thermal resistances, m2K/W, [number of the layers]
        Notes:
            The number of the layers are...
                3 for single glass,
                5 for double glasses and
                7 for triple glasses.
        """

        _, r, _ = self.get_temp_and_r()

        return r

