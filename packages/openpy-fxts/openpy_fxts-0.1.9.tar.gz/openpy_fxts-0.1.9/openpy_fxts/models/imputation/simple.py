# -*- coding: utf-8 -*-
# @Time    : 25/03/2023
# @Author  : Ing. Jorge Lara
# @Email   : jlara@iee.unsj.edu.ar
# @File    : ------------
# @Software: PyCharm

import pandas as pd
from sklearn.impute import SimpleImputer
from openpy_fxts.models.imputation.utilities.Utils import Metrics, Utils
from openpy_fxts.models.imputation.base_lib import init_models
from openpy_fxts.utils import get_numeric_categorical
import impyute as impy
import numpy as np

mt = Metrics()


class imp_basic(init_models):
    
    def __init__(
            self,
            df_miss: pd.DataFrame = None,
            df_true: pd.DataFrame = None
    ):
        super().__init__(df_miss, df_true)
        self.df_miss = df_miss
        self.df_true = df_true

    def constan(
            self,
            method: list
    ):
        """
        :param self.df_miss:
        :param method:
        :param self.df_true:
        :return:
        """
        dict_skelarn, dict_metrics = dict(), dict()
        # imputing with a constan
        for kk in method:
            df_imputation = self.df_miss.copy(deep=True)
            model = SimpleImputer(strategy=kk)
            df_imputation.iloc[:, :] = model.fit_transform(df_imputation)
            dict_skelarn[kk] = df_imputation
            dict_metrics = mt.add_dict_metrics(
                self.df_true,
                df_imputation,
                dict_metrics,
                kk
            )

        return dict_skelarn, dict_metrics

    def fillna(
            self,
            list_method: list = None,
            aux: str = 'mean'
    ):
        """
        :param list_fillna:
        :return:
        """
        dict_fillna, dict_metrics = dict(), dict()
        for i in list_method:
            df_imp = self.df_miss.copy(deep=True)
            df_imp.fillna(method=i, inplace=True)
            if Utils(df_imp).check_missing():
                model = SimpleImputer(strategy=aux)
                df_imp.iloc[:, :] = model.fit_transform(df_imp)
            dict_fillna[i] = df_imp
            dict_metrics = mt.add_dict_metrics(
                self.df_true,
                df_imp,
                dict_metrics,
                i
            )
        return dict_fillna, dict_metrics

    def replace_moving_window(
            self,
            data: np.array = None,
            res_min: int = 15,
            n_days: int = None,
            previous: bool = None,
            back: bool = None
    ):
        list_aux = Utils(self.df_miss).list_column_missing()
        dict_interpolate, dict_metrics = dict(), dict()
        numeric, categorical = get_numeric_categorical(self.df_miss)

        if previous is None and back is None:
            previous = True
        window = (24 * 60) / res_min
        if n_days is not None:
            window = window * n_days
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if np.isnan(data[row, col]):
                    if previous:
                        data[row, col] = data[row - window, col]
                    if back:
                        data[row, col] = data[row + window, col]

        if self.df_true is None:
            return X_imp
        else:
            dict_aux = dict()
            dict_aux = mt.add_dict_metrics(self.df_true[list_aux], X_imp[list_aux], dict_aux, 'moving_window')
            return X_imp, dict_aux['moving_window']

    def mean_moving_window(
            self,
            data: np.array = None,
            n_hours: int = None,
            res_min: int = None,
            n_past: bool = None,
            n_future: bool = None,
    ):
        aux = 0
        if n_hours is None:
            n = 1
            n_hours = n * 60
        while len(data[np.isnan(data)]) > 0:
            print(aux)
            if n_past is None and n_future is None and res_min is not None:
                n_past, n_future = n_hours / res_min, n_hours / res_min
            elif n_past is None and n_future is None and res_min is None:
                n_past, n_future = 4, 4
            for row in range(data.shape[0]):
                for col in range(data.shape[1]):
                    if np.isnan(data[row, col]):
                        data[row, col] = np.concatenate(
                            (
                                data[row - n_past: row, col],
                                data[row: row + n_future, col]
                            )
                        ).mean()
                        if np.isnan(data[row, col]):
                            data[row, col] = data[row - n_past: row, col].mean()
                            if np.isnan(data[row, col]):
                                data[row, col] = data[row: row + n_future, col].mean()


    def moving_window(
            self,
            nindex=None,
            wsize=3,
            errors="coerce",
            func=np.mean,
            inplace=False,
            **kwargs
    ):
        list_aux = Utils(self.df_miss).list_column_missing()
        X_imp = self.df_miss.copy()
        while X_imp.isnull().sum().sum() > 0:
            X_imp = impy.moving_window(
                X_imp.to_numpy(),
                nindex=nindex,
                wsize=wsize,
                errors=errors,
                func=func,
                inplace=inplace
            )
            X_imp = pd.DataFrame(X_imp, columns=self.df_miss.columns)
            X_imp['datetime'] = self.df_miss.index
            X_imp.set_index('datetime', inplace=True)
        if self.df_true is None:
            return X_imp
        else:
            dict_aux = dict()
            dict_aux = mt.add_dict_metrics(self.df_true[list_aux], X_imp[list_aux], dict_aux, 'moving_window')
            return X_imp, dict_aux['moving_window']

        return

    def interpolate(
            self,
            method: list,
            axis=0,
            limit=None,
            inplace=True,
            limit_direction=None,
            limit_area=None,
            downcast=None,
            order=2,
            aux: str = 'mean'
    ):
        """
        :param list_methods:
        :param axis:
        :param limit:
        :param inplace:
        :param limit_direction:
        :param limit_area:
        :param downcast:
        :param order:
        :return:
        """
        dict_interpolate, dict_metrics = dict(), dict()
        for kk in method:
            df_imp = self.df_miss.copy(deep=True)
            df_imp.interpolate(
                method=kk,
                axis=axis,
                limit=limit,
                inplace=inplace,
                limit_direction=limit_direction,
                limit_area=limit_area,
                downcast=downcast,
                order=order
            )
            if Utils(df_imp).check_missing():
                model = SimpleImputer(strategy=aux)
                df_imp.iloc[:, :] = model.fit_transform(df_imp)
            dict_interpolate[kk] = df_imp
            dict_metrics = mt.add_dict_metrics(
                self.df_true,
                df_imp,
                dict_metrics,
                kk
            )
        return dict_interpolate, dict_metrics
