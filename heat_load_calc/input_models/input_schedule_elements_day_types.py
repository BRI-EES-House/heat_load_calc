from dataclasses import dataclass


from heat_load_calc.tenum import EDayType
from heat_load_calc.input_models.input_schedule_element import InputScheduleElement


@dataclass
class InputScheduleElementsDayTypes:

    input_schedule_elements_weekday: InputScheduleElement
    input_schedule_elements_holiday_out: InputScheduleElement
    input_schedule_elements_holiday_in: InputScheduleElement

    def day_type(self, day_type: EDayType) -> InputScheduleElement:

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

        input_schedule_elements_weekday = InputScheduleElement.read(id=id, d=d_weekday)
        input_schedule_elements_holiday_out = InputScheduleElement.read(id=id, d=d_holiday_out)
        input_schedule_elements_holiday_in = InputScheduleElement.read(id=id, d=d_holiday_in)
        

        return InputScheduleElementsDayTypes(
            input_schedule_elements_weekday=input_schedule_elements_weekday,
            input_schedule_elements_holiday_out=input_schedule_elements_holiday_out,
            input_schedule_elements_holiday_in=input_schedule_elements_holiday_in
        )

