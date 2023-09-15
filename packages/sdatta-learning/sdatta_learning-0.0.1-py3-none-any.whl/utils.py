import pandas as pd
import numpy as np
from configs import global_static_config as static_config


def parse_columns(data: pd.DataFrame) -> pd.DataFrame:
    """ Parse the columns of a dataframe.

        Args:
                data: The dataframe to parse.

        Returns:
                The parsed dataframe.
    """
    if static_config.date_str in data.columns:
        data[static_config.date_str] = pd.to_datetime(data[static_config.date_str])

    if static_config.sales_str in data.columns:
        # try float first and if not work try int

        data[static_config.sales_str] = data[static_config.sales_str].astype(float)

    if static_config.item_str in data.columns:
        data[static_config.item_str] = data[static_config.item_str].astype(np.int64)

    if static_config.sku_str in data.columns:
        data[static_config.sku_str] = data[static_config.sku_str].astype(np.int64)

    if static_config.store_str in data.columns:
        data[static_config.store_str] = data[static_config.store_str].astype(np.int64)

    return data


def sum_agg_per_item_date_store(data: pd.DataFrame) -> pd.DataFrame:
    """ Aggregate the sales per date, item and store.

        Args:
                data: The dataframe to aggregate.

        Returns:
            The aggregated dataframe.
    """
    data = data.groupby([static_config.date_str, static_config.store_str, static_config.item_str]).sum()[
        static_config.sales_str].reset_index()
    data[static_config.item_str] = data[static_config.item_str]
    data[static_config.store_str] = data[static_config.store_str]
    return data


def add_item_store_id_col(df, item_str=static_config.item_str, store_str=static_config.store_str):
    """ Add a column with the item and store id.

        Args:

                df: The dataframe to add the column to.
                item_str: The name of the item column.
                store_str: The name of the store column.


        Returns:
                The dataframe with the new column.

    """
    df[item_str + ', ' + store_str] = df[item_str].astype(str) + ', ' + df[store_str].astype(str)
    return df


def take_more_than_zero_sales(data):
    ''' Take only the rows with sales > 0.

        Args:
                data: The dataframe to take the rows from.


        Returns:
                The dataframe with only the rows with sales > 0.

        '''
    data = data[data[static_config.sales_str] > 0]
    return data


def fill_zero_in_sales_gaps(df: pd.DataFrame, end_date: str = None) -> pd.DataFrame:
    """ Fill the gaps in the sales column with 0. The gaps are the dates that are not in the dataframe.

        Args:
                df: The dataframe to fill the gaps in.
                end_date: The last date to fill the gaps until.
         Returns:
                The dataframe with the gaps filled.
    """
    if static_config.date_str in df.columns:
        df = df.set_index(static_config.date_str)

    if end_date is None:
        end_date = df.index.max()
    df = df.reindex(pd.date_range(start=min(df.index), end=end_date))
    df[static_config.sales_str] = df[static_config.sales_str].fillna(0)
    if static_config.store_str in df.columns:
        df = df.fillna({static_config.store_str: df[static_config.store_str].unique()[0]})
    if static_config.item_str in df.columns:
        df = df.fillna({static_config.item_str: df[static_config.item_str].unique()[0]})
    if static_config.item_store_str in df.columns:
        df = df.fillna({static_config.item_store_str: df[static_config.item_store_str].unique()[0]})
    df = parse_columns(df)
    return df.reset_index().rename(columns={static_config.index_str: static_config.date_str})

def rename_palmers_sales_data_columns(df: pd.DataFrame) -> pd.DataFrame:
    """ Rename the columns of the dataframe to match the other data

            Args:
                    df: The dataframe to rename the columns of.

            Returns:
                    The dataframe with the renamed columns.
        """
    df = df.rename(columns={static_config.outlet_str: static_config.store_str,
                            static_config.mat_no_str: static_config.sku_str,
                            static_config.quantity_str: static_config.sales_str})

    return df[[static_config.date_str, static_config.store_str, static_config.sku_str, static_config.sales_str]]

def add_item_column_from_sku_column(df: pd.DataFrame) -> pd.DataFrame:
    """ Add a column with the item id from the sku column.

            Args:
                    df: The dataframe to add the column to.

            Returns:
                    The dataframe with the new column.
        """
    df[static_config.item_str] = df[static_config.sku_str].astype(str).str[:-3].astype(np.int64)
    return df

def sales_window_agg(df: pd.DataFrame, window: int, type_of_agg: str, inference_bool=False) -> pd.DataFrame:
    """ Aggregate the sales per date, item and store.

            Args:
                    df: The dataframe to aggregate.
                    window: The window to aggregate over.

            Returns:
                The aggregated dataframe.
        """
    df[static_config.sales_str] = df[static_config.sales_str].rolling(window=window).agg(type_of_agg)
    if inference_bool == False:
        df = df.dropna()
    return df

def drop_sundays(df: pd.DataFrame) -> pd.DataFrame:
    """ Drop the sundays from the dataframe.

            Args:
                    df: The dataframe to drop the sundays from.

            Returns:
                    The dataframe without sundays.
        """
    df = df[df[static_config.date_str].dt.dayofweek != 6]
    return df


def get_min_max_date(id_data_with_features: pd.DataFrame) -> tuple:
    """ Get the min and max date of the data.

            Args:
                    id_data_with_features: The dataframe to get the min and max date from.

            Returns:
                    The min and max date.
    """
    
    min_date, max_date = id_data_with_features[static_config.date_str].min(), id_data_with_features[static_config.date_str].max()
    min_date, max_date = str(min_date)[:10], str(max_date)[:10]
    return min_date, max_date


def filter_data_by_bigger_the_date(df: pd.DataFrame, start_date: str) -> pd.DataFrame:
    """
    Filter data by date
    Args:
        df_sales:      pandas DataFrame
        start_date:    start date
        end_date:      end date

    Returns:   filtered pandas DataFrame

    """
    df = df[df[static_config.date_str] >= start_date]
    return df



def aggregate_data_by_date(df_sales: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate data by date
    Args:
        target_col:     name of target column
        df_sales:      pandas DataFrame

    Returns:   aggregate by target_col pandas DataFrame

    """
    df_sales[static_config.sales_str] = df_sales[static_config.sales_str].astype(np.float64)
    return df_sales.groupby(['date'])[static_config.sales_str].sum().reset_index()


def find_max_year(df: pd.DataFrame) -> int:
    """
    Find max year in data
    Args:
    df: pandas DataFrame

    Returns: max year in data
    """
    max_date = int(df[static_config.date_str].max().year)
    return max_date

def take_top_features(X: pd.DataFrame, id: str, dict_of_features: dict) -> pd.DataFrame:
    """
    take top features.
    Args:
        X:  df of X
        id:  str of id
        dict_of_features: dict of dict_of_features

    Returns:  X with top features

    """

    features = dict_of_features[id]['selected_features']
    features = [feature for feature in features if feature not in [static_config.store_str, static_config.item_str, static_config.date_str]]
    X = X[features]
    return X
