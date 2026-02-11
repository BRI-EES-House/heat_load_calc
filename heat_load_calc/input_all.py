from heat_load_calc.input_models.input_common import InputCommon
from heat_load_calc.input_rooms import InputRoom

class InputAll:

    def __init__(self, d: dict):

        if 'common' not in d:
            raise KeyError('Key common could not be found in the input file.')
        
        d_common = d['common']

        if 'rooms' not in d:
            raise KeyError('Key rooms could not be found in the input file.')

        d_rooms = d['rooms']

        if not isinstance(d_rooms, list):
            raise TypeError("Item rooms should be list in the input file.")
        

        self.d_common = d_common

        self.d_rooms = d_rooms

        self.ipt_common: InputCommon = InputCommon.read(d_common=d_common)

        self.ipt_rooms: list[InputRoom] = [InputRoom.read(d_room=d_room) for d_room in d_rooms]
