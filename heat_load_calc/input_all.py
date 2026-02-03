from heat_load_calc.input_common import InputCommon

class InputAll:

    def __init__(self, d: dict):

        if 'common' not in d:
            raise KeyError('Key common could not be found in the input file.')
        
        d_common = d['common']

        if 'rooms' not in d:
            raise KeyError('Key rooms could not be found in the input file.')
        
        d_rooms = d['rooms']

        self.d_common = d_common

        self.d_rooms = d_rooms

        self.ipt_common: InputCommon = InputCommon.read(d_common=d_common)
