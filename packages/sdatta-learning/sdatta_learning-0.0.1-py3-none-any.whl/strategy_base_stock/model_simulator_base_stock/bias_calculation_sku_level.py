import pandas as pd
import numpy as np
from configs import global_static_config as static_config
import pickle


def get_optimal_bias_sku_level(dict_of_stock_by_item, y_test_sku, y_pred_item, sku, threshold=0.03):
    """
    take the dict_of_stock_by_item and the y_test_sku and y_pred_item and the sku.
    if in the intersection of y_pred_item and y_test_sku is nan so in y_pred_item it 0.
    Args:
        dict_of_stock_by_item: the dictionary of stock levels for specific item_id cross level prediction level
        y_test_sku: the actual sales of the sku
        y_pred_item: the prediction of the item level
        sku: the sku that we want to get the prediction for
        threshold: the threshold on the quantile of the residual that we want to get the prediction for it
    Returns:
        the prediction of the sku level
    """
    data_ = pd.DataFrame()
    y_pred_item[static_config.date_str] = pd.to_datetime(y_pred_item[static_config.date_str])
    y_test_sku[static_config.date_str] = pd.to_datetime(y_test_sku[static_config.date_str])
    y_pred_item = y_pred_item.sort_values(by=static_config.date_str)
    y_test_sku = y_test_sku.sort_values(by=static_config.date_str)
    date_range = pd.date_range(start=y_pred_item[static_config.date_str].min(), end=y_pred_item[static_config.date_str].max())
    data_[static_config.date_str] = date_range
    data_ = data_[data_[static_config.date_str].isin(y_pred_item[static_config.date_str])]
    y_pred_item[static_config.date_str] = y_pred_item[static_config.date_str].astype(str)
    y_test_sku[static_config.date_str] = y_test_sku[static_config.date_str].astype(str)
    data_[static_config.date_str] = data_[static_config.date_str].astype(str)
    data_ = pd.merge(data_, y_test_sku, on=static_config.date_str, how='left')
    data_[static_config.sales_str].fillna(0, inplace=True)
    data_[static_config.sales_str] = data_[static_config.sales_str].astype(int)
    y_pred_item[static_config.sales_str] = y_pred_item[static_config.sales_str].astype(int)
    sum_test_sales = data_[static_config.sales_str].sum()
    y_pred_item["sku_sales_pred"] = y_pred_item.apply(lambda row: dict_of_stock_by_item[int(np.ceil(row[static_config.sales_str]))][sku], axis=1)
    y_pred_item["sku_sales_pred"] = y_pred_item["sku_sales_pred"].astype(int)
    y_pred_item["sku_sales_pred"] = y_pred_item["sku_sales_pred"].fillna(0)
    data_ = pd.merge(data_, y_pred_item[[static_config.date_str, "sku_sales_pred"]], on=static_config.date_str, how='left')
    data_["residual"] = data_[static_config.sales_str] - data_["sku_sales_pred"]
    residual_vec = data_["residual"].apply(lambda x: max(0, x)).values
    bias = 0

    while np.sum(residual_vec) / sum_test_sales >= threshold:
        bias += 1
        residual_vec = np.subtract(residual_vec, 1)
        residual_vec = np.maximum(0, residual_vec)
    return bias






def get_residual_analysis(store,dict_of_stock_levels, y_test, y_pred, threshold=0.03):
    """
    This function will get dictionary of stock levels that map from item_id cross level prediction level cross sku to float value.
    y_test dataframe that contains the actual sales for each item_id cross level prediction level cross sku.
    y_pred dataframe that contains the predicted sales for each item_id cross level prediction level cross sku.
    then it will calculate the residual analysis for each item_id cross level prediction level cross sku.

    Args:
        dict_of_stock_levels:   dictionary of stock levels that map from item_id cross level prediction level cross sku to float value.
        actual_sales:   dataframe that contains the actual sales for each item_id cross level prediction level cross sku.

    Returns:
            dictionary of the following structure: {item_id: {prediction_level: sum(remainder)}}
    """
    result = {}
    for sku in dict_of_stock_levels[0].keys():
        y_test_sku = y_test[(y_test[static_config.sku_str].astype(str) == str(sku)) & (y_test[static_config.store_str].astype(str) == str(store))]
        y_pred_item = y_pred
        result[sku] = get_optimal_bias_sku_level(dict_of_stock_levels, y_test_sku, y_pred_item, sku, threshold)
    return result

# def _load_models(store):
#     """
#     Load models from task and return a dictionary with dataset_file_name as key and dataframe as value
#     Args:
#         store:  store number
#     Returns:
#         dictionary with dataset_file_name as key and dataframe as value
#     """
#     task = Task.get_task(task_id=ID_TASK_LIST).artifacts
#     local_path = task[DICT_KEY].get_local_copy()
#     with open(local_path, 'rb') as f:
#         model_pkl = pickle.load(f)
#     models = model_pkl[str(store)]
#     return models

def load_dict_of_stock_levels(data_path):
    """
    load the dictionary of stock levels from the data_path
    Args:
        data_path:  the path to the dictionary of stock levels

    Returns:
        dictionary of stock levels
    """
    with open(data_path, 'rb') as f:
        optimal_stock_levels_sku_tuned = pickle.load(f)
    return optimal_stock_levels_sku_tuned

def train_model_with_blend_rolling(y_train, y_pred, coef_non_linear=0.2, window=2):
    """
    This function blends the predicted values with the rolling average of the last 2 days of the training set
    current implementation: 0.2 * y_pred + 0.8 * rolling_average
    Args:
        y_train:    the target of the training set
        y_pred:   the predicted values of the test set
        coef_non_linear:    the coefficient of the rolling average
        window: the window of the rolling average

    Returns:
        blend_with_rolling_avg_08: the blended values
    """
    rolling_average_train = y_train.rolling(window=window).mean().shift(window).fillna(0)
    blend_with_rolling_avg_08 = [coef_non_linear * b + (1 - coef_non_linear) * r for b, r in zip(y_pred, rolling_average_train)]
    blend_with_rolling_avg_08 = np.array(blend_with_rolling_avg_08, dtype=np.float64)
    blend_with_rolling_avg_08 = pd.Series(blend_with_rolling_avg_08, index=y_train.index)
    return blend_with_rolling_avg_08

def main2(dict_of_stock_levels,sku_sales_data, dict_for_model_simulator_base_stock, store):
    """
    This function will get dictionary of stock levels with information about the residual analysis at sku level
    The residual information is a map from item_id cross level prediction level cross sku to float value.
    then it uses this information to tune the stock levels to increase the bias in the prediction.
    remainder_dict: a dictionary of the following structure: {item_id: {prediction_level: sum(remainder)}}
    Args:
        dict_of_stock_levels: dictionary of stock levels with information item_id cross level prediction level cross sku

    Returns:
            a dictionary of the following structure: {item_id: {prediction_level: {sku: base_stock_level}}}

    Notes:
        the remainder is a positive integer, and the base_stock_level is a positive integer
    """
    sku_sales_data[static_config.sales_str] = sku_sales_data[static_config.sales_str].astype(int)
    sku_sales_data[static_config.sales_str] = np.where(sku_sales_data[static_config.sales_str] < 0, 0, sku_sales_data[static_config.sales_str])
    residual = {}

    for item_id in dict_for_model_simulator_base_stock.keys():
        actual_sales = dict_for_model_simulator_base_stock[item_id]['y_test_real']
        train_sales = dict_for_model_simulator_base_stock[item_id]['y_train_real']
        predicted_sales = dict_for_model_simulator_base_stock[item_id]['y_test_pred']
        predicted_sales_train = dict_for_model_simulator_base_stock[item_id]['y_train_pred']
        predicted_sales_train = train_model_with_blend_rolling(train_sales, predicted_sales_train)
        predicted_sales = np.array(predicted_sales, dtype=np.float64)
        predicted_sales = pd.Series(predicted_sales, index=actual_sales.index)
        predicted_sales = pd.DataFrame(predicted_sales).reset_index()
        predicted_sales.columns = [static_config.date_str, static_config.sales_str]
        predicted_sales_train = pd.DataFrame(predicted_sales_train).reset_index()
        predicted_sales_train.columns = [static_config.date_str, static_config.sales_str]
        y_pred = pd.concat([predicted_sales_train, predicted_sales], axis=0)
        y_pred[static_config.sales_str] = y_pred[static_config.sales_str].astype(int)
        y_pred[static_config.sales_str] = np.where(y_pred[static_config.sales_str] < 0, 0, y_pred[static_config.sales_str])
        residual[item_id] = get_residual_analysis(store,dict_of_stock_levels[item_id], sku_sales_data, y_pred, threshold=0.03)
    return residual

# if __name__ == '__main__':
#
#     dict_of_stock_levels = load_dict_of_stock_levels(path_optimal_stock_levels_sku_tuned)
#     optimal_stock_levels_sku_bias_tuned = main2(dict_of_stock_levels)


