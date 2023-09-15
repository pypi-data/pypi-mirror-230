import pandas as pd
import numpy as np
import configs.global_static_config as static_config
import json


def calculate_base_stock(train: pd.DataFrame,
                         threshold) -> float:
    """
    This function calculates the base stock for a given train
    Args:
        train: dataframe with the following columns: [date, sales, stock, 3_days_sales]
        threshold: value between 0 and 1, default value is 0.5

    Returns:
        base stock value

    """
    residual = np.where(min(train[static_config.stock_str] - train[static_config.three_days_sales_str]) <= 0, 1,
                        min(train[static_config.stock_str] - train[static_config.sales_str]))
    palmers_max_stock_train = max(train[static_config.stock_str])
    max_3_days_sales_train = max(train[static_config.three_days_sales_str].fillna(0))
    upper_stock_train = np.where(np.ceil(residual * threshold) <= 0, 1, np.ceil(residual * threshold)).item()
    base_stock_train_value = np.where(upper_stock_train + max_3_days_sales_train >= palmers_max_stock_train,
                                      palmers_max_stock_train, upper_stock_train + max_3_days_sales_train).item()
    if base_stock_train_value <= 0:
        base_stock_train_value = 1.0
    return base_stock_train_value


def generate_train_slice(df_sku_store_sales_stock: pd.DataFrame, num_of_days: int) -> pd.DataFrame:
    """
    This function generates a train slice from a given dataframe
    Args:
        df_sku_store_sales_stock: dataframe with the following columns: [date, sales, stock, 3_days_sales]
        num_of_days: number of days to take from the end of the dataframe

    Returns: dataframe with the following columns: [date, sales, stock, 3_days_sales] with the last num_of_days days

    """
    df = df_sku_store_sales_stock[(df_sku_store_sales_stock[static_config.date_str] >
                                   df_sku_store_sales_stock[static_config.date_str].max() -
                                   pd.Timedelta(days=num_of_days))]
    return df


def add_3_days_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function adds a column with the sum of the sales of the last 3 days
    Args:
        df: dataframe with the following columns: [date, sales, stock]

    Returns: dataframe with the following columns: [date, sales, stock, 3_days_sales]

    """
    df[static_config.three_days_sales_str] = df[static_config.sales_str].rolling(3).sum()
    return df


def generate_item_column(sku_store: str) -> str:
    """
    generate "item" column from "sku_store" column
    Args:
        sku_store:  sku_store column

    Returns: item column

    """
    item = sku_store.split(', ')[0][:-3]
    return item


def add_sku_store_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    generate "sku_store" column from "sku" and "store" columns
    Args:
        df:  dataframe

    Returns: dataframe with "sku_store" column

    """
    if static_config.sku_str + ', ' + static_config.store_str not in df.columns:
        df[static_config.sku_store_str] = df[static_config.sku_str].astype(str) + ', ' + \
                                           df[static_config.store_str].astype(str)
    return df


def date_parse_sales_data(sales_sparse: pd.DataFrame) -> pd.DataFrame:
    """
    convert "date" column to datetime type
    Args:
        sales_sparse:  dataframe

    Returns: dataframe with "date" column in datetime type

    """
    sales_sparse[static_config.date_str] = pd.to_datetime(sales_sparse[static_config.date_str])
    return sales_sparse


def date_parse_stock_data(stock_sparse: pd.DataFrame) -> pd.DataFrame:
    """
    convert "from_date" and "to_date" columns to datetime type
    Args:
        stock_sparse:   dataframe

    Returns: dataframe with "from_date" and "to_date" columns in datetime type

    """
    stock_sparse[static_config.from_date_str] = pd.to_datetime(stock_sparse[static_config.from_date_str])
    stock_sparse[static_config.to_date_str] = pd.to_datetime(stock_sparse[static_config.to_date_str])
    return stock_sparse


def generate_sku_store_sales_stock(sku_store: str, sales_sparse: pd.DataFrame, stock_sku_store: pd.DataFrame,
                                   freq) -> tuple:
    """
    generate sales and stock data for each sku_store
    Args:
        sku_store:  sku_store id
        sales_sparse:   dataframe
        stock_sku_store:    dataframe
        freq:   frequency of the data

    Returns:    dataframe with sales and stock data for each sku_store

    """
    df_sku_store_sales_stock = pd.DataFrame()
    for row in stock_sku_store.iterrows():
        df = pd.DataFrame()
        df[static_config.date_str] = pd.date_range(row[1][static_config.from_date_str],
                                                    row[1][static_config.to_date_str], freq=freq)
        df[static_config.sku_store_str] = sku_store
        df[static_config.stock_str] = row[1][static_config.stock_str]
        df_sku_store_sales_stock = pd.concat([df_sku_store_sales_stock, df])
    sales_sku_store = sales_sparse[sales_sparse[static_config.sku_store_str] == sku_store]
    return sales_sku_store, df_sku_store_sales_stock


def filter_data_sku_store_and_start_date(stock_sparse: pd.DataFrame, sku_store: str, start_date: str) -> pd.DataFrame:
    """
    filter data by sku_store and start_date
    Args:
        stock_sparse: dataframe with the following columns: [sku_store, from_date, to_date, stock]
        sku_store: str of sku_store
        start_date: str of start_date

    Returns: dataframe with the following columns: [sku_store, from_date, to_date, stock] filtered by sku_store and
    start_date

    """
    df = stock_sparse[(stock_sparse[static_config.sku_store_str] == sku_store) & (
            stock_sparse[static_config.from_date_str] >= start_date)]
    return df


def merge_sales_and_stock(sales_sku_store: pd.DataFrame, df_sku_store_sales_stock: pd.DataFrame) -> pd.DataFrame:
    """
    merge sales and stock data
    Args:
        sales_sku_store: dataframe with the following columns: [date, sales]
        df_sku_store_sales_stock: dataframe with the following columns: [date, sku_store, stock]

    Returns:
        dataframe with the following columns: [date, sku_store, sales, stock]

    """
    df_sku_store_sales_stock = df_sku_store_sales_stock.merge(sales_sku_store[[static_config.date_str,
                                                                               static_config.sales_str]],
                                                              on=static_config.date_str, how='left').fillna(0)
    return df_sku_store_sales_stock


def generate_relevant_sku_stock_in_stock_interval_time(sales_sparse: pd.DataFrame, stock_sparse: pd.DataFrame,
                                                       start_date_of_interval:str) -> list:
    """
    generate relevant sku_stores in stock interval time
    Args:
        sales_sparse: df with the following columns: [date, sku_store, sales]

        stock_sparse: df with the following columns: [sku_store, from_date, to_date, stock]

    Returns: list of relevant sku_stores in stock interval time

    """
    relevant_sku_stock_in_stock_interval_time = sales_sparse[(sales_sparse[static_config.sku_store_str]
                                                              .isin(
        stock_sparse[(stock_sparse[static_config.to_date_str]
                      > pd.to_datetime(start_date_of_interval)) &
                     (stock_sparse[static_config.stock_str] >
                      0)][static_config.sku_store_str]
        .unique()))][static_config.sku_store_str].unique()
    return relevant_sku_stock_in_stock_interval_time


def handle_big_base_stock(train: pd.DataFrame, threshold) -> int:
    """
    calculate base stock for big base stock value sku_stores
    Args:
        train:  dataframe with the following columns: [date, sku_store, 3_days_sales, stock]
        threshold:  float

    Returns:   base stock value

    """
    max_3_days_sales_train = max(train[static_config.three_days_sales_str].fillna(0))
    residual = train[static_config.stock_str] - train[static_config.three_days_sales_str]
    min_residual = residual.min()
    if min_residual < 0:
        min_residual = 0
    base_stock = np.ceil(max_3_days_sales_train + min_residual * threshold)
    return base_stock


def filter_relevant_ids(sales_data: pd.DataFrame, stock_data: pd.DataFrame, relevant_ids_json_path: str) -> tuple:
    """
    filter relevant ids from sales and stock data
    Args:
        sales_data: dataframe with the following columns: [date, sku_store, sales]
        stock_data: dataframe with the following columns: [sku_store, from_date, to_date, stock]
        relevant_ids_json_path: str of relevant ids json path

    Returns:    dataframe with the following columns: [date, sku_store, sales] filtered by relevant ids,
                dataframe with the following columns: [sku_store, from_date, to_date, stock] filtered by relevant ids

    """
    with open(relevant_ids_json_path, 'r') as f:
        relevant_ids = json.load(f)
    sales_data = sales_data[sales_data[static_config.sku_store_str].isin(relevant_ids)]
    stock_data = stock_data[stock_data[static_config.sku_store_str].isin(relevant_ids)]
    return sales_data, stock_data

def rename_and_filter_relevant_columns(sales_sparse: pd.DataFrame, stock_sparse: pd.DataFrame) -> tuple:
    """
    rename and filter relevant columns and replace "2099-12-31" with today's date
    Args:
        sales_sparse:  dataframe with the following columns: [outlet, mat_no, quantity, date]
        stock_sparse: dataframe with the following columns: [bwkey, matnr, valid_from_date, valid_to_date, lbkum]

    Returns: dataframe with the following columns: [store, sku, sales, date], dataframe with the following columns:
    [store, sku, stock, from_date, to_date]
    """
    sales_sparse.rename({'outlet': static_config.store_str, 'quantity': static_config.sales_str, 'mat_no': static_config.sku_str}, axis=1, inplace=True)
    sales_sparse = sales_sparse[[static_config.store_str, static_config.sku_str, static_config.sales_str, static_config.date_str]]
    stock_sparse.rename(
        {'bwkey': static_config.store_str, 'matnr': static_config.sku_str, 'valid_to_date': static_config.to_date_str,
         'valid_from_date': static_config.from_date_str,
         'lbkum': static_config.stock_str}, axis=1, inplace=True)
    stock_sparse = stock_sparse[[static_config.store_str, static_config.sku_str,
                                 static_config.stock_str, static_config.from_date_str, static_config.to_date_str]]
    return sales_sparse, stock_sparse