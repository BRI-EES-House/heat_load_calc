
def key_not_exists(s1: str, s2: str):

    return f'Key \'{s1}\' could not be found in key \'{s2}\'.'

def value_invalid(s1: str, s2: str):

    return f'An invalid value was specified as key \'{s1}\' in key \'{s2}\'.'

def value_out_of_range_GT(s1: str, s2: str, v: str):

    return f'Value \'{s1}\' should be greater than {v} in key \'{s2}\'.'

def value_out_of_range_GE(s1: str, s2: str, v: str):

    return f'Value \'{s1}\' should be greater than or equal to {v} in key \'{s2}\'.'

def value_out_of_range_LT(s1: str, s2: str, v: str):

    return f'Value \'{s1}\' should be less than {v} in key \'{s2}\'.'

def value_out_of_range_LE(s1: str, s2: str, v: str):

    return f'Value \'{s1}\' should be less than or equal to {v} in key \'{s2}\'.'