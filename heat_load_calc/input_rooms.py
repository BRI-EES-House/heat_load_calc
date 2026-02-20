from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime


from heat_load_calc.tenum import EInterval, EWeatherMethod, ERegion, ENumberOfOccupants, EScheduleType, EDayType
from heat_load_calc.input_models.input_schedule_elements import InputScheduleElements


@dataclass
class InputScheduleDataDayTypes:

    d_weekday: dict
    d_holiday_out: dict
    d_holiday_in: dict
    input_schedule_elements_weekday: InputScheduleElements
    input_schedule_elements_holiday_out: InputScheduleElements
    input_schedule_elements_holiday_in: InputScheduleElements

    def day_type(self, day_type: EDayType) -> InputScheduleElements:

        return{
            EDayType.Weekday: self.input_schedule_elements_weekday,
            EDayType.HolidayOut: self.input_schedule_elements_holiday_out,
            EDayType.HolidayIn: self.input_schedule_elements_holiday_in
        }[day_type]

    @classmethod
    def read(cls, id: int, d: dict):

        try:

            d_weekday = d[EDayType.Weekday.value]
            d_holiday_out = d[EDayType.HolidayOut.value]
            d_holiday_in = d[EDayType.HolidayIn.value]

        except KeyError as e:
            raise KeyError(f'Key {e} could not be found in \'const\' tag. (ID={id})')

        input_schedule_elements_weekday = InputScheduleElements.read(id=id, d=d_weekday)
        input_schedule_elements_holiday_out = InputScheduleElements.read(id=id, d=d_holiday_out)
        input_schedule_elements_holiday_in = InputScheduleElements.read(id=id, d=d_holiday_in)
        

        return InputScheduleDataDayTypes(
            d_weekday=d_weekday,
            d_holiday_out=d_holiday_out,
            d_holiday_in=d_holiday_in,
            input_schedule_elements_weekday=input_schedule_elements_weekday,
            input_schedule_elements_holiday_out=input_schedule_elements_holiday_out,
            input_schedule_elements_holiday_in=input_schedule_elements_holiday_in
        )


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
                
                ipt_schedule_data_day_const = InputScheduleDataDayTypes.read(id=id, d=d_const)
                
                return InputScheduleDataConst(ipt_schedule_data_day_types_const=ipt_schedule_data_day_const)

            case EScheduleType.NUMBER:

                try:

                    d_one = d_schedule_data['1']
                    d_two = d_schedule_data['2']
                    d_three = d_schedule_data['3']
                    d_four = d_schedule_data['4']

                except KeyError as e:

                    raise KeyError(f'Key {e} could not be found in \'schedule\' tag. (ID={id})')
                
                ipt_schedule_data_day_types_one = InputScheduleDataDayTypes.read(id=id, d=d_one)
                ipt_schedule_data_day_types_two = InputScheduleDataDayTypes.read(id=id, d=d_two)
                ipt_schedule_data_day_types_three = InputScheduleDataDayTypes.read(id=id, d=d_three)
                ipt_schedule_data_day_types_four = InputScheduleDataDayTypes.read(id=id, d=d_four)

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

    ipt_schedule_data_day_types_const: InputScheduleDataDayTypes

    schedule_type: EScheduleType = EScheduleType.CONST


@dataclass
class InputScheduleDataNumber(InputScheduleData):

    ipt_schedule_data_day_types_one: InputScheduleDataDayTypes
    ipt_schedule_data_day_types_two: InputScheduleDataDayTypes
    ipt_schedule_data_day_types_three: InputScheduleDataDayTypes
    ipt_schedule_data_day_types_four: InputScheduleDataDayTypes

    schedule_type: EScheduleType = EScheduleType.NUMBER

    def num(self, noo: ENumberOfOccupants) -> InputScheduleDataDayTypes:

        return{
            ENumberOfOccupants.One: self.ipt_schedule_data_day_types_one,
            ENumberOfOccupants.Two: self.ipt_schedule_data_day_types_two,
            ENumberOfOccupants.Three: self.ipt_schedule_data_day_types_three,
            ENumberOfOccupants.Four: self.ipt_schedule_data_day_types_four
        }[noo]
    

@dataclass
class InputSchedule(ABC):

    d_schedule: dict

    # room id (this is used only for display error message.)
    id: int

    @property
    @abstractmethod
    def is_schedule_type_defined(self) -> bool: ...

    @classmethod
    def read(cls, id: int, d_schedule: dict):

        if 'schedule_type' in d_schedule:

            try:
                schedule_type = EScheduleType(d_schedule['schedule_type'])
            except ValueError:
                raise ValueError(f'An invalid value was specified for \'schedule_type\' in \'schedule\' tag. (ID={id})')          
            
            if 'schedule' not in d_schedule:

                raise KeyError(f'Key \'schedule\' could not be found in \'schedule\' tag. (ID={id})')
            
            d_schedule_data = d_schedule['schedule']

            ipt_schedule_data = InputScheduleData.read(id=id, d_schedule_data=d_schedule_data, schedule_type=schedule_type)

            return InputScheduleDirect(id=id, d_schedule=d_schedule, schedule_type=schedule_type, ipt_schedule_data=ipt_schedule_data)
        
        else:

            if 'name' not in d_schedule:

                raise KeyError(f'Key \'name\' could not be found in \'schedule\' tag. (ID={id})')

            name = d_schedule['name']

            return InputScheduleFile(id=id, d_schedule=d_schedule, name=name)


@dataclass
class InputScheduleDirect(InputSchedule):

    schedule_type: EScheduleType

    ipt_schedule_data: InputScheduleData
    
    is_schedule_type_defined: bool = True


@dataclass
class InputScheduleFile(InputSchedule):

    name: str

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

        ipt_schedule = InputSchedule.read(id=id, d_schedule=d_schedule)

        return InputRoom(
            id=id,
            name=name,
            a_f=a_f,
            d_schedule=d_schedule,
            ipt_schedule=ipt_schedule
        )
