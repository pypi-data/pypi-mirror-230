import pandas as pd

def prepare_stock_df(stock_df: pd.DataFrame,
                        min_date: pd.DatetimeIndex,
                        max_date: pd.DatetimeIndex):
    # get the first row of stock_df and check if its matnr value starts with 3 zeroes:
    # if it does, remove the first 3 zeroes from all matnr values. if it doesn't, do nothing
    if str(stock_df.iloc[0]['matnr']).startswith('000'):
        stock_df['matnr'] = stock_df['matnr'].apply(lambda x: str(x)[3:])

    stock_df["sku, store"] = stock_df['matnr'].astype(str) + ', ' + stock_df['bwkey'].astype(str)


    stock_df['lbkum'] = stock_df['lbkum'].astype(float)
    stock_df = stock_df[stock_df['lbkum'] > 0]


    stock_df['valid_from_date'] = pd.to_datetime(stock_df['valid_from_date'])
    stock_df['valid_to_date'] = pd.to_datetime(stock_df['valid_to_date'])

    # drop rows where valid_from_date > valid_to_date
    stock_df = stock_df[~(stock_df['valid_from_date'] > stock_df['valid_to_date'])]

    # drop rows with valid_to_date before min_date
    # and change valid_from_date to min(min_date, valid_from_date)
    stock_df = stock_df[~(stock_df['valid_to_date'] < min_date)]
    stock_df['valid_from_date'] = stock_df['valid_from_date'].apply(lambda x: x if x >= min_date else min_date)

    # drop rows with valid_from_date after max_date
    # and change valid_to_date to max(max_date, valid_to_date)
    stock_df = stock_df[~(stock_df['valid_from_date'] > max_date)]
    stock_df['valid_to_date'] = stock_df['valid_to_date'].apply(lambda x: x if x <= max_date else max_date)

    return stock_df


def prepare_sales_df(sales_df, min_date, max_date):
    # date,sku,store,"sku, store",sales
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    sales_df['sales'] = sales_df['sales'].astype(float)

    #sales_df['sales'] = sales_df['sales'].apply(lambda x: 0 if x < 0 else x)

    # filter only sales between dates:
    sales_df = sales_df[(sales_df['date'] >= min_date)]
    sales_df = sales_df[(sales_df['date'] <= max_date)]

    return sales_df


def fill_sales_with_zeroes(sales_df, stock_df, min_date, max_date, id_list=None):
    # if the type of min_date or max_date is str, then convert it to datetime
    if type(min_date) == str:
        min_date = pd.to_datetime(min_date, errors='coerce')
    if type(max_date) == str:
        max_date = pd.to_datetime(max_date, errors='coerce')

    stock_df = prepare_stock_df(stock_df, min_date, max_date)
    sales_df = prepare_sales_df(sales_df, min_date, max_date)

    # filter sales and stock according to id_list
    if id_list is not None:
        sales_df = sales_df[sales_df['sku, store'].isin(id_list)]
        stock_df = stock_df[stock_df['sku, store'].isin(id_list)]


    stock_df['date'] = [pd.date_range(s, e, freq='d') for s, e in
                  zip(pd.to_datetime(stock_df['valid_from_date']),
                      pd.to_datetime(stock_df['valid_to_date']))]
    stock_df = stock_df.explode('date')

    merged_df = stock_df.merge(sales_df, left_on=['sku, store', 'date', 'bwkey', 'matnr'],
                               right_on = ['sku, store', 'date', 'store', 'sku'],
                               how='left', suffixes=('_stock', '_sales')).fillna(0)

    merged_df['sku'] = merged_df['matnr']
    merged_df['store'] = merged_df['bwkey']
    merged_df['date'] = pd.to_datetime(merged_df['date'])
    merged_df = merged_df[merged_df['date'].dt.dayofweek != 6]


    result_df = merged_df[['date', 'sku', 'store', 'sku, store', 'sales']]


    return result_df

