# load and clean-up datasets
import os
import pathlib

import pandas as pd
from numpy import nan
from numpy import isnan
from pandas import read_csv


# fill missing values with a value at the same time one day ago
def fill_missing(values):
    one_day = 60 * 24
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            if isnan(values[row, col]):
                values[row, col] = values[row - one_day, col]
    return values


def import_data_HPC(view: bool = True):

    # load all datasets
    dataset = pd.read_csv(
        'http://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip', 
        sep=';', 
        na_values=['nan', '?'],
        low_memory=False, 
        infer_datetime_format=True,  
        parse_dates={'datetime': ['Date', 'Time']},
        index_col=['datetime']	
    )
    # summarize
    if view:
        print(dataset.shape)
        print('\n')
        #dataset.head()
    values = dataset.values.astype('float32')
    dataset['sub_metering_4'] = (values[:, 0] * 1000 / 60) - (values[:, 4] + values[:, 5] + values[:, 6])

    return dataset


def import_data_pump_sensor(view: bool = True):
    dataset = pd.read_csv(
        './datasets/sensor_final.csv',
        index_col="timestamp",
        parse_dates=["timestamp"]
    )
    if view:
        print(dataset.shape)
        print('\n')
    return dataset


def _get_dataframe_raw(date_init, date_end):
    script_path = os.path.dirname(os.path.abspath(__file__))
    data = pd.read_csv(
        pathlib.Path(script_path).joinpath('./BBDD', 'HPC_raw_noNaN.csv'),
        header=0,
        parse_dates=['datetime'],
        index_col=['datetime'],
        # infer_datetime_format=False
    )
    if date_init is None and date_end is None:
        return data
    if date_init is None and date_end is not None:
        return data.loc[:date_end]
    if date_init is not None and date_end is None:
        return data.loc[date_init:]
    else:
        return data.loc[date_init, date_end]


def hpc_dataframe(
        ts: str = '10min',
        mean: bool = True,
        date_init: str = None,
        date_end: str = None
):
    data = _resample(
        data=_get_dataframe_raw(date_init, date_end),
        op=ts,
        mean=mean
    )
    return data


def _resample(
        data: pd.DataFrame = None,
        op: str = None,
        mean: bool = None,
):
    if data is None:
        print('Insert DataFrame')
        return None
    else:
        if bool:
            df_resample = data.resample(op).mean()
            print(df_resample.shape)
        else:
            df_resample = data.resample(op).sum()
            print(df_resample.shape)
        return df_resample


def pump_sensor_dataframe():
    script_path = os.path.dirname(os.path.abspath(__file__))
    return pd.read_csv(
        pathlib.Path(script_path).joinpath('../../datasets/BBDD_tests', 'sensor_final.csv'),
        index_col="timestamp",
        parse_dates=["timestamp"]
    )
