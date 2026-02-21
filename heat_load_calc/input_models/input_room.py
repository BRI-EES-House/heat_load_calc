from dataclasses import dataclass
from abc import ABC, abstractmethod
import os

from heat_load_calc.input_models.input_schedule_data import InputScheduleData, InputScheduleDataConst, InputScheduleDataNumber


@dataclass
class InputRoom:

    # id (>=0)
    id: int

    # name
    name: str

    # sub_name
    sub_name: str

    # floor area, m2 (>0.0)
    a_f: float

    # volume, m3 (>0.0)
    v: float

    ipt_schedule_data: InputScheduleData

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
        
        name = str(d_room['name'])

        # sub name

        sub_name = str(d_room.get('sub_name', ''))

        # floor area, m2

        if 'floor_area' not in d_room:
            raise KeyError(f'Key \'floor_area\' could not be found in \'room\' tag. (ID={id})')
        
        try:
            a_f = float(d_room['floor_area'])
        except:
            raise ValueError(f'An invalid value was specified for \'floor_area\'. \'floor_area\' must be an float. (ID={id})')

        if a_f <= 0.0:
            raise ValueError(f'\'floor_area\' should be greater than 0.0. (ID={id})')
        
        # volume, m3

        if 'volume' not in d_room:
            raise KeyError(f'Key \'volume\' could not be found in \'room\' key. (ID={id})')
        
        try:
            v = float(d_room['volume'])
        except ValueError:
            raise ValueError(f'An invalid value was specified for \'volume\' in \'room\' key. (ID={id})')
        
        if v <= 0.0:
            raise ValueError(f'\'volume\' should be greater than 0.0. (ID={id})')

        # schedule

        if 'schedule' not in d_room:
            raise KeyError(f'Key \'schedule\' could not be found in \'room\' tag. (ID={id})')

        d_schedule = d_room['schedule']

        ipt_schedule_data = InputScheduleData.read(id=id, d_schedule=d_schedule)

        return InputRoom(
            id=id,
            name=name,
            sub_name=sub_name,
            a_f=a_f,
            v=v,
            ipt_schedule_data=ipt_schedule_data
        )
