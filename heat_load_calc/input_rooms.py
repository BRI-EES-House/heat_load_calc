from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime


from heat_load_calc.tenum import EInterval, EWeatherMethod, ERegion, ENumberOfOccupants


@dataclass
class InputRoom:

    floor_area: float

    d_schedule: dict

    @classmethod
    def read(cls, d_room: dict):

        if 'id' not in d_room:
            raise KeyError('Key id could not be found in room tag.')

        if 'floor_area' not in d_room:
            raise KeyError('Key floor_area could not be found in room tag.')

        floor_area = float(d_room['floor_area'])

        if floor_area <= 0.0:
            raise ValueError('floor area should be greater than 0.0.')

        d_schedule = d_room['schedule']

        return InputRoom(
            floor_area=floor_area,
            d_schedule=d_schedule
        )
