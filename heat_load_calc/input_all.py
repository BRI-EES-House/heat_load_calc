from heat_load_calc.input_models.input_common import InputCommon
from heat_load_calc.input_rooms import InputRoom
from heat_load_calc.input_models.input_building import InputBuilding

class InputAll:

    def __init__(self, d: dict):

        if 'common' not in d:
            raise KeyError('Key \'common\' is not defined.')
        
        d_common = d['common']

        if 'building' not in d:
            raise KeyError('Key \'building\' is not defined.')
        
        d_building = d['building']

        if 'rooms' not in d:
            raise KeyError('Key \'rooms\' is not defined.')

        d_rooms = d['rooms']

        if not isinstance(d_rooms, list):
            raise TypeError("Value \'rooms\' should be list.")
        

        self.d_common = d_common

        self.d_rooms = d_rooms

        self.ipt_common: InputCommon = InputCommon.read(d_common=d_common)

        self.ipt_building: InputBuilding = InputBuilding.read(d_building=d_building)

        self.ipt_rooms: list[InputRoom] = [InputRoom.read(d_room=d_room) for d_room in d_rooms]
