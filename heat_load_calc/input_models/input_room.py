from dataclasses import dataclass
from abc import ABC, abstractmethod
import os


from heat_load_calc.error_message import (
    key_not_exists as KNE,
    value_invalid as VI,
    value_out_of_range_GE as RGE,
    value_out_of_range_LE as RLE,
    value_out_of_range_GT as RGT,
    value_out_of_range_LT as RLT
)
from heat_load_calc.input_models.input_schedule_data import InputScheduleData, InputScheduleDataConst, InputScheduleDataNumber
from heat_load_calc.input_models.input_furniture import InputFurniture

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

    ipt_furniture: InputFurniture

    # amont of natural ventilation with opening window, m3/h (>=0.0)
    v_vent_ntr_set: float

    # MET
    met: float

    ipt_schedule_data: InputScheduleData

    @classmethod
    def read(cls, d_room: dict):

        # id

        if 'id' not in d_room:
            raise KeyError(KNE('id', 'room'))
        
        try:
            id = int(d_room['id'])
        except ValueError:
            raise ValueError(VI('id', 'room'))
        
        if id < 0:
            raise ValueError(RGE('id', 'room', '0.0'))

        # name
       
        if 'name' not in d_room:
            raise KeyError(KNE('name', 'room'))
        
        name = str(d_room['name'])

        # sub name

        sub_name = str(d_room.get('sub_name', ''))

        # floor area, m2

        if 'floor_area' not in d_room:
            raise KeyError(KNE('floor_area', 'room'))
        
        try:
            a_f = float(d_room['floor_area'])
        except:
            raise ValueError(VI('floor_area', 'room'))

        if a_f <= 0.0:
            raise ValueError(RGT('floor_area', 'room', '0.0'))
        
        # volume, m3

        if 'volume' not in d_room:
            raise KeyError(KNE('floor_area', 'room'))
        
        try:
            v = float(d_room['volume'])
        except ValueError:
            raise ValueError(VI('floor_area', 'room'))
        
        if v <= 0.0:
            raise ValueError(RGT('floor_area', 'room', '0.0'))
        
        if 'furniture' not in d_room:
            raise KeyError(KNE('furniture', 'room'))
        
        d_furniture = d_room['furniture']

        ipt_furniture = InputFurniture.read(d_furniture=d_furniture)

        # natural ventilation, m3/h

        if 'ventilation' not in d_room:
            raise KeyError(KNE('ventilation', 'room'))
        
        if 'natural' not in d_room['ventilation']:
            raise KeyError(KNE('natural', 'ventilation'))
        
        try:
            v_vent_ntr_set = float(d_room['ventilation']['natural'])
        except ValueError:
            raise ValueError(VI('natural', 'ventilation'))

        if v_vent_ntr_set < 0.0:
            raise ValueError(RGE('natural', 'ventilation', '0.0'))
        
        # MET

        try:
            met = float(d_room.get('MET', 1.0))
        except ValueError:
            raise ValueError(VI('MET', 'room'))
        
        if met <= 0.0:
            raise ValueError(RGT('MET', 'room', '0.0'))
            
        # schedule

        if 'schedule' not in d_room:
            raise KeyError(KNE('schedule', 'room'))

        d_schedule = d_room['schedule']

        ipt_schedule_data = InputScheduleData.read(id=id, d_schedule=d_schedule)

        return InputRoom(
            id=id,
            name=name,
            sub_name=sub_name,
            a_f=a_f,
            v=v,
            ipt_furniture=ipt_furniture,
            v_vent_ntr_set=v_vent_ntr_set,
            met=met,
            ipt_schedule_data=ipt_schedule_data
        )
