from dataclasses import dataclass
from abc import ABC, abstractmethod


from heat_load_calc.tenum import ENumberOfOccupants, EScheduleType
from heat_load_calc.input_models.input_schedule_elements_day_types import InputScheduleElementsDayTypes


@dataclass
class InputScheduleData(ABC):
    
    @property
    @abstractmethod
    def schedule_type(self) -> EScheduleType: ...

    @classmethod
    def read(cls, id: int, d_schedule_data: dict, schedule_type: EScheduleType):

        match schedule_type:

            case EScheduleType.CONST:
                
                try:

                    d_const = d_schedule_data['const']
                
                except KeyError as e:
                
                    raise KeyError(f'Key {e} could not be found in \'schedule\' tag. (ID={id})')
                
                ipt_schedule_data_day_const = InputScheduleElementsDayTypes.read(id=id, d=d_const)
                
                return InputScheduleDataConst(ipt_schedule_data_day_types_const=ipt_schedule_data_day_const)

            case EScheduleType.NUMBER:

                try:

                    d_one = d_schedule_data['1']
                    d_two = d_schedule_data['2']
                    d_three = d_schedule_data['3']
                    d_four = d_schedule_data['4']

                except KeyError as e:

                    raise KeyError(f'Key {e} could not be found in \'schedule\' tag. (ID={id})')
                
                ipt_schedule_data_day_types_one = InputScheduleElementsDayTypes.read(id=id, d=d_one)
                ipt_schedule_data_day_types_two = InputScheduleElementsDayTypes.read(id=id, d=d_two)
                ipt_schedule_data_day_types_three = InputScheduleElementsDayTypes.read(id=id, d=d_three)
                ipt_schedule_data_day_types_four = InputScheduleElementsDayTypes.read(id=id, d=d_four)

                return InputScheduleDataNumber(
                    ipt_schedule_data_day_types_one=ipt_schedule_data_day_types_one,
                    ipt_schedule_data_day_types_two=ipt_schedule_data_day_types_two,
                    ipt_schedule_data_day_types_three=ipt_schedule_data_day_types_three,
                    ipt_schedule_data_day_types_four=ipt_schedule_data_day_types_four
                )
            
            case _:
                raise ValueError(f'An invalid schedule_type was specified in \'schedule\' tag. (ID={id})')


@dataclass
class InputScheduleDataConst(InputScheduleData):

    ipt_schedule_data_day_types_const: InputScheduleElementsDayTypes

    schedule_type: EScheduleType = EScheduleType.CONST


@dataclass
class InputScheduleDataNumber(InputScheduleData):

    ipt_schedule_data_day_types_one: InputScheduleElementsDayTypes
    ipt_schedule_data_day_types_two: InputScheduleElementsDayTypes
    ipt_schedule_data_day_types_three: InputScheduleElementsDayTypes
    ipt_schedule_data_day_types_four: InputScheduleElementsDayTypes

    schedule_type: EScheduleType = EScheduleType.NUMBER

    def num(self, noo: ENumberOfOccupants) -> InputScheduleElementsDayTypes:

        return{
            ENumberOfOccupants.One: self.ipt_schedule_data_day_types_one,
            ENumberOfOccupants.Two: self.ipt_schedule_data_day_types_two,
            ENumberOfOccupants.Three: self.ipt_schedule_data_day_types_three,
            ENumberOfOccupants.Four: self.ipt_schedule_data_day_types_four
        }[noo]
    
