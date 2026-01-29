from heat_load_calc.tenum import EInterval, EWeatherMethod
from dataclasses import dataclass

class InputAll:

    def __init__(self, d: dict):

        if 'common' not in d:
            raise KeyError('Key common could not be found in the input file.')
        
        d_common = d['common']

        self.d_common = d_common

        self.ipt_common: InputCommon = InputCommon.read(d_common=d_common)


@dataclass
class InputCommon:

    itv: EInterval

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

        return InputCommon(
            itv = itv
        )


@dataclass
class InputWeather:

    method: EWeatherMethod

    @classmethod
    def read(cls, d_weather: dict):

        # Tag 'method' should be defined.
        if 'method' not in d_weather:
            raise KeyError('Key method could not be found in weather tag.')
        
        method =  EWeatherMethod(d_weather['method'])

        # 'method' takes the value of either 'ees' or 'file'.
        match method:

            case EWeatherMethod.EES:

                # Tag 'region' should be defined.
                if 'region' not in d_weather:
                   raise KeyError('Key region should be specified if the ees method applied.')
                
                return InputWeatherEES(method=method, region=int(d_weather['region']))
                
                ...
            
            case EWeatherMethod.FILE:

                ...
            
            case _:

                raise ValueError('Invalid value is specified for the method.')

@dataclass
class InputWeatherEES(InputWeather):

    region: int