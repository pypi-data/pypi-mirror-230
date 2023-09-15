import pandas as pd
import category_encoders as ce
from src.feature_engineering.encoders_features.item_store_sales_encoder_features import config
import copy
from configs import global_static_config as static_config


class ItemStoreSalesEncodersFeaturesGenerator:
    """
    This class is responsible for the item store sales encoders features.
        Attributes:
            item_str: The item column name.
            store_str: The store column name.
            sales_str: The sales column name.
            date_str: The date column name.
    """
    def __init__(self, item_store_sales_encoder_features_config_dict: dict):
        self.item_str = static_config.item_str
        self.store_str = static_config.store_str
        self.sales_str = static_config.sales_str
        self.date_str = static_config.date_str
        self.X_columns_types = item_store_sales_encoder_features_config_dict['X_columns_types_for_expand_date']
        self.encoders_types = item_store_sales_encoder_features_config_dict['encoders_types']

    def sales_encoder_fit(self, encoder: ce, specific_data: pd.DataFrame, X_columns_types: list) -> ce:
        """ Fit the encoder to the data.
            Args:
                    encoder: The encoder to fit.
                    specific_data: The data to fit the encoder to.
                    X_columns_types: The columns to fit the encoder to.

            Returns:
                    The fitted encoder.
        """
        if not all(specific_data[col].dtype == config.category_str for col in X_columns_types):
            specific_data[X_columns_types] = specific_data[X_columns_types].astype(config.category_str)
        encoder_fit = encoder.fit(specific_data[X_columns_types], specific_data[self.sales_str])
        return encoder_fit

    def fit_all_encoder_and_all_X_columns_for_one_id(self, data: pd.DataFrame, id: str) -> dict:
        """ Fit all the encoders to the data.
            Args:
                    data: The data to fit the encoders to.
                    id: The id of the data.


            Returns:
                    A dictionary with the fitted encoders.
        """
        sales_encoders_dict = {}
        sales_encoders_dict[id] = {}
        sales_encoders_dict[id][config.encoders_str] = {}
        sales_encoders_dict[id][config.X_columns_types_str] = copy.deepcopy(self.X_columns_types)

        for encoder_name in self.encoders_types.keys():
            encoder_class = self.encoders_types[encoder_name].__class__
            encoder = encoder_class()
            fitted_encoder = self.sales_encoder_fit(encoder, data, self.X_columns_types)
            sales_encoders_dict[id][config.encoders_str][encoder_name] = fitted_encoder
        return sales_encoders_dict

    def sales_encoder_transform_for_one_id(self, id_data, sales_encoders_dict: dict, id: str) -> pd.DataFrame:
        """ Transform the data with all the encoders.
            Args:
                    id_data: The data to transform.
                    sales_encoders_dict: The encoders to transform with.
                    id: The id of the data.

            Returns:
                    The transformed data.
        """
        transformed_all_data = pd.DataFrame()
        for encoder_name in sales_encoders_dict[id][config.encoders_str].keys():
            encoder = sales_encoders_dict[id][config.encoders_str][encoder_name]
            transformed_data = encoder.transform(id_data[sales_encoders_dict[id][config.X_columns_types_str]])
            transformed_data.columns = [encoder_name + '_' + col for col in transformed_data.columns]
            transformed_all_data = pd.concat([transformed_all_data, transformed_data], axis=1)
        return transformed_all_data

    def transform_all_sales_encoders(self, id_data: pd.DataFrame, id: str, sales_encoders_dict: dict) -> pd.DataFrame:
        """ Transform the data with all the encoders.
            Args:
                    id_data: The data to transform.
                    id: The id of the data.
                    sales_encoders_dict: The encoders to transform with.


            Returns:
                    The transformed data.
        """
        transformed_all_data = pd.DataFrame()
        transformed_data = self.sales_encoder_transform_for_one_id(id_data, sales_encoders_dict, id)
        transformed_data[static_config.id_str] = id
        transformed_data[self.X_columns_types] = id_data[self.X_columns_types]
        transformed_all_data = pd.concat([transformed_all_data, transformed_data], axis=1)
        return transformed_all_data
