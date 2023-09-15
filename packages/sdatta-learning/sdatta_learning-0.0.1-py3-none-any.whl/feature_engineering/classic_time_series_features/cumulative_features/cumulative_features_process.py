import pandas as pd
import numpy as np
from typing import List
from configs import global_static_config as static_config


class CumulativeFeatureGenerator:

    """
    This class generates cumulative features.
    Attributes:
        sales_str: The sales column name.
        date_str: The date column name.
        item_store_str: The item store column name.
    """
    def __init__(self):
        self.sales_str = static_config.sales_str
        self.date_str = static_config.date_str
        self.item_store_str = static_config.item_store_str
        self.store_str = static_config.store_str
        self.item_str = static_config.item_str

        pass

    def add_cumulative_sum_column_respect_time(self, df: pd.DataFrame, list_freq: List[str]) -> pd.DataFrame:
        """
        This function adds cumulative sum columns to the data frame.
        Args:
            df:  the data frame to add the cumulative sum columns to
            list_freq:  the list of frequencies to calculate the cumulative sum on

        Returns: the data frame with the cumulative sum columns

        """
        for freq in list_freq:
            df_grouped = df.groupby([self.item_store_str,
                                     pd.Grouper(key=self.date_str,
                                                freq=freq)])[self.sales_str].sum().reset_index()
            df_grouped[f"sales_cumulative_{self.item_store_str}_{freq}"] = \
                df_grouped.groupby(self.item_store_str, group_keys=False)[self.sales_str]\
                    .apply(lambda x: np.cumsum(x.shift(1)))
            df = df.merge(df_grouped.drop(columns=[self.sales_str])
                          , on=[self.item_store_str, self.date_str], how='left').ffill()
            df = df.drop_duplicates(subset=[self.item_store_str, self.date_str], keep='last')
        for column in df.columns:
            if column.startswith('sales_cumulative'):
                df[column] = df[column].fillna(0)
        return df

    import pandas as pd

    def calculate_statistics(self, df: pd.DataFrame, window_size: int) -> pd.DataFrame:
        """
        This function calculates the statistics of a target column for each (item, store) combination.
        Args:
            df:  the data frame to calculate the statistics on
            window_size: the window size to calculate the statistics on

        Returns: the data frame with the statistics

        """
        group_data = df.groupby([self.date_str, self.item_store_str])[self.sales_str]
        df_stat_roll = group_data.rolling(window_size, min_periods=1).agg(
            ['mean', 'median', 'std', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)]).shift(1).reset_index()
        cols_to_drop = [col for col in df_stat_roll.columns if col.startswith('level')]
        df_stat_roll = df_stat_roll.drop(columns=cols_to_drop)
        col_names_roll = [f'{self.item_store_str}_' + '_'.join([str(window_size), 'day', col]).strip() +
                          '_shifted' for col in ['mean', 'median', 'std', 'quantile_25', 'quantile_75']]
        df_stat_roll.columns = [self.date_str, self.item_store_str] + col_names_roll
        return df_stat_roll

    def calculate_rolling_mean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        This function calculates the rolling mean of a target column for each (item, store) combination.
        Args:
            df: the data frame to calculate the rolling mean on

        Returns: the data frame with the rolling mean

        """
        df_stat_roll_concat = pd.concat(df, axis=1)
        df_stat_roll_concat = df_stat_roll_concat.loc[:, ~df_stat_roll_concat.columns.duplicated()]
        df_stat_roll_concat = df_stat_roll_concat.reset_index(drop=True)
        return df_stat_roll_concat

    def merge_dataframes(self, df: pd.DataFrame, df_stat_roll_concat: pd.DataFrame) -> pd.DataFrame:
        """
        This function merges the data frame with the statistics with the original data frame.
        Args:
            df:  the original data frame
            df_stat_roll_concat:  the data frame with the statistics

        Returns: the merged data frame

        """
        df = pd.merge(df, df_stat_roll_concat, on=[self.item_store_str, self.date_str], how='left')
        df = df.drop_duplicates(subset=[self.item_store_str, self.date_str], keep='last')
        return df

    def calculate_statistics_functions_per_item_store(self, df: pd.DataFrame, window_size_list: List[int]) -> pd.DataFrame:
        """
        This function calculates the statistics of a target column for each (item, store) combination.
        The statistics can be computed for different window sizes.

        Args:
            df: the data frame to calculate the statistics on
            window_size_list: the list of window sizes to calculate the statistics on   -> list(range(1, 31))
        Returns:
            df_stat: the data frame with the statistics
        """
        df_stat_rolls = []
        for window_size in window_size_list:
            df_stat_roll = self.calculate_statistics(df, window_size)
            df_stat_roll = self.calculate_rolling_mean(df_stat_roll)
            df_stat_rolls.append(df_stat_roll)
        df_stat_roll_concat = pd.concat(df_stat_rolls, axis=1)
        df_stat_roll_concat = df_stat_roll_concat.loc[:, ~df_stat_roll_concat.columns.duplicated()]
        df_stat_roll_concat = df_stat_roll_concat.reset_index(drop=True)
        df = self.merge_dataframes(df, df_stat_roll_concat)
        return df

    import pandas as pd


    def calculate_statistics_2(self, df: pd.DataFrame, stat_col: str, window_size: int) -> pd.DataFrame:
        """
        This function calculates the statistics of a target column for each (item, store) combination.
        Args:
            df:  the data frame to calculate the statistics on
            stat_col:  the column to calculate the statistics on
            window_size:  the window size to calculate the statistics on

        Returns: the data frame with the statistics

        """
        group_data = df.groupby([self.date_str, stat_col])[self.sales_str]
        df_stat_roll = group_data.rolling(window_size, min_periods=1).agg(
            ['mean', 'median', 'std', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)]).shift(1).reset_index()
        cols_to_drop = [col for col in df_stat_roll.columns if col.startswith('level')]
        df_stat_roll = df_stat_roll.drop(columns=cols_to_drop)
        col_names_roll = [f'{stat_col}_' + '_'.join([str(window_size), 'day', col]).strip() + '_shifted' for col in
                          ['mean', 'median', 'std', 'quantile_25', 'quantile_75']]
        df_stat_roll.columns = [[self.date_str, stat_col] + col_names_roll]
        for col in col_names_roll:
            col_name_roll = f'{col}_365_day_rolling_mean'
            df_stat_roll[col_name_roll] = \
                df_stat_roll[col].rolling(365).mean().shift(1).reset_index()[
                    col]
        return df_stat_roll

    def merge_dataframes_2(self, df: pd.DataFrame, df_stat_roll_concat: pd.DataFrame, stat_col: str) -> pd.DataFrame:
        """
        This function merges the data frame with the statistics with the original data frame.
        Args:
            df:  the original data frame
            df_stat_roll_concat:  the data frame with the statistics
            stat_col:  the column to calculate the statistics on

        Returns: the merged data frame

        """
        df_stat_roll_concat = df_stat_roll_concat.loc[:, ~df_stat_roll_concat.columns.duplicated()]
        df_stat_roll_concat.columns = ['_'.join(map(str, col)).rstrip('_') for col in df_stat_roll_concat.columns]
        df_stat_roll_concat = df_stat_roll_concat.reset_index(drop=True)
        df = pd.merge(df, df_stat_roll_concat, on=[stat_col, self.date_str], how='left')
        df = df.drop_duplicates(subset=[stat_col, self.date_str], keep='last')
        return df

    def add_stats_functions_to_data(self, df: pd.DataFrame, window_size_list: List[int]) -> pd.DataFrame:
        """
        This function for loop on the self.item_store_str and call the function calculate_statistics_functions
        _per_item_store  then apply the function to the data frame and return the data frame with the new columns
        Args:
            df:     the data frame to calculate the statistics on
            window_size_list:   the list of window sizes to calculate the statistics on  -> list(range(1, 31))
        Returns:
            df:   the data frame with the statistics
        """
        for stat_col in [self.store_str, self.item_str]:
            df_stat_rolls = []
            for window_size in window_size_list:
                df_stat_roll = self.calculate_statistics_2(df, stat_col, window_size)
                df_stat_rolls.append(df_stat_roll)
            df_stat_roll_concat = pd.concat(df_stat_rolls, axis=1)
            df = self.merge_dataframes_2(df, df_stat_roll_concat, stat_col)
            del df_stat_rolls
        return df
