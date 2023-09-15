# -*- coding: utf-8 -*-
# @Time    : 24/03/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm


import os
import pathlib
import logging

import pandas as pd

from openpy_fxts.error_handling_logging import update_logg_file

log_py = logging.getLogger(__name__)


class _sample_test:

    def _example(self, data_name: str, date_init: str, date_end: str):

        dataset = pd.DataFrame()
        script_path = os.path.dirname(os.path.abspath(__file__))
        if data_name == 'HPC':
            path_aux = pathlib.Path(script_path).joinpath("../BBDD", "HPC", "Raw", "household_power_consumption.csv")
            dataset = pd.read_csv(path_aux, index_col='datetime', parse_dates=True)
            x = ['Global_active_power', 'Global_reactive_power', 'Voltage', 'Global_intensity', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3', 'sub_metering_4']
            y = ['kW', 'kVA', 'Volt(V)', 'I(A)', 'SM1(kWh)', 'SM2(kWh)', 'SM3(kWh)', 'SM4(kWh)']
            for m, n in zip(x, y):
                dataset.columns = dataset.columns.str.replace(m, n)

            dataset = dataset.resample('15T', convention='start').mean()
            dataset = dataset[dataset.index >= date_init]
            dataset = dataset[['kW', 'kVA', 'Volt(V)', 'I(A)']]

            return dataset


        aux = dataset.empty

        if aux:
            update_logg_file('Enter the name of an available datasets source, refer to documentation.', 4, log_py)
            exit()

        return dataset
