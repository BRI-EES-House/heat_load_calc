from dataclasses import dataclass


from heat_load_calc.tenum import EInterval, ENumberOfOccupants, EShapeFactorMethod
from heat_load_calc.input_models.input_season import InputSeason, InputSeasonDefined, InputSeasonNotDefined
from heat_load_calc.input_models.input_weather import InputWeather, InputWeatherEES, InputWeatherFile
from heat_load_calc.input_models.input_calculation_day import InputCalculationDay


@dataclass
class InputCommon:

    itv: EInterval

    ipt_weather: InputWeather

    ipt_season: InputSeason

    n_ocp: ENumberOfOccupants

    ipt_calculation_day: InputCalculationDay

    shape_factor_method: EShapeFactorMethod

    @classmethod
    def read(self, d_common: dict):

        # If 'interval' tag is not exist, '15m' is set as the default value.
        # 'interval' takes the value of either '15m', '30m', or '1h'.
        itv = EInterval(d_common.get('interval', '15m'))

        # Tag 'weather' should be defined.
        if 'weather' not in d_common:
            raise KeyError('Key weather could not be found in common tag.')
        
        d_weather = d_common['weather']

        ipt_weather = InputWeather.read(d_weather=d_weather)

        # Tag 'season' is optional.
        if 'season' in d_common:

            d_season = d_common['season']

            ipt_season = InputSeasonDefined.read(d_season=d_season)
        
        else:

            ipt_season = InputSeasonNotDefined()
        
        _n_ocp = d_common['number_of_occupants'] if 'number_of_occupants' in d_common else 'auto'

        n_ocp = ENumberOfOccupants(_n_ocp)

        if 'calculation_day' in d_common:
            
            ipt_calculation_day = InputCalculationDay.read(d_calculation_day=d_common['calculation_day'])

        else:

            ipt_calculation_day = None

        # If key 'mutual_radiation_method' is not exist, 'Nagata' is set as the default value.
        shape_factor_method = EShapeFactorMethod(d_common.get('mutual_radiation_method', 'Nagata'))

        return InputCommon(
            itv = itv,
            ipt_weather=ipt_weather,
            ipt_season=ipt_season,
            n_ocp=n_ocp,
            ipt_calculation_day=ipt_calculation_day,
            shape_factor_method=shape_factor_method
        )
    

