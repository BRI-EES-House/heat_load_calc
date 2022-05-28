import os
import pandas as pd
import numpy as np
import csv


class ScheduleMaker:

    def __init__(self):
        pass

    @staticmethod
    def get_v_mec_vent_local_is_ns(s_folder: str, rd: dict):

        df_local_vent = get_df_local_vent(s_folder=s_folder)

        numpy_local_vent = get_numpy_local_vent(s_folder=s_folder)

        vent = []
        for rm in rd['rooms']:
            if 'local_ventilation' in rm['ventilation']:
                if rm['ventilation']['local_ventilation']['method'] == 'constant':
                    print('Set the constant value.')
                    vent.append(np.full(shape=(8760*4), fill_value=float(rm['ventilation']['local_ventilation']['constant_value'])))
                else:
                    print('Read pandas data from csv data.')
                    vent.append(df_local_vent[str(rm['id'])].values)
            else:
                print('Read csv data.')
                vent.append(numpy_local_vent[int(rm['id'])])

        return np.stack(vent)


def get_df_local_vent(s_folder: str):

    file_path_local_vent = os.path.join(s_folder, "local_vent.csv")

    if os.path.exists(file_path_local_vent):
        print('The file local_vent was exist.')
        return pd.read_csv(file_path_local_vent)
    else:
        print('The file local_vent was not exist.')
        return None


def get_numpy_local_vent(s_folder):

    file_path_local_vent_csv = os.path.join(s_folder, 'mid_data_local_vent.csv')

    if os.path.exists(file_path_local_vent_csv):
        print('The file mid_data_local_vent was exist.')
        with open(file_path_local_vent_csv, 'r') as f:
            r = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            return np.array([row for row in r]).T
    else:
        return None

