from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime


from heat_load_calc.tenum import EInterval, EWeatherMethod, ERegion, ENumberOfOccupants


@dataclass
class InputSchedule:

    d_schedule: dict

    is_schedule_type_defined: bool

    @classmethod
    def read(cls, d_schedule: dict):

        if 'schedule_type' in d_schedule:

            

            return InputScheduleDirect(d_schedule=d_schedule)
        
        else:

            return InputScheduleFile(d_schedule=d_schedule)


@dataclass
class InputScheduleDirect(InputSchedule):

    is_schedule_type_defined: bool = True


@dataclass
class InputScheduleFile(InputSchedule):

    is_schedule_type_defined: bool = False


@dataclass
class InputRoom:

    # id (>=0)
    id: int

    # name
    name: str

    # floor area, m2 (>0.0)
    a_f: float

    d_schedule: dict

    ipt_schedule: InputSchedule

    @classmethod
    def read(cls, d_room: dict):

        # id

        if 'id' not in d_room:
            raise KeyError('Key \'id\' could not be found in \'room\' tag.')
        
        try:
            id = int(d_room['id'])
        except ValueError:
            raise ValueError('An invalid value was specified for \'id\'. \'id\' must be an integer.')
        
        if id < 0:
            raise ValueError('\'id\' should be greater than or equal to 0.')

        # name
       
        if 'name' not in d_room:
            raise KeyError(f'Key \'name\' could not be found in \'room\' tag. (ID={id})')
        
        name = d_room['name']

        # floor area

        if 'floor_area' not in d_room:
            raise KeyError(f'Key \'floor_area\' could not be found in \'room\' tag. (ID={id})')
        
        try:
            a_f = float(d_room['floor_area'])
        except:
            raise ValueError(f'An invalid value was specified for \'floor_area\'. \'floor_area\' must be an float. (ID={id})')

        if a_f <= 0.0:
            raise ValueError(f'\'floor_area\' should be greater than 0.0. (ID={id})')

        # schedule

        if 'schedule' not in d_room:
            raise KeyError(f'Key \'schedule\' could not be found in \'room\' tag. (ID={id})')

        d_schedule = d_room['schedule']

        ipt_schedule = InputSchedule.read(d_schedule=d_schedule)

        return InputRoom(
            id=id,
            name=name,
            a_f=a_f,
            d_schedule=d_schedule,
            ipt_schedule=ipt_schedule
        )
