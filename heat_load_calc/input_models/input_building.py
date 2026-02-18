from dataclasses import dataclass

from heat_load_calc.input_models.input_infiltration import InputInfiltration


@dataclass
class InputBuilding:

    d_infiltration: dict

    ipt_infiltration: InputInfiltration

    @classmethod
    def read(self, d_building: dict):

        if 'infiltration' not in d_building:

            raise KeyError('Key \'infiltration\' is not defined in tag \'building\'.')
        
        d_infiltration = d_building['infiltration']

        ipt_infiltration = InputInfiltration.read(d_infiltration=d_infiltration)

        return InputBuilding(d_infiltration=d_infiltration, ipt_infiltration=ipt_infiltration)

