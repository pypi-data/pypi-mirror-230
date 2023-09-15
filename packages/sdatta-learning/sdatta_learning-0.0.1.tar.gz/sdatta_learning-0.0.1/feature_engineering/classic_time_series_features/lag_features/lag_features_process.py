import pandas as pd
from configs import global_static_config as static_config


class LagsRollingAverageDiffsEWMsFeaturesGenerator:
    def __init__(self, lags_features_config_dict = None):
        self.item_str = static_config.item_str
        self.store_str = static_config.store_str
        self.sales_str = static_config.sales_str
        self.date_str = static_config.date_str
        self.item_store_str = static_config.item_store_str
        self.list_of_lag_types = list(lags_features_config_dict.keys())


        if 'lag' in self.list_of_lag_types:
            self.lags_back = lags_features_config_dict['lag']
        if 'rolling' in self.list_of_lag_types:
            self.windows = lags_features_config_dict['rolling']
        if 'diff' in self.list_of_lag_types:
            self.diff_lags = lags_features_config_dict['diff']
        if 'ewm' in self.list_of_lag_types:
            self.ewms = lags_features_config_dict['ewm']

    def add_lags_and_rolling_averages_and_diffs_and_ewms(self, df1: pd.DataFrame, item: str, list_of_lag_types: list):
        """
                        add lags, rolling averages, diffs and ewms to the dataframe and filter by the list_of_lag_types
        Args:
            df1: df to add the features to
            item:  item to add the features to
            list_of_lag_types: list of lag types to add

        Returns:    df1 with the added features

        """
        if 'lag' in list_of_lag_types:
            for lag in self.lags_back:
                df1[f'{item}_sales_lag_{lag}'] = df1[self.sales_str].shift(lag)
        if 'rolling' in list_of_lag_types:
            for window in self.windows:
                df1[f'{item}_sales_rolling_{window}'] = df1[self.sales_str].shift(1).rolling(window).mean()
        if 'diff' in list_of_lag_types:
            for diff_lag in self.diff_lags:
                df1[f'{item}_sales_diff_{diff_lag}'] = df1[self.sales_str].shift(1) - df1[self.sales_str].shift(diff_lag)
        if 'ewm' in list_of_lag_types:
            for ewm in self.ewms:
                df1[f'{item}_sales_ewm_{ewm}'] = df1[self.sales_str].shift(1).ewm(alpha=ewm).mean()
        return df1

    def return_df_of_item_store_sales_with_lags_rolling_diff_ewm(self, data: pd.DataFrame,
                                                                 id_str: str = static_config.id_str) -> pd.DataFrame:
        """
        Returns a dataframe of item store sales with lags, rolling averages, diffs and ewms
        Args:
            data: df to add the features to
            id_str: str of the id to add the features to

        Returns:   df with the added features

        """

        item_store_data = LagsRollingAverageDiffsEWMsFeaturesGenerator.add_lags_and_rolling_averages_and_diffs_and_ewms(
            self, data[[self.date_str, self.sales_str, self.item_store_str]], id_str, self.list_of_lag_types)

        return item_store_data.drop(columns=[self.sales_str])

    def return_df_of_store_sales_with_lags_rolling_diff_ewm(self, data: pd.DataFrame, store_str: str = static_config.store_str) -> pd.DataFrame:
        """
        Returns a dataframe of store sales with lags, rolling averages, diffs and ewms
        Args:
            data: df to add the features to
            store_str: str of the store to add the features to

        Returns: df with the added features

        """
        df_of_store_sales = pd.DataFrame()
        i = 0
        for store in data[store_str].unique():
            i += 1
            store_data = data[data[store_str] == store].groupby(self.date_str)[[self.sales_str]].sum().reset_index()
            store_data[store_str] = store
            store_data = LagsRollingAverageDiffsEWMsFeaturesGenerator.add_lags_and_rolling_averages_and_diffs_and_ewms(
                self, store_data[[self.date_str, self.sales_str]], self.store_str, self.list_of_lag_types)
            store_data[store_str] = store
            df_of_store_sales = pd.concat([df_of_store_sales, store_data])
        return df_of_store_sales.drop(columns=[self.sales_str])

    def return_df_of_item_sales_with_lags_rolling_diff_ewm(self, data: pd.DataFrame,
                                                           item_str: str = static_config.item_str) -> pd.DataFrame:
        """
        Returns a dataframe of item sales with lags, rolling averages, diffs and ewms
        Args:
            data:   df to add the features to
            item_str:   str of the item to add the features to

        Returns:   df with the added features

        """
        df_of_item_sales = pd.DataFrame()
        i = 0
        for item in data[item_str].unique():
            i += 1
            item_data = data[data[item_str] == item].groupby(self.date_str)[[self.sales_str]].sum().reset_index()
            item_data[item_str] = item
            item_data = LagsRollingAverageDiffsEWMsFeaturesGenerator.add_lags_and_rolling_averages_and_diffs_and_ewms(
                self, item_data[[self.date_str, self.sales_str]], self.item_str, self.list_of_lag_types)
            item_data[item_str] = item
            df_of_item_sales = pd.concat([df_of_item_sales, item_data])
        return df_of_item_sales.drop(columns=[self.sales_str])
