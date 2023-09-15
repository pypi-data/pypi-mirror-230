import itertools
import numpy as np
import pandas as pd
def df_date_id_sales_stock_generation(sales_data, stock_data):
    df_all_data = pd.DataFrame()
    min_data = '2022-07-01'
    max_date = '2023-08-01'
    for id in stock_data['sku, store'].unique():

        sales_id = sales_data[(sales_data['sku, store'] == id)].set_index('date')
        stock_filtered = stock_data[(stock_data['sku, store'] == id)]
        stock_id = pd.DataFrame()
        for row in stock_filtered.iterrows():
            df_stock_sample = pd.DataFrame()
            date_from = row[1]['valid_from_date']
            date_to = row[1]['valid_to_date']
            stock = row[1]['lbkum']
            df_stock_sample['date'] = pd.date_range(date_from, date_to)
            df_stock_sample['stock'] = stock
            stock_id = stock_id.append(df_stock_sample)
        stock_id['sku, store'] = id
        id_data = stock_id.set_index('date').merge(sales_id.drop(columns=['sku, store']), how='left', left_index=True, right_index=True)
        df_all_data = df_all_data.append(id_data)
    df_all_data['sales'] = df_all_data['sales'].fillna(0)
    df_all_data = df_all_data[['sku, store', 'stock', 'sales']]
    df_all_data = df_all_data[(df_all_data.index >= min_data) & (df_all_data.index <= max_date)]
    return df_all_data




def calculate_sparse_data_metric(sales:pd.DataFrame, base_stock:pd.DataFrame, static_extra_stock_value:int=200):
    # sum_miss_sales
    base_stock_minus_sales = base_stock - sales['sales'].values
    # where base_stock_minus_sales < 0
    sum_miss_sales = np.sum(np.abs(base_stock_minus_sales[base_stock_minus_sales < 0]))
    extra_stock = np.sum(np.abs(base_stock_minus_sales - 1)) / static_extra_stock_value
    sparse_data_metric = sum_miss_sales + extra_stock
    print(f'sum_miss_sales: {sum_miss_sales}', end=' ')
    print(f'extra_stock: {extra_stock}', end=' ')
    print(f'sparse_data_metric: {sparse_data_metric}')
    return sparse_data_metric


def calculate_static_sparse_data_base_stock(data:pd.DataFrame, days_of_sales_agg:int, percent_of_residual:float, extra_stock:int, min_stock:int):
    data[f'{days_of_sales_agg}_days_sales'] = data['sales'].rolling(days_of_sales_agg).sum()
    max_sales_agg_days = data[f'{days_of_sales_agg}_days_sales'].max()
    residual = data['stock'].values - data['sales'].values
    min_residual = np.min(residual)
    # if np.ceil(max_sales_agg_days + (min_residual * percent_of_residual) + extra_stock) is 0  then it will be min_stock
    sparse_data_base_stock = np.where(np.ceil(max_sales_agg_days + (min_residual * percent_of_residual) + extra_stock) <= min_stock, min_stock, np.ceil(max_sales_agg_days + (min_residual * percent_of_residual) + extra_stock))
    return int(sparse_data_base_stock)



def make_all_combinations(days_of_sales_agg, percent_of_residual, extra_stock, min_stock):
    parameters = [days_of_sales_agg, percent_of_residual, extra_stock, min_stock]

    tune_params_combinations = []
    for combo in itertools.product(*parameters):
        combination = {
            "days_of_sales_agg": combo[0],
            "percent_of_residual": combo[1],
            "extra_stock": combo[2],
            "min_stock": combo[3]
        }
        tune_params_combinations.append(combination)
    return tune_params_combinations



def find_best_params(dict_of_sparse_data_metric:dict):
    best_params = {}
    for id in dict_of_sparse_data_metric.keys():
        for params in dict_of_sparse_data_metric[id]:
            if 'sparse_data_metric' in params.keys():
                if id not in best_params.keys():
                    best_params[id] = params
                else:
                    if params['sparse_data_metric'] < best_params[id]['sparse_data_metric']:
                        best_params[id] = params
    return best_params