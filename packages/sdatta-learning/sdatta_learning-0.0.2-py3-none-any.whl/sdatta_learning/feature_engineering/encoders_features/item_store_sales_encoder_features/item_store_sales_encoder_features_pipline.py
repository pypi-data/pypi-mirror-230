import pandas as pd
from src.sdatta_learning.feature_engineering.encoders_features.item_store_sales_encoder_features.item_store_sales_encoder_features_process import ItemStoreSalesEncodersFeaturesGenerator


def sales_encoder_pipline_fit_and_transform(data: pd.DataFrame, id: str, encoders_dict: dict,
                                            item_store_sales_encoder_features_config_dict: dict) -> (pd.DataFrame, dict):
    """
    fit and transform data with encoders - for train data
    Args:
        data:   df with sales data
        id:  str - id of the data
        encoders_dict: dict with encoders
        item_store_sales_encoder_features_config_dict: dict with config for the encoders


    Returns: transformed data

    """

    item_store_encoder_preprocess = ItemStoreSalesEncodersFeaturesGenerator(item_store_sales_encoder_features_config_dict)
    data_copy = data.copy()
    encoders_features_dict = item_store_encoder_preprocess.fit_all_encoder_and_all_X_columns_for_one_id(data_copy, id)
    # add 'sales_encoders' to encoders_dict if not exist
    if 'sales_encoders' not in encoders_dict.keys():
        encoders_dict['sales_encoders'] = {}
    encoders_dict['sales_encoders'][f'sales_encoder_{id}'] = encoders_features_dict
    transformed_data = item_store_encoder_preprocess.transform_all_sales_encoders(data_copy, id, encoders_features_dict)
    return transformed_data, encoders_dict


def sales_encoder_pipline_just_transform(data: pd.DataFrame, id: str, encoders_dict: dict,
                                         item_store_sales_encoder_features_config_dict: dict) -> pd.DataFrame:
    """
    transform data with encoders - for test data
    Args:
        data:  df with sales data
        id: str - id of the data
        encoders_dict: dict with encoders
        item_store_sales_encoder_features_config_dict: dict with config

    Returns: transformed data

    """
    data_copy = data.copy()
    item_store_encoder_preprocess = ItemStoreSalesEncodersFeaturesGenerator(item_store_sales_encoder_features_config_dict)
    sales_encoders_dict = encoders_dict['sales_encoders'][f'sales_encoder_{id}']
    transformed_data = item_store_encoder_preprocess.transform_all_sales_encoders(data_copy, id, sales_encoders_dict)
    return transformed_data
