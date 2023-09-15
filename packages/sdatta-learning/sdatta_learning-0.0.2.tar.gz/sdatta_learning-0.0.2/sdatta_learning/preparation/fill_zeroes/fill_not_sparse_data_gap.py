
import pandas as pd
import json
from datetime import datetime, timedelta
from clearml import Task, Dataset


selected_machine = 'machine_1'

model_snapshots_path = 'azure://palmersstorageaccount.blob.core.windows.net/sdatta-analysis'
Task.add_requirements(r"C:\Users\proxyman\Downloads\requirements.txt")

task = Task.init(project_name="palmers/prod", task_name=f"prod_fill_zeros_20220101_{selected_machine}",
                 output_uri=model_snapshots_path,
                 task_type=Task.TaskTypes.custom,
                 auto_connect_frameworks=False
                 , auto_resource_monitoring=False)
task.set_base_docker("palmerscr.azurecr.io/alltrees/ubuntu22.04:1.0.0")

print('selected_machine', selected_machine)

task.execute_remotely(queue_name='ultra-high-cpu')
print('selected_machine', selected_machine)


class DataSetLoader():
    def __init__(self, dataset_project, dataset_name, tags=None, lazy_load=True):
        """
        This class is used to load the data from the dataset
        Args:
            dataset_project: the dataset project name
            dataset_name: the dataset name
            tags: the tags of the dataset
            lazy_load: if True, the data will be loaded only when the load function is called
        """
        self.tags = tags
        self.data_path = None if lazy_load else self.load()
        self.dataset_project = dataset_project
        self.dataset_name = dataset_name

    def load(self, dataset_project=None, dataset_name=None):
        """
        Load the dataset from ClearML get the local copy of the dataset
        :return: the local path of the dataset

        note:
        if dataset_project is None, the dataset_project will be the same as the project
        if dataset_name is None, the dataset_name will be the same as the name
        """
        if dataset_project is not None:
            self._set_dataset_project(dataset_project)
        if dataset_name is not None:
            self._set_dataset_name(dataset_name)
        print(f"dataset_project: {self.dataset_project}")
        print(f"dataset_name: {self.dataset_name}")
        self.data_path = Dataset.get(dataset_name=self.dataset_name,
                                     dataset_project=self.dataset_project).get_local_copy()
        return self.data_path

    @classmethod
    def _set_dataset_project(cls, dataset_project):
        cls.dataset_project = dataset_project

    @classmethod
    def _set_dataset_name(cls, dataset_name):
        cls.dataset_name = dataset_name


def load_data_from_dataset(dataset_project=None, dataset_names=None,
                           dataset_file_names=None):
    """
    This function will load the data from the dataset and return a dictionary of dataframes
    using the DataSetLoader class from clearml_architecture_item.loader module to load the data from the dataset
    Args:
        dataset_project: the dataset project name
        dataset_names: the dataset names
        dataset_file_names: the dataset file names

    Returns: a dictionary of dataframes
    """
    dfs = {}
    for dataset_name, dataset_file_name in zip(dataset_names, dataset_file_names):
        df_path = DataSetLoader(dataset_project, dataset_name).load()
        if dataset_file_name:
            dataset_file_path = df_path + '/' + dataset_file_name
            df = pd.read_csv(dataset_file_path, dtype=str)
            dfs[dataset_file_name] = df
            print(f"dataset {dataset_file_name} is loaded")
    return dfs


def load_json_from_dataset(dataset_project=None, dataset_names=None,
                           dataset_file_names=None):
    """
    This function will load the data from the dataset and return a dictionary of dataframes
    using the DataSetLoader class from clearml_architecture_item.loader module to load the data from the dataset
    Args:
        dataset_project: the dataset project name
        dataset_names: the dataset names
        dataset_file_names: the dataset file names

    Returns: a dictionary of dataframes
    """
    dfs = {}
    for dataset_name, dataset_file_name in zip(dataset_names, dataset_file_names):
        df_path = DataSetLoader(dataset_project, dataset_name).load()
        if dataset_file_name:
            dataset_file_path = df_path + '/' + dataset_file_name

            with open(dataset_file_path) as f:
                data = json.load(f)
            dfs[dataset_file_name] = data
            print(f"dataset {dataset_file_name} is loaded")
    return dfs


def load_id_set(id_path):
    with open(id_path, 'r') as f:
        id_set = json.load(f)

    return id_set

def preprocess_df_sales(df_sales: pd.DataFrame):
    df_sales = df_sales[['date', 'mat_no', 'outlet', 'quantity']].rename(columns={'mat_no': 'sku', 'outlet': 'store', 'quantity': 'sales'})
    df_sales['sales'] = df_sales['sales'].astype(int)
    df_sales[df_sales['sales'] < 0] = 0
    df_sales = df_sales.groupby(['date', 'sku', 'store'])['sales'].sum().reset_index()
    df_sales['sku']= df_sales['sku'].astype(str)
    df_sales['store'] = df_sales['store'].astype(str)
    df_sales["sku, store"] = df_sales['sku'].astype(str)+ ', ' + df_sales['store'].astype(str)

    return df_sales


def preprocess_df_stock(df_stock):
    df_stock['matnr'] = df_stock['matnr'].apply(lambda x: str(x)[3:])
    df_stock["sku, store"] = df_stock['matnr'].astype(str)+ ', ' + df_stock['bwkey'].astype(str)

    # on daily run replace with current date, on filling gap replace with the most recent one
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    df_stock['valid_to_date'] = df_stock['valid_to_date'].replace('2099-12-31', '2023-06-22') 
    df_stock['lbkum'] = df_stock['lbkum'].astype(float)

    df_stock = df_stock[df_stock['lbkum'] > 0]

    return df_stock


def fill_not_sparse_data_gap(df_stock, df_sales, id_set):
    # df_stock = preprocess_df_stock(df_stock)
    # df_sales = preprocess_df_sales(df_sales)

    not_sparse_data = df_sales[df_sales["sku, store"].isin(id_set)]
    not_sparse_data['date'] = pd.to_datetime(not_sparse_data['date'])
    not_sparse_data = not_sparse_data[not_sparse_data['date'].dt.dayofweek != 6]
    
    for id in id_set:
        df_stock_id = df_stock[df_stock["sku, store"] == id]
        zeros_date_ranges = []
    
        for _, row in df_stock_id.iterrows():
            date_range = pd.date_range(row['valid_from_date'], row['valid_to_date'])
            zeros_date_ranges.extend(date_range)
                
        sales_id_dates = df_sales[df_sales["sku, store"] == id]['date']
        zeros_date_ranges = list(set(zeros_date_ranges) - set(pd.to_datetime(sales_id_dates)))
    
        id_zeros_df = pd.DataFrame(index=zeros_date_ranges).reset_index().rename(columns={'index': 'date'})
        id_zeros_df["sku, store"] = id
        id_zeros_df['sku'] = id.split(', ')[0]
        id_zeros_df['store'] = id.split(', ')[1]
        id_zeros_df['sales'] = 0
        
        if(len(id_zeros_df.index) > 0):
            not_sparse_data = pd.concat([not_sparse_data, id_zeros_df], ignore_index=True)
    
    not_sparse_data = not_sparse_data[not_sparse_data['date'].dt.dayofweek != 6]

    a_week_ago = datetime.now() - timedelta(7)
    earliest_date = pd.to_datetime('2022-01-01')

    not_sparse_data = not_sparse_data[not_sparse_data['date'] >= earliest_date]
    
    return not_sparse_data



dataset_file_names=['prod_sales_from_20220101']
data_load = load_data_from_dataset(dataset_project='palmers/datasets', dataset_names=['prod_sales_from_20220101'],
                                    dataset_file_names=dataset_file_names)
sales_df = data_load[dataset_file_names[0]]

dataset_file_names=['prod_mbew_from_20220101_v2']
data_load = load_data_from_dataset(dataset_project='palmers/datasets', dataset_names=['prod_mbew_from_20220101_v2'],
                                    dataset_file_names=dataset_file_names)
mbew_df = data_load[dataset_file_names[0]]

dataset_file_names=['not_sparse_data.json']
data_load = load_json_from_dataset(dataset_project='palmers/datasets', dataset_names=['prod_ids'],
                                    dataset_file_names=dataset_file_names)
ids_set = data_load[dataset_file_names[0]]


machines = {
    'machine_1': [3,100, 135],
    'machine_2': [143, 144, 184, 117],
    'machine_3': [171, 172, 89, 96],
    'machine_4': [189, 216, 217, 185],
    'machine_5': [3005, 3202, 79, 88],
    'machine_6': [57, 63, 73, 74, 76],
    'machine_7': [141,123, 130, 133],
    'machine_8': [162, 167,186, 188],
    'machine_9': [4134, 44, 4906,91],
    'machine_10': [4104, 4123,226,],
    'machine_11': [119, 152,168, 22, 51],
    'machine_12': [149, 150, 4904,],
    'machine_13': [164, 166, 202, 4129, ],
    'machine_14': [175, 179, 18, ],
    'machine_15': [ 28, 29,181],
    'machine_16': [4803, 4805, 22],
    'machine_17': [3205, 3208, 136,],
    'machine_18': [214],
}


filter = [str(s) for s in machines[selected_machine]]

sales_df = preprocess_df_sales(sales_df)
mbew_df = preprocess_df_stock(mbew_df)

# print(mbew_df)
sales_df = sales_df[sales_df['store'].isin(filter)]
mbew_df = mbew_df[mbew_df['bwkey'].isin(filter)]

df = fill_not_sparse_data_gap(mbew_df, sales_df, ids_set)


task.upload_artifact(artifact_object=df, name=f'prod_not_sparse_20220101_{selected_machine}_({machines[selected_machine]})_V2')