from dataclasses import dataclass
from abc import ABC, abstractmethod


from heat_load_calc.tenum import EWeatherMethod, ERegion


@dataclass
class InputWeather(ABC):

    @property
    @abstractmethod
    def method(self) -> EWeatherMethod: ...

    @classmethod
    def read(cls, d_weather: dict):

        # Tag 'method' should be defined.
        if 'method' not in d_weather:
            raise KeyError('Key method could not be found in weather tag.')
        
        # 'method' takes the value of either 'ees' or 'file'.
        match EWeatherMethod(d_weather['method']):

            case EWeatherMethod.EES:

                # Tag 'region' should be defined.
                if 'region' not in d_weather:
                   raise KeyError('Key region should be specified if the ees method applied.')
                
                # Tag 'region' should be number which is 1, 2, 3, 4, 5, 6, 7, or 8 with representing the region.
                region = ERegion(int(d_weather['region']))
                
                return InputWeatherEES(region=region)
                            
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
                
                return InputWeatherFile(file_path=file_path, latitude=latitude, longitude=longitude)
            
            case _:

                raise ValueError('Invalid value is specified for the method.')

@dataclass
class InputWeatherEES(InputWeather):

    region: ERegion
    method: EWeatherMethod = EWeatherMethod.EES

@dataclass
class InputWeatherFile(InputWeather):

    file_path: str
    latitude: float
    longitude: float
    method: EWeatherMethod = EWeatherMethod.FILE
