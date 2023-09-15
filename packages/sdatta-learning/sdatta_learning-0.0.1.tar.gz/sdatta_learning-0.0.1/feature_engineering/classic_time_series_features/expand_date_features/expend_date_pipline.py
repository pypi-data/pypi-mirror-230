from src.feature_engineering.classic_time_series_features.expand_date_features.expend_date_process import \
    ExpandDateFeatureGenerator

import pandas as pd


def expand_date_pipline(data: pd.DataFrame, list_of_columns_expand_date: list) -> pd.DataFrame:
    """
    This function run the pipeline of expand date features and return the data with the new features
    Args:
        data: the data with the sales

    Returns:
        data_sales2: the data with the new features
    """
    expand_date_feature_generator = ExpandDateFeatureGenerator(list_of_columns_expand_date)
    data = expand_date_feature_generator.expand_data_by_date(data)
    return data