import pandas as pd
import itertools
import numpy as np
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
from configs import global_static_config as static_config


class LinearFeatures:

    def __init__(self):
        pass

    def train_test_val_split(self, X, y, split_date):
        """
        This function is for splitting the data to train, test and validation sets based on the split date
        Args:
            X: features
            y: target
            split_date: date to split the data

        Returns:
            X_train, X_test, X_val, y_train, y_test, y_val
        """
        X_train = X[X.index < split_date]
        X_test = X[X.index >= split_date]
        y_train = y[y.index < split_date]
        y_test = y[y.index >= split_date]
        return X_train, X_test, y_train, y_test

    def find_best_window(self, df, window_size: int, target: str = "sales"):
        warnings.filterwarnings("ignore")
        p = d = q = range(0, window_size)
        pdq = list(itertools.product(p, d, q))
        best_aic = np.inf
        best_pdq = None
        for param in pdq:
            try:
                temp_model = ARIMA(df[target], order=param)
                results = temp_model.fit()
                if results.aic < best_aic:
                    best_aic = results.aic
                    best_pdq = param
            except:
                continue
        return best_pdq[2]

    def smoothing_exponential(self, y_train, y_test, y_pred, window_length: int, W_pred: float,
                              W_smoothing: float, trend='add', seasonal='add'):
        """
        This function blends the predicted values with the exponential smoothing of the last window_Size days of the training set
        the formula is: W_pred * y_pred + W_smoothing * exponential_smoothing
        Args:
            y_train:    the target of the training set
            y_test:    the target of the test set
            y_pred:   the predicted values of the test set
            window_length:    the size of the window to calculate the exponential smoothing
            W_pred:    the weight of the predicted values
            W_smoothing:    the weight of the exponential smoothing
            trend:    the trend of the exponential smoothing
            seasonal:    the seasonal of the exponential smoothing

        Returns:
            the blended values
        """
        ets_model = ExponentialSmoothing(y_train, trend=trend, seasonal=seasonal, seasonal_periods=window_length)
        ets_model_trained = ets_model.fit()
        ets_predictions = ets_model_trained.predict(start=len(y_train), end=len(y_train) + len(y_test) - 1)
        blend_with_smoothing = [W_pred * b + W_smoothing * r for b, r in zip(y_pred, ets_predictions)]
        return blend_with_smoothing

    def rolling_blend(self, y_train, y_test, y_pred, window_length: int, W_pred: float,
                      W_rolling: float):
        """
        This function blends the predicted values with the rolling average of the last 2 days of the training set
        the formula is: W_pred * y_pred + W_rolling * rolling_average
        Args:
            y_train:    the target of the training set
            y_test:    the target of the test set
            y_pred:   the predicted values of the test set

        Returns:
            blend_with_rolling_avg_08: the blended values
        """
        actual_sales_extended = pd.concat([y_train, y_test])
        rolling_average = actual_sales_extended.rolling(window=window_length).mean().shift(window_length).fillna(0)
        blend_with_rolling = [W_pred * b + W_rolling * r for b, r in zip(y_pred, rolling_average[window_length:])]
        return blend_with_rolling

    def explore_weights(self,y_train, y_test, y_pred, best_window: int, weights):
        """
        This function explores the weights of the exponential smoothing and the rolling average to find the best weights
        and the best minimum error
        Args:
            y_train:    the target of the training set
            y_test:    the target of the test set
            y_pred:   the predicted values of the test set
            best_window:    the best window size

        Returns:
            best_w_exp: the best weight for the exponential smoothing
            best_w_roll: the best weight for the rolling average
            best_error_exp: the best error for the exponential smoothing
            best_error_roll: the best error for the rolling average
        """
        errors_exp = []
        errors_roll = []
        best_w_exp = None
        best_w_roll = None
        best_error_exp = None
        best_error_roll = None
        for w in weights:
            y_pred_smooth = self.smoothing_exponential(y_train, y_test, y_pred, best_window,
                                                       w, 1 - w)
            y_pred_rolling = self.rolling_blend(y_train, y_test, y_pred, best_window,
                                                w, 1 - w)
            error_smoothing = mean_absolute_error(y_test, y_pred_smooth)
            error_rolling = mean_absolute_error(y_test, y_pred_rolling)
            errors_exp.append((w, error_smoothing))
            errors_roll.append((w, error_rolling))
            best_w_exp, best_error_exp = self.chek_min_error(best_w_exp, w, error_smoothing, best_error_exp)
            best_w_roll, best_error_roll = self.chek_min_error(best_w_roll, w, error_rolling, best_error_roll)
        return best_w_exp, best_w_roll, best_error_exp, best_error_roll

    def chek_min_error(self, best_w: float, w: float,error,best_error):
        """
        This function checks if the current error is the minimum error and if so it updates the best error and best w
        Args:
            best_w: the best w so far
            w: the current w
            error: the current error
            best_error: the best error so far

        Returns:
            best_w: the best w so far
        """
        if best_w is None or error < best_error:
            best_w = w
            best_error = error
        return best_w, best_error

    def best_method_w_error(self, best_w_exp: float, best_w_roll: float, best_error_exp: float, best_error_roll: float):
        """
        This function determines the best method and the best weight and the best error based on the errors of the two methods
        Args:
            best_w_exp: the best weight of the exponential smoothing
            best_w_roll: the best weight of the rolling average
            best_error_exp: the best error of the exponential smoothing
            best_error_roll: the best error of the rolling average

        Returns:
            best_method: the best method
            best_weight: the best weight
            best_error: the best error
        """
        if best_error_exp < best_error_roll:
            best_method = 'smoothing_exponential'
            best_weight = best_w_exp
            best_error = best_error_exp

        else:
            best_method = 'rolling_blend'
            best_weight = best_w_roll
            best_error = best_error_roll
        return best_method, best_weight, best_error

    def for_plot_window_and_method(self, df: pd.DataFrame, features_importance, model: object, split_date: str, window_size: int, weights: list):
        """
        This function is used for preparing the data for the plot for dictionary that contains the following keys:
        'window_size': the window size
        'method': the best method
        'weight': the best weight
        'error': the best error
        Args:
            df: the dataframe
            features_importance: the features importance
            model: the model

        Returns:
            dict_for_plot: the dictionary for the plot
        """
        df[static_config.date_str] = pd.to_datetime(df[static_config.date_str])
        df = df.set_index(static_config.date_str)
        X = df.drop(static_config.sales_str, axis=1)
        y = df[static_config.sales_str]
        X = X[features_importance]
        print("sales_str", static_config.sales_str)
        print("features_importance", features_importance)
        X_train, X_test, y_train, y_test = self.train_test_val_split(X, y, split_date)
        best_window = self.find_best_window(df, window_size=window_size)
        trained_model = model.fit(X_train, y_train)
        y_pred = trained_model.predict(X_test)
        dict_for_plot = { "smoothing_exponential": [],
        "rolling_blend": []}
        errors_exp = []
        errors_roll = []
        for w in weights:

            y_pred_smooth = self.smoothing_exponential(y_train, y_test, y_pred, best_window,
                                                       w, 1 - w)
            y_pred_rolling = self.rolling_blend(y_train, y_test, y_pred, best_window,
                                                w, 1 - w)
            error_smoothing = mean_absolute_error(y_test, y_pred_smooth)
            error_rolling = mean_absolute_error(y_test, y_pred_rolling)
            errors_exp.append((w, error_smoothing))
            errors_roll.append((w, error_rolling))
            dict_for_plot["smoothing_exponential"].append({"error": error_smoothing, "w": w})
            dict_for_plot["rolling_blend"].append({"error": error_rolling, "w": w})

        best_w_exp, best_w_roll, best_error_exp, best_error_roll = self.explore_weights(y_train, y_test, y_pred,
                                                                                        best_window, weights)
        best_method, best_weight, best_error = self.best_method_w_error(best_w_exp, best_w_roll, best_error_exp,
                                                                        best_error_roll)
        dict_for_plot["best_method"] = best_method
        dict_for_plot["best_weight"] = best_weight
        dict_for_plot["best_error"] = best_error
        dict_for_plot["best_window"] = best_window
        return dict_for_plot



    def find_best_window_and_method(self, df: pd.DataFrame, features_importance: list ,model: object, split_date: str, window_size: int, weights: list):
        """
        This function finds the best window size and the best method and the best weight for the blending
        by the following steps:
        1. finds the best window size
        2. finds the best weight for the exponential smoothing and the rolling average
        3. finds the best method and the best weight and the best error
        Args:
            df: the dataframe
            model: the model to use -> catboost or xgboost

        Returns:
            best_window: the best window size
            best_method: the best method
            best_weight: the best weight
        """
        df[static_config.date_str] = pd.to_datetime(df[static_config.date_str])
        df = df.set_index(static_config.date_str)
        X = df.drop(static_config.sales_str, axis=1)
        y = df[static_config.sales_str]
        X = X[features_importance]
        X_train, X_test, y_train, y_test = self.train_test_val_split(X, y, split_date)
        best_window = self.find_best_window(df, window_size=window_size)
        trained_model = model.fit(X_train, y_train)
        y_pred = trained_model.predict(X_test)
        best_w_exp, best_w_roll, best_error_exp, best_error_roll = self.explore_weights(y_train, y_test, y_pred, best_window, weights)
        best_method, best_weight, best_error = self.best_method_w_error(best_w_exp, best_w_roll, best_error_exp, best_error_roll)

        print(f"best window: {best_window}  ,best method: {best_method} ,best weight: {best_weight} and best error: {best_error}")
        return best_method, best_weight, best_window


# data_ = data_clearml()
# LinearFeatures(data_).find_best_window_and_method(data_)

