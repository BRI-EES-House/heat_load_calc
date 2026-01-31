from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime


from heat_load_calc.tenum import EInterval, EWeatherMethod, ERegion


@dataclass
class InputSeason(ABC):
    
    @property
    @abstractmethod
    def is_defined(self) -> bool: ...

@dataclass
class InputSeasonDefined(InputSeason):

    is_summer_period_set: bool

    is_winter_period_set: bool

    summer_start: str | None

    summer_end: str | None

    winter_start: str | None

    winter_end: str | None

    is_defined: bool = True

    @classmethod
    def read(cls, d_season: dict):

        # Tag 'is_summer_period_set' shoud be defined in season item.
        if 'is_summer_period_set' not in d_season:
            raise KeyError('Key is_summer_period_set could not be found in season tag.')

        # Tag 'is_winter_period_set' shoud be defined in season item.
        if 'is_winter_period_set' not in d_season:
            raise KeyError('Key is_winter_period_set could not be found in season tag.')
        
        is_summer_period_set = d_season['is_summer_period_set']
        is_winter_period_set = d_season['is_winter_period_set']

        # Value of 'is_summer_period_set' shoud be bool.
        if not isinstance(is_summer_period_set, bool):
            raise ValueError('Value of tag is_summer_period_set should be bool.')

        # Value of 'is_Winter_period_set' shoud be bool.
        if not isinstance(is_winter_period_set, bool):
            raise ValueError('Value of tag is_winter_period_set should be bool.')

        def check_datetime_str(v: str, arg_name: str):

            # check the format
            # If the case of wrong format or not exist day(i.e. 4/31), ValueError.
            # If the case of wrong type of the value(i.e. not literal), TypeError.

            try:
                datetime.strptime(v, '%m/%d')
            except ValueError:
                raise ValueError(f'Value of {arg_name} is wrong format or not exist day.')
            except TypeError:
                raise TypeError(f'Value of {arg_name} is not str.')

        if is_summer_period_set:

            if 'summer_start' not in d_season:
                raise KeyError('Key summer_start should be specified in season tag.')
            
            if 'summer_end' not in d_season:
                raise KeyError('Key summer_end should be specified in season tag.')
            
            summer_start = d_season['summer_start']
            summer_end = d_season['summer_end']

            check_datetime_str(summer_start, 'summer_start')
            check_datetime_str(summer_end, 'summer_end')
        
        else:

            summer_start = None
            summer_end = None
        
        if is_winter_period_set:

            if 'winter_start' not in d_season:
                raise KeyError('Key winter_start should be specified in season tag.')
            
            if 'winter_end' not in d_season:
                raise KeyError('Key winter_end should be specified in season tag.')
            
            winter_start = d_season['winter_start']
            winter_end = d_season['winter_end']

            check_datetime_str(winter_start, 'winter_start')
            check_datetime_str(winter_end, 'winter_end')
        
        else:

            winter_start = None
            winter_end = None

        return InputSeasonDefined(
            is_summer_period_set=is_summer_period_set,
            is_winter_period_set=is_winter_period_set,
            summer_start=summer_start,
            summer_end=summer_end,
            winter_start=winter_start,
            winter_end=winter_end
        )

@dataclass
class InputSeasonNotDefined(InputSeason):

    is_defined: bool = False

@dataclass
class InputWeather(ABC):

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
                
                # Tag 'region' should be number which is 1, 2, 3, 4, 5, 6, 7, or 8 with representing the region.
                region = ERegion(int(d_weather['region']))
                
                return InputWeatherEES(method=method, region=region)
                            
            case EWeatherMethod.FILE:

                # Tag 'file_path' should be defined.
                if 'file_path' not in d_weather:
                    raise KeyError('Key file_path should be specified if the file method applied.')

                file_path = str(d_weather['file_path'])

                # Tag 'latitude' should be defined.
                if 'latitude' not in d_weather:
                    raise KeyError('Key latitude should be specified if the file method applied.')
                
                # Latitude should be float from -90.0 to 90.0 (deg.).
                latitude = float(d_weather['latitude'])

                if (latitude < -90.0) or (latitude > 90.0):
                    raise ValueError('Latitude should be defined between -90.0 deg. and 90.0 deg.')
                
                # Tag 'longitude' should be defined.
                if 'longitude' not in d_weather:
                    raise KeyError('Key longitude should be specified if the file method applied.')

                # Longitude should be float from -180.0 to 180.0 (deg.).                
                longitude = float(d_weather['longitude'])

                if (longitude < -180.0) or (longitude > 180.0):
                    raise ValueError('Longitude should be defined between -180.0 deg. and 180.0 deg.')
                
                return InputWeatherFile(method=method, file_path=file_path, latitude=latitude, longitude=longitude)
            
            case _:

                raise ValueError('Invalid value is specified for the method.')

@dataclass
class InputWeatherEES(InputWeather):

    region: ERegion

@dataclass
class InputWeatherFile(InputWeather):

    file_path: str
    latitude: float
    longitude: float

@dataclass
class InputCommon:

    itv: EInterval

    ipt_weather: InputWeather

    ipt_season: InputSeason

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

        return InputCommon(
            itv = itv,
            ipt_weather=ipt_weather,
            ipt_season=ipt_season
        )


class InputAll:

    def __init__(self, d: dict):

        if 'common' not in d:
            raise KeyError('Key common could not be found in the input file.')
        
        d_common = d['common']

        self.d_common = d_common

        self.ipt_common: InputCommon = InputCommon.read(d_common=d_common)


