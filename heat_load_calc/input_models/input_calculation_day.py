from dataclasses import dataclass


@dataclass
class InputCalculationDay:

    n_d_main: int

    n_d_run_up: int | None

    n_d_run_up_build: int | None

    @classmethod
    def read(cls, d_calculation_day: dict):

        if 'main' not in d_calculation_day:
            raise KeyError('Key \'main\' is not exists in tag \'calculation_day\'')

        try:

            n_d_main = int(d_calculation_day['main'])

        except ValueError:
            raise ValueError('An invalid value was specified in \'calculation_day\' tag.')

        try:

            n_d_run_up = int(d_calculation_day['run_up']) if 'run_up' in d_calculation_day else None
            n_d_run_up_build = int(d_calculation_day['run_up_building']) if 'run_up_building' in d_calculation_day else None
            
        except ValueError:
            raise ValueError('An invalid value was specified in \'calculation_day\' tag.')
            
        if not 365 >= n_d_main > 0:
            raise ValueError('Value \'main\' in tag \'calculation_day\' is out of range.')

        if n_d_run_up is not None:
            if not 365 >= n_d_run_up >= 0:
                raise ValueError('Value \'main\' in tag \'calculation_day\' is out of range.')

        if n_d_run_up_build is not None:
            if not 365 >= n_d_run_up_build >= 0:
                raise ValueError('Value \'main\' in tag \'calculation_day\' is out of range.')
        
        return InputCalculationDay(n_d_main=n_d_main, n_d_run_up=n_d_run_up, n_d_run_up_build=n_d_run_up_build)

