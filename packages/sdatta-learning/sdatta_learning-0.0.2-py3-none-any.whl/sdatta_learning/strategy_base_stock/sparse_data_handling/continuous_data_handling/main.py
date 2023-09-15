from sparse_data_handling.production_1.src.loader import df_from_dataset_clearml
from sparse_data_handling.production_2 import project_config, static_config
import warnings
import json
warnings.filterwarnings("ignore")
from sparse_data_handling.production_2.utils import *
def load_data():
    sales_data = pd.read_csv(
        '/Users/guybasson/Desktop/Palmers/palmers/sparse_data_handling/research/sparse_sales_for_august_23_fit.csv')
    stock_data = pd.read_csv(
        '/Users/guybasson/Desktop/Palmers/palmers/sparse_data_handling/research/sparse_stock_for_august_23_fit.csv')
    seasonal_items = df_from_dataset_clearml(project_config.seasonal_items_dataset_name, project_config.dataset_project,
                                             project_config.seasonal_items_file_name)
    return sales_data, stock_data, seasonal_items

def preprocess_sales_and_stock_data(sales_data, stock_data):
    sales_data = sales_data.groupby(['mat_no', 'outlet', static_config.date_str]).sum().reset_index()
    sales_data = sales_data.rename(columns={'quantity': 'sales'})
    sales_data[static_config.date_str] = pd.to_datetime(sales_data[static_config.date_str])
    max_sales_date = sales_data[static_config.date_str].max().strftime('%Y-%m-%d')
    stock_data = stock_data.replace({'2099-12-31': max_sales_date})



    stock_data['valid_from_date'] = pd.to_datetime(stock_data['valid_from_date'])
    stock_data['valid_to_date'] = pd.to_datetime(stock_data['valid_to_date'])
    sales_data[static_config.sku_store_str] = sales_data['mat_no'].astype(str) + ', ' + sales_data['outlet'].astype(str)
    stock_data[static_config.sku_store_str] = stock_data['matnr'].astype(str) + ', ' + stock_data['bwkey'].astype(str)
    return sales_data, stock_data

def filter_relevant_items(sales_data, stock_data):
    with open('/Users/guybasson/Desktop/Palmers/palmers/sparse_data_handling/production_1/src/relevant_sparse_ids.json') as f:
        relevant_sparse_ids = json.load(f)
    sales_data = sales_data[(sales_data[static_config.sku_store_str].isin(relevant_sparse_ids))]
    stock_data = stock_data[(stock_data[static_config.sku_store_str].isin(relevant_sparse_ids))]
    return sales_data, stock_data

def filter_not_seasonal(sales_data, stock_data, seasonal_items):
    not_seasonal_sales_data = sales_data[~sales_data['mat_no'].isin(seasonal_items[static_config.item_str].unique())]
    not_seasonal_stock_data = stock_data[~stock_data['matnr'].isin(seasonal_items[static_config.item_str].unique())]
    return not_seasonal_sales_data, not_seasonal_stock_data
def find_best_params_for_not_seasonal_items_sparse_data():
    sales_data, stock_data, seasonal_items = load_data()
    sales_data, stock_data = preprocess_sales_and_stock_data(sales_data, stock_data)
    sales_data, stock_data = filter_relevant_items(sales_data, stock_data)
    not_seasonal_sales_data, not_seasonal_stock_data = filter_not_seasonal(sales_data, stock_data, seasonal_items)
    num_of_ids = not_seasonal_sales_data[static_config.sku_store_str].nunique()
    print("num_of_ids: ", num_of_ids)
    num_of_machines = 7000
    num_of_ids_per_machine = np.ceil(num_of_ids / num_of_machines)
    not_seasonal_stock_data_1 = not_seasonal_stock_data[
        (not_seasonal_stock_data[static_config.sku_store_str].isin(not_seasonal_sales_data[static_config.sku_store_str].unique()[1000:1010]))]
    df_all_data = df_date_id_sales_stock_generation(not_seasonal_sales_data, not_seasonal_stock_data_1)
    df_all_data[static_config.item_str] = df_all_data[static_config.sku_store_str].apply(lambda x: x.split(',')[0][:-3])
    df_all_data[static_config.item_str] = df_all_data[static_config.item_str].astype(int)
    tune_params_combinations = make_all_combinations(project_config.days_of_sales_agg,
                                                     project_config.percent_of_residual,
                                                     project_config.extra_stock,
                                                     project_config.min_stock)
    dict_of_sparse_data_metric = {}
    num_of_machine = 2
    i = 0
    while (i < num_of_ids_per_machine) & (i <= num_of_ids):
        index = int((num_of_machine - 1) * num_of_ids_per_machine + i)
        print(index)
        id = not_seasonal_sales_data[static_config.sku_store_str].unique()[index]
        print(i, end=' - ')
        print(id, end=' ')
        data_example = df_all_data[df_all_data[static_config.sku_store_str] == id]
        len_id = len(data_example)
        num_of_folds = int(len_id / project_config.jump_days - project_config.num_of_train_days / project_config.jump_days - project_config.num_of_val_days / project_config.jump_days) + 2
        average_sparse_data_metric = 0
        dict_of_sparse_data_metric[id] = {}
        list_of_all_combinations_results = []
        for params in tune_params_combinations:
            for i in range(num_of_folds):
                print(i, ":", end=' ')
                data_train = data_example.iloc[i * project_config.jump_days:i * project_config.jump_days + project_config.num_of_train_days]
                data_val = data_example.iloc[
                           i * project_config.jump_days + project_config.num_of_train_days:i * project_config.jump_days + project_config.num_of_train_days + project_config.num_of_val_days]
            #    print("len data_train: ", len(data_train), end=' ')
           #     print("len data_val: ", len(data_val), end=' ')
                base_stock = calculate_static_sparse_data_base_stock(data_train,
                                                                     days_of_sales_agg=params['days_of_sales_agg'],
                                                                     percent_of_residual=params['percent_of_residual'],
                                                                     extra_stock=params['extra_stock'],
                                                                     min_stock=params['min_stock'])
         #       print("base_stock: ", base_stock, end=' ')
                sparse_data_metric = calculate_sparse_data_metric(data_val, base_stock)
                average_sparse_data_metric += sparse_data_metric / num_of_folds
            # append to dict
            list_of_all_combinations_results.append({
                "days_of_sales_agg": params['days_of_sales_agg'],
                "percent_of_residual": params['percent_of_residual'],
                "extra_stock": params['extra_stock'],
                "min_stock": params['min_stock'],
                "sparse_data_metric": average_sparse_data_metric
            })
            dict_of_sparse_data_metric[id] = list_of_all_combinations_results
       #     print("average_sparse_data_metric: ", average_sparse_data_metric)
        i += 1
    best_params = find_best_params(dict_of_sparse_data_metric)
    print("num_of_ids_per_machine: ", num_of_ids_per_machine)
    return best_params


if __name__ == '__main__':
    best_params_not_seasonal = find_best_params_for_not_seasonal_items_sparse_data()
    print("best_params_not_seasonal: ", best_params_not_seasonal)