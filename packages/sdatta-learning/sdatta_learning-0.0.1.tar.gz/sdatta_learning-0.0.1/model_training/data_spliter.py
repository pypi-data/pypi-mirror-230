from configs import global_static_config as static_config
from sklearn.model_selection import TimeSeriesSplit
import pandas as pd


def create_X_and_y(df: pd.DataFrame, columns_to_drop_for_X:list, column_of_y) -> (pd.DataFrame, pd.Series):
    """
    create X and y from df. X is df without the column of y and the columns to drop for X.
    y with target column only.
    Args:
        df:     pd.DataFrame

    Returns:    X, y

    """

    df = df.set_index(static_config.date_str)
    X = df
    for column in columns_to_drop_for_X:
        if column in df.columns:
            X = X.drop(columns=[column])
    y = df[column_of_y]
    return X, y



def create_X_y_train_test_split(X: pd.DataFrame, y: pd.Series, split_date:str) -> (pd.DataFrame, pd.DataFrame, pd.Series, pd.Series):
    """
    create X_train, X_test, y_train, y_test from X and y with split_date.
    Args:
        X:        pd.DataFrame
        y:      pd.Series
        split_date:     str

    Returns:   X_train, X_test, y_train, y_test

    """
    X_train = X[X.index < split_date]
    X_test = X[X.index >= split_date]
    y_train = y[X.index < split_date]
    y_test = y[X.index >= split_date]
    return X_train, X_test, y_train, y_test



def get_fold_indexes(n_samples: int, n_folds: int) -> list:
    """
    get fold indexes for cross validation.
    Args:
        n_samples:  int
        n_folds:  int

    Returns:     list

    """
    fold_indexes = []
    step = n_samples // n_folds
    for i in range(n_folds):
        start = i * step
        end = start + step
        if i == n_folds - 1:
            end = n_samples  # Last fold takes remaining samples
        fold_indexes.append((start, end))
    return fold_indexes

def get_separated_blocked_folds(X: pd.DataFrame, y: pd.Series, n_splits: int, val_percent: float) -> (list, list, list, list):
    """
    get separated blocked folds for cross validation.
    Args:
        X: df of X
        y: series of y
        n_splits: number of splits(folds)
        val_percent:  percent of validation data from each fold

    Returns:    X_trains, y_trains, X_vals, y_vals

    """

    fold_indices = get_fold_indexes(len(X), n_splits)
    val_samples = int((fold_indices[0][1]-fold_indices[0][0]) * val_percent)

    X_trains, y_trains = [], []
    X_vals, y_vals = [], []

    for i in range(n_splits):
        X_train_fold = X.iloc[fold_indices[i][0]:(fold_indices[i][1]-val_samples)]
        X_val_fold = X.iloc[(fold_indices[i][1]-val_samples):fold_indices[i][1]]
        y_train_fold = y.iloc[fold_indices[i][0]:(fold_indices[i][1]-val_samples)]
        y_val_fold = y.iloc[(fold_indices[i][1]-val_samples):fold_indices[i][1]]

        X_trains.append(X_train_fold)
        y_trains.append(y_train_fold)

        X_vals.append(X_val_fold)
        y_vals.append(y_val_fold)

    return X_trains, y_trains, X_vals, y_vals


def get_timeseries_folds(X: pd.DataFrame, y: pd.Series, n_splits: int, val_size: int) -> (list, list, list, list):
    """
    get time series folds for cross validation.
    Args:
        X: df of X
        y: series of y
        n_splits:   number of splits(folds)
        val_size:   size of validation data from each fold(num of indices)

    Returns:   X_trains, y_trains, X_vals, y_vals

    """
    tscv = TimeSeriesSplit(n_splits=n_splits, test_size=val_size)

    X_trains, y_trains = [], []
    X_vals, y_vals = [], []

    for train_index, val_index in tscv.split(X):
        X_trains.append(X.iloc[train_index])
        y_trains.append(y.iloc[train_index])
        X_vals.append(X.iloc[val_index])
        y_vals.append(y.iloc[val_index])

    return X_trains, y_trains, X_vals, y_vals


def blocked_fixed_window_folds(X: pd.DataFrame, y: pd.Series, n_splits: int, val_percent: float, len_of_block: int) -> (list, list, list, list):
    """
    get blocked fixed window folds for cross validation.
    Args:
        X: df of X
        y: series of y
        n_splits:   number of splits(folds)
        val_percent:   percent of validation data from each fold

    Returns:    X_trains, y_trains, X_vals, y_vals

    """
    len_of_data = len(X)
    len_of_val = int(len_of_block * val_percent)
    len_of_train = len_of_block - len_of_val
    len_of_stride = len_of_data - len_of_train
    ratio_of_stride = len_of_stride / n_splits
    X_trains = []
    y_trains = []
    X_vals = []
    y_vals = []
    for i in range(n_splits):
        X_trains.append(X.iloc[len_of_data - int(i * ratio_of_stride) - len_of_block:len_of_data - int(i * ratio_of_stride) - len_of_val])
        y_trains.append(y.iloc[len_of_data - int(i * ratio_of_stride) - len_of_block:len_of_data - int(i * ratio_of_stride) - len_of_val])
        X_vals.append(X.iloc[len_of_data - int(i * ratio_of_stride) - len_of_val:len_of_data - int(i * ratio_of_stride)])
        y_vals.append(y.iloc[len_of_data - int(i * ratio_of_stride) - len_of_val:len_of_data - int(i * ratio_of_stride)])
    return X_trains, y_trains, X_vals, y_vals


def create_ts_folds(X: pd.DataFrame, y: pd.Series, n_splits:int,
                    cv_type: str,
                    val_percent: float,
                    val_size: int,
                    len_of_fold: int) -> (list, list, list, list):
    """
    create folds for cross validation.
    Args:
        X: df of X
        y: series of y
        n_splits: int of number of splits(folds)
        cv_type: str of type of cross validation
        val_percent: float of percent of validation data from each fold
        val_size: int of size of validation data from each fold
        len_of_fold: int of length of each fold

    Returns:   X_trains, y_trains, X_vals, y_vals

    """
    if cv_type == 'SeparatedBlocked':
        return get_separated_blocked_folds(X, y, n_splits, val_percent)
    elif cv_type == 'FixedWindowBlocked':
        return blocked_fixed_window_folds(X, y, n_splits, val_percent, len_of_fold)
    elif cv_type == 'TimeSeriesSplit':
        return get_timeseries_folds(X, y, n_splits, val_size)
    else:
        raise ValueError('cv_type must be one of "SeparatedBlocked", "FixedWindowBlocked", "TimeSeriesSplit"')


