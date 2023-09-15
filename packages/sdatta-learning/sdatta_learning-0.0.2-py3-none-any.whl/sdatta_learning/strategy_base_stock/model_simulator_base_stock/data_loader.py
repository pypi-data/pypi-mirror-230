import pandas as pd
from clearml import Dataset
from configs import global_static_config as static_config



class DataSetLoader():
    def __init__(self, dataset_project, dataset_name, tags=None, lazy_load=True, dataset_file_names=['sales_no_sparse_raw.csv']):
        """
        This class is used to load the data from the dataset
        Args:
            dataset_project: the dataset project name
            dataset_name: the dataset name
            tags: the tags of the dataset
            lazy_load: if True, the data will be loaded only when the load function is called
            dataset_file_names: the names of the files in the dataset
        """
        self.tags = tags
        self.data_path = None if lazy_load else self.load()
        self.dataset_project = dataset_project
        self.dataset_name = dataset_name
        self.dataset_file_names = dataset_file_names

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

    def load_data(self):
        """
        Load the data from the dataset and return a dataframe
        the function applies a simple processing to the data
        and load in the format of sku, store, date, sales
        Returns:

        """
        data_load = load_data_from_dataset(dataset_project=self.dataset_project, dataset_names=self.dataset_name,
                                           dataset_file_names=self.dataset_file_names)
        data = data_load[self.dataset_file_names[0]]
        data[static_config.date_str] = pd.to_datetime(data[static_config.date_str])
        data[static_config.sales_str] = data[static_config.sales_str].astype(float)

        return data

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