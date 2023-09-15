from src.feature_engineering.event_features.one_hot_encoder_event_features.one_hot_encoder_event_process import OneHotEncoderEventFeaturesGenerator
import pandas as pd

def one_hot_encoder_event_pipline(data: pd.DataFrame, event_one_hot_date: pd.DataFrame) -> pd.DataFrame:
    """
    This function run the pipeline of one hot encoder event features and return the data with the new features
    Args:
        data: the data with the sales
        event_one_hot_date: the data with the events

    Returns:
        data_sales2: the data with the new features
    """
    one_hot_encoder_event_features_generator = OneHotEncoderEventFeaturesGenerator()
    data = one_hot_encoder_event_features_generator.merge_event_one_hot_encoder_by_date(data, event_one_hot_date)
    return data