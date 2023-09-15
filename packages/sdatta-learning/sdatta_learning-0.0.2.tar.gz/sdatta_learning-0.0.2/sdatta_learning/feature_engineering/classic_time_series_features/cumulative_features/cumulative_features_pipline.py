from src.sdatta_learning.feature_engineering.classic_time_series_features.cumulative_features.cumulative_features_process \
    import CumulativeFeatureGenerator
from configs import global_static_config as static_config

import pandas as pd


def run_pipline_cumulative(data_sales: pd.DataFrame, freq_list_of_cumulative_features: list) -> pd.DataFrame:
    """
    This function run the pipeline of cumulative features and return the data with the new features
    Args:
        data_sales: the data with the sales

    Returns:
        data_sales2: the data with the new features
    """
    cumulative_feature_generator = CumulativeFeatureGenerator()
    data_sales = cumulative_feature_generator.\
        add_cumulative_sum_column_respect_time(data_sales, freq_list_of_cumulative_features)
    data_sales.drop(columns=[static_config.sales_str], inplace=True)
    return data_sales
