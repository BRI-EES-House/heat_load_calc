from dataclasses import dataclass


from heat_load_calc.tenum import EInterval, ENumberOfOccupants
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


        return InputCommon(
            itv = itv,
            ipt_weather=ipt_weather,
            ipt_season=ipt_season,
            n_ocp=n_ocp,
            ipt_calculation_day=ipt_calculation_day
        )
    
    @staticmethod
    def _get_n_d(d_common: dict):

        if 'calculation_day' in d_common:
            
            d_calculation_day = d_common['calculation_day']

            n_d_main = int(d_calculation_day['main']) if 'main' in d_calculation_day else None
            n_d_run_up = int(d_calculation_day['run_up']) if 'run_up' in d_calculation_day else None
            n_d_run_up_build = int(d_calculation_day['run_up_building']) if 'run_up_building' in d_calculation_day else None
        
        else:

            n_d_main = None
            n_d_run_up = None
            n_d_run_up_build = None

        return n_d_main, n_d_run_up, n_d_run_up_build


