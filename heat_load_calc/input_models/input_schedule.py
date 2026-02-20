from dataclasses import dataclass
import os
import json

from heat_load_calc.input_models.input_schedule_data import InputScheduleData


@dataclass
class InputSchedule:

    # room id (this is used only for display error message.)
    id: int

    ipt_schedule_data: InputScheduleData
    
    @classmethod
    def read(cls, id: int, d_schedule: dict):

        if 'schedule_type' in d_schedule:

            ipt_schedule_data = InputScheduleData.read(id=id, d_schedule=d_schedule)

            return InputSchedule(id=id, ipt_schedule_data=ipt_schedule_data)

        else:

            if 'name' not in d_schedule:

                raise KeyError(f'Key \'name\' could not be found in \'schedule\' tag. (ID={id})')

            name = d_schedule['name']

            with open(str(os.path.dirname(os.path.dirname(__file__))) + '/schedule/' + name + '.json', 'r', encoding='utf-8') as f:
                d_schedule = json.load(f)

            ipt_schedule_data = InputScheduleData.read(id=id, d_schedule=d_schedule)

            return InputSchedule(id=id, ipt_schedule_data=ipt_schedule_data)

