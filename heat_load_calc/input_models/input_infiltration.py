from dataclasses import dataclass

from heat_load_calc.tenum import EStory, EStructure, EInsidePressure, EInfiltrationMethod, ECValueEstimateMethod

@dataclass
class InputInfiltration:

    method: EInfiltrationMethod
    story: EStory
    c_value_estimate: ECValueEstimateMethod
    c_value: float | None
    ua_value: float | None
    struct: EStructure | None
    inside_pressure: EInsidePressure

    @classmethod
    def read(cls, d_infiltration: dict):

        if not 'method' in d_infiltration:

            raise KeyError('Key \'method\' should be defined in \'infiltration\' tag.')

        method = EInfiltrationMethod(d_infiltration['method'])

        match method:

            case EInfiltrationMethod.BALANCE_RESIDENTIAL:

                if not 'story' in d_infiltration:

                    raise KeyError('Key \'story\' should be defined in \'infiltration\' tag.')
                
                story = EStory(d_infiltration['story'])

                if not 'c_value_estimate' in d_infiltration:

                    raise KeyError('Key \'c_value_estimate\' should be defined in \'infiltration\' tag.')
                
                c_value_estimate = ECValueEstimateMethod(d_infiltration['c_value_estimate'])

                match c_value_estimate:

                    case ECValueEstimateMethod.SPECIFY:

                        if 'c_value' not in d_infiltration:
                            raise KeyError('Key \'c_value\' should be defined in \'infiltration\' tag.')

                        try:
                            c_value = float(d_infiltration['c_value'])
                        except ValueError:
                            raise ValueError('Invalid value was specified in key \'c_value\' in \'infiltration\' tag.')
                        
                        if c_value < 0.0:
                            raise ValueError('Value \'c_value\' should be more than or equal to zero.')
                        
                        ua_value = None

                        struct = None
                    
                    case ECValueEstimateMethod.CALCULATE:

                        c_value = None

                        if 'ua_value' not in d_infiltration:
                            raise KeyError('Key \'ua_value\' should be defined in \'infiltration\' tag.')

                        try:
                            ua_value = float(d_infiltration['ua_value'])
                        
                        except ValueError:
                            raise ValueError('Invalid value was specified in key \'ua_value\' in \'infiltration\' tag.')

                        if ua_value < 0.0:
                            raise ValueError('Invalid value was specified in key \'ua_value\' in \'infiltration\' tag.')
                        
                        if 'struct' not in d_infiltration:
                            raise KeyError('Key \'struct\' should be defined in \'infiltration\' tag.')

                        try:
                            struct = EStructure(d_infiltration['struct'])
                        
                        except ValueError:
                            raise ValueError('Invalid value was specified in key \'struct\' in \'infiltration\' tag.')

                    case _:
                        raise ValueError('An invalid value is specified in key \'c_value_estimate\' in tag \'infiltration\'.')

                if 'inside_pressure' not in d_infiltration:
                    raise KeyError('Key \'inside_pressure\' should be defined in \'infiltration\' tag.')

                inside_pressure = EInsidePressure(d_infiltration['inside_pressure'])

            case _:
                
                raise ValueError('An invalid value is specified for value \'method\' in \'infiltration\' tag.')
        
        return InputInfiltration(
            method=method,
            story=story,
            c_value_estimate=c_value_estimate,
            c_value=c_value,
            ua_value=ua_value,
            struct=struct,
            inside_pressure=inside_pressure
        )
