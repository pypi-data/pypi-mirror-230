import pandas as pd
from src.feature_engineering.classic_time_series_features.lag_features.lag_features_process import \
    LagsRollingAverageDiffsEWMsFeaturesGenerator
from src.utils import parse_columns, sum_agg_per_item_date_store, add_item_store_id_col, \
    take_more_than_zero_sales
import warnings

warnings.filterwarnings("ignore")


def run_item_pipline_lags_rolling_averages_diffs_ewms(data: pd.DataFrame,
                                                      lags_features_config_dict: dict,
                                                      parse_columns_bool: bool = False,
                                                      sum_agg_per_item_date_store_bool: bool = False,
                                                      add_item_store_id_col_bool: bool = False,
                                                      take_more_than_zero_sales_bool: bool = False) -> pd.DataFrame:
    """
    """
    lags_rolling_averages_diffs_ewms_preprocess = LagsRollingAverageDiffsEWMsFeaturesGenerator(lags_features_config_dict)
    if parse_columns_bool:
        data = parse_columns(data)
    if sum_agg_per_item_date_store_bool:
        data = sum_agg_per_item_date_store(data)
    if add_item_store_id_col_bool:
        data = add_item_store_id_col(data)
    if take_more_than_zero_sales_bool:
        data = take_more_than_zero_sales(data)
    df_of_item_sales = lags_rolling_averages_diffs_ewms_preprocess.return_df_of_item_sales_with_lags_rolling_diff_ewm(
        data)

    return df_of_item_sales


def run_store_pipline_lags_rolling_averages_diffs_ewms(data: pd.DataFrame,
                                                       lags_features_config_dict, parse_columns_bool: bool = False,
                                                       sum_agg_per_item_date_store_bool: bool = False,
                                                       add_item_store_id_col_bool: bool = False,
                                                       take_more_than_zero_sales_bool: bool = False) -> pd.DataFrame:
    """
    Runs the store pipeline for lags, rolling averages, diffs and ewms
    Args:
        data: df to add the features to
        parse_columns_bool: bool to sum agg per item date store
        sum_agg_per_item_date_store_bool:    bool to add item store id col
        add_item_store_id_col_bool:     bool to take more than zero sales
        take_more_than_zero_sales_bool:     bool to parse the columns

    Returns:    store df with the added features

    """
    lags_rolling_averages_diffs_ewms_preprocess = LagsRollingAverageDiffsEWMsFeaturesGenerator(lags_features_config_dict)
    if parse_columns_bool:
        data = parse_columns(data)
    if sum_agg_per_item_date_store_bool:
        data = sum_agg_per_item_date_store(data)
    if add_item_store_id_col_bool:
        data = add_item_store_id_col(data)
    if take_more_than_zero_sales_bool:
        data = take_more_than_zero_sales(data)

    df_of_store_sales = lags_rolling_averages_diffs_ewms_preprocess.return_df_of_store_sales_with_lags_rolling_diff_ewm(
        data)
    return df_of_store_sales


def run_id_pipline_lags_rolling_averages_diffs_ewms(data: pd.DataFrame,
                                                    lags_features_config_dict, parse_columns_bool: bool = False,
                                                    sum_agg_per_item_date_store_bool: bool = False,
                                                    add_item_store_id_col_bool: bool = False,
                                                    take_more_than_zero_sales_bool: bool = False) -> pd.DataFrame:
    """
    Runs the id pipeline for lags, rolling averages, diffs and ewms
    Args:
        data:  df to add the features to
        parse_columns_bool:     bool to parse the columns
        sum_agg_per_item_date_store_bool:   bool to sum agg per item date store
        add_item_store_id_col_bool:   bool to add item store id col
        take_more_than_zero_sales_bool:  bool to take more than zero sales

    Returns:   id df with the added features

    """
    lags_rolling_averages_diffs_ewms_preprocess = LagsRollingAverageDiffsEWMsFeaturesGenerator(lags_features_config_dict)
    if parse_columns_bool:
        data = parse_columns(data)
    if sum_agg_per_item_date_store_bool:
        data = sum_agg_per_item_date_store(data)
    if add_item_store_id_col_bool:
        data = add_item_store_id_col(data)
    if take_more_than_zero_sales_bool:
        data = take_more_than_zero_sales(data)

    df_of_item_store_sales = lags_rolling_averages_diffs_ewms_preprocess.return_df_of_item_store_sales_with_lags_rolling_diff_ewm(
        data)
    return df_of_item_store_sales
