from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime


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
