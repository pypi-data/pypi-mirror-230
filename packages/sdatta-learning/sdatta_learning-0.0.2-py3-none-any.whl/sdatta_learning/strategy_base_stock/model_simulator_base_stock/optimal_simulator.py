from clearml import Dataset
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from configs import global_static_config as static_config



class CumulativeSumPredictor():
    """
    This class is used to predict the sales using the cumulative sum method

    The cumulative sum method is defined as follows:
    1. create a cumulative sum of the sales
    2. take the last n days of the cumulative sum
    3. take the linear regression of the last n days
    4. predict the trend of the linear regression for the next day
    """

    def __init__(self, window=7):
        """
        Args:
            window: the window size of the cumulative sum
        """
        self.window = window

    @staticmethod
    def _build_cumulative_sum(data: pd.DataFrame, sales: str = static_config.sales_str) -> pd.DataFrame:
        """
        This function build the cumulative sum of the sales

        Args:
            data: the data set
            sales: the name of the sales column

        Returns:
            the data set with the cumulative sum column
        """
        data['cumulative_sum'] = data[sales].cumsum()
        return data

    def _add_linear_reg_of_last_7_days_cum_sum(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        This function add the linear regression of the last 7 days of the cumulative sum

        Args:
            data: the data set

        Returns:
            the data set with the linear regression column
        """
        data['cumulative_sum_linear_reg'] = data['cumulative_sum'].rolling(self.window).apply(
            lambda x: np.polyfit(range(self.window), x, 1)[0], raw=True)
        return data

    def fit_predict(self, data: pd.DataFrame):
        """
        This function fit the cumulative sum model and predict the sales

        Args:
            data: the data set

        Returns:
            the cumulative_sum_linear_reg column as a list
        """
        data = self._build_cumulative_sum(data)
        data = self._add_linear_reg_of_last_7_days_cum_sum(data)
        return data['cumulative_sum_linear_reg'].tolist()


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
        # print(f"dataset_project: {self.dataset_project}")
        # print(f"dataset_name: {self.dataset_name}")
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
            # print(f"dataset {dataset_file_name} is loaded")
    return dfs


class Simulator:
    def __init__(self, horizon_forwards, horizon_backwards, dataset_project='palmers/datasets',
                 dataset_names=['sales_for_simulator'], dataset_file_names=['sales_no_sparse_raw.csv']):
        """
        This class is used to simulate the optimal stock levels
        This is the initial function of the class
        Args:
            horizon_forwards: the horizon forwards (in months)
            horizon_backwards: the horizon backwards(in years)
            dataset_project: the dataset project name
            dataset_names: the dataset names
            dataset_file_names: the dataset file names
        """
        self.optimal_stock_levels = None
        self.horizon_forwards = horizon_forwards
        self.horizon_backwards = horizon_backwards
        self.dataset_project = dataset_project
        self.dataset_names = dataset_names
        self.dataset_file_names = dataset_file_names

    # def load_data(self):
    #     """
    #     Load the data from the dataset and return a dataframe
    #     the function applies a simple processing to the data
    #     and load in the format of sku, store, date, sales
    #     Returns:
    #
    #     """
    #     data_load = load_data_from_dataset(dataset_project=self.dataset_project, dataset_names=self.dataset_names,
    #                                        dataset_file_names=self.dataset_file_names)
    #     data = data_load[self.dataset_file_names[0]]
    #     data[static_config.date_str] = pd.to_datetime(data[static_config.date_str])
    #     data[static_config.sales_str] = data[static_config.sales_str].astype(float)
    #     data = data[data[static_config.sales_str] > 0]
    #     max_date = data[static_config.date_str].max()
    #     split_date_ = max_date - pd.DateOffset(years=self.horizon_backwards, months=self.horizon_forwards)
    #     data = data[data[static_config.date_str] >= split_date_]
    #     df_all = data.groupby([SKU_column, static_config.store_str, static_config.date_str])[static_config.sales_str].sum().reset_index()
    #     return df_all


    def preprocess_data(self, data):
        """
        Load the data from the dataset and return a dataframe
        the function applies a simple processing to the data
        and load in the format of sku, store, date, sales
        Returns:

        """
        data[static_config.date_str] = pd.to_datetime(data[static_config.date_str])
        data[static_config.sales_str] = data[static_config.sales_str].astype(float)
        data[static_config.sku_store_str] = data[static_config.sku_str].astype(str) + ', ' + data[static_config.store_str].astype(str)
        data = data[data[static_config.sales_str] > 0]
        max_date = data[static_config.date_str].max()
        split_date_ = max_date - pd.DateOffset(years=self.horizon_backwards, months=self.horizon_forwards)
        data = data[data[static_config.date_str] >= split_date_]
        df_all = data.groupby([static_config.sku_str, static_config.store_str, static_config.date_str])[static_config.sales_str].sum().reset_index()
        return df_all


    def load_data_size_item_sku_store(self, df_all):
        """
        Load data from task and return a dictionary with dataset_file_name as key and dataframe as value

        Returns: dictionary with dataset_file_name as key and dataframe as value
        """

        df_all[static_config.item_str] = df_all[static_config.sku_str].astype(str).str[:-3]
        df_all[static_config.item_store_str] = df_all[static_config.item_str].astype(str) + ', ' + df_all[static_config.store_str].astype(str)
        item_to_skus = df_all.groupby(static_config.item_store_str)[static_config.sku_str].unique().apply(list).to_dict()
        sales_per_item_id_dict = df_all.groupby(static_config.item_store_str)[static_config.sales_str].sum().to_dict()
        sales_per_sku_id_dict = df_all.groupby([static_config.sku_str, static_config.store_str])[static_config.sales_str].sum().to_dict()
        res = {}
        for item_id, skus in item_to_skus.items():
            res[item_id] = {}
            item, store = item_id.split(', ')
            for sku in skus:
                res[item_id][sku] = sales_per_sku_id_dict[sku, store] / sales_per_item_id_dict[item_id]
        return res

#    @staticmethod
    # def _load_models(store):
    #     """
    #     Load models from task and return a dictionary with dataset_file_name as key and dataframe as value
    #     Args:
    #         store:  store number
    #     Returns:
    #         dictionary with dataset_file_name as key and dataframe as value
    #     """
    #     task = Task.get_task(task_id=ID_TASK_LIST).artifacts
    #     local_path = task[DICT_KEY].get_local_copy()
    #     with open(local_path, 'rb') as f:
    #         model_pkl = pickle.load(f)
    #     models = model_pkl[str(store)]
    #     return models

    @staticmethod
    def _custom_error(main_dist, sub_dist):
        """
        This function calculate the custom error between two distributions by calculating the mean of the absolute min of the difference between the two distributions.
        Args:
            main_dist:  main distribution
            sub_dist:   sub distribution
        Returns:
            the mean of the absolute min of the difference between the two distributions
        """

        res = [abs(min(0, main_dist.get(key, 0) - sub_dist.get(key, 0))) for key in main_dist.keys()]
        return np.mean(res)

    def get_matrix_dist(self, sales_of_id_data, predicted_sales_ranges, defualt_dist):
        """
        This function takes the sales of the item and the predicted sales for the item and returns the matrix of the distribution of the sales for each sku in the item id per
        each level of predicted sales.
        Args:
            sales_of_id_data:   data frame of the sales of the item, includes the columns of sku, store, item, date, sales, predicted_sales
            predicted_sales_ranges: list of predicted sales ranges
            defualt_dist:   dictionary of dictionaries, the keys are the predicted sales, the values are dictionaries of the distribution of the sales for each sku in the item id


        Returns:
                matrix_dist:    dictionary of dictionaries, the keys are the predicted sales, the values are dictionaries of the distribution of the sales for each sku in the item id
        """
        res = {}
        skus = defualt_dist.keys()
        for predicted_sales_ in predicted_sales_ranges:
            temp = sales_of_id_data[sales_of_id_data['predicted_sales'] == predicted_sales_].copy().reset_index()
            if len(temp) == 0:
                res[predicted_sales_] = defualt_dist
                continue
            sales_percentage_per_sku = temp.groupby('sku')[static_config.sales_str].sum().reset_index()
            missing_skus = set(skus) - set(sales_percentage_per_sku["sku"])
            sales_percentage_per_sku['dist'] = sales_percentage_per_sku[static_config.sales_str] / sales_percentage_per_sku[
                static_config.sales_str].sum()
            sales_percentage_per_sku = sales_percentage_per_sku.append(
                pd.DataFrame({"sku": list(missing_skus), static_config.sales_str: 0, "dist": 0}))
            res[predicted_sales_] = sales_percentage_per_sku.set_index("sku")['dist'].to_dict()
        return res

    @staticmethod
    def train_model_with_blend_rolling(y_train, y_pred, coef_non_linear=0.2, window=2):
        """
        This function blends the predicted values with the rolling average of the last 2 days of the training set
        current implementation: 0.2 * y_pred + 0.8 * rolling_average
        Args:
            y_train:    the target of the training set
            y_pred:   the predicted values of the test set
            coef_non_linear:    the coefficient of the rolling average
            window: the window of the rolling average

        Returns:
            blend_with_rolling_avg_08: the blended values
        """
        rolling_average_train = y_train.rolling(window=window).mean().shift(window).fillna(0)
        blend_with_rolling_avg_08 = [coef_non_linear * b + (1 - coef_non_linear) * r for b, r in
                                     zip(y_pred, rolling_average_train)]
        blend_with_rolling_avg_08 = np.array(blend_with_rolling_avg_08, dtype=np.float64)
        blend_with_rolling_avg_08 = pd.Series(blend_with_rolling_avg_08, index=y_train.index)
        return blend_with_rolling_avg_08

    @staticmethod
    def get_trend_model_linear_reg_cum_sum(y, window=7):
        """
        This function constructs a linear regression model on the cumulative sum of the target.
        the features for the model are the cumulative sum of the target for the last 7 days.
        Args:
            y: the target
            window: the window of the cumulative sum

        Returns:
            output from the linear regression model
        """
        model = CumulativeSumPredictor(window=window)
        return model.fit_predict(y)

    def train_model_with_blend_linear_reg_cum_sum(self, y_train, y_pred, coef_non_linear=0.2, window=7):
        """
        This function blends the predicted values with the linear regression model on the cumulative sum of the target.
        current implementation: 0.2 * y_pred + 0.8 * linear regression model on the cumulative sum of the target
        Args:
            y_train:    the target of the training set
            y_pred:   the predicted values of the test set
            coef_non_linear:    the coefficient of the rolling average
            window: the window of the rolling average

        Returns:
            blend_with_linear_reg_cum_sum_08: the blended values
        """
        linear_reg_cum_sum = self.get_trend_model_linear_reg_cum_sum(y_train, window=window)
        blend_with_linear_reg_cum_sum_08 = [coef_non_linear * b + (1 - coef_non_linear) * r for b, r in
                                            zip(y_pred, linear_reg_cum_sum)]
        blend_with_linear_reg_cum_sum_08 = np.array(blend_with_linear_reg_cum_sum_08, dtype=np.float64)
        blend_with_linear_reg_cum_sum_08 = pd.Series(blend_with_linear_reg_cum_sum_08, index=y_train.index)
        return blend_with_linear_reg_cum_sum_08

    def current_sku_data_to_dict_dist(self, predicted_sales_train, predicted_sales_, current_sku_data, dist_dict):
        """
        This function is used to get the distribution of the sku for each item in the item_list based on the total size of the item.
        filter and group the current sku data by date and calculate the mean of the sales for each date.
        then calculate the distribution of the sku for each item in the item_list based on the total size of the item.
        filter the distribution of the sku based on the predicted sales.
        convert the distribution of the sku to a dictionary.
        Args:
            predicted_sales_train:  the predicted sales of the training set
            predicted_sales_:   the predicted sales of the test set
            current_sku_data:   the data of the current sku
            dist_dict:  the distribution of the sku for each item in the item_list based on the total size of the item.

        Returns:
            fiter_data_sku_dict:    the distribution of the sku for each item in the item_list based on the total size of the item.
        """
        predicted_train_sales_filter_dates = predicted_sales_train[predicted_sales_train == predicted_sales_].index
        filter_data_sku = current_sku_data[current_sku_data[static_config.date_str].isin(predicted_train_sales_filter_dates)]
        item_total_sales = filter_data_sku[static_config.sales_str].sum()
        sku_sales_by_pred = filter_data_sku.groupby([static_config.sku_str]).agg({static_config.sales_str: 'sum'}).to_dict()
        res = {k: v / item_total_sales for k, v in sku_sales_by_pred[static_config.sales_str].items()}
        return res

    def get_score_miss_sales(self, stock_level_per_id_dict, current_sku_data, general_dist_dict):
        """
        This function is used to calculate the score of our strategy.
        Args:
            stock_level_per_id_dict (dict) - the stock level of each item in the item_list
            current_sku_data (pd.DataFrame) - the data of the current sku
            general_dist_dict:  the distribution of the sku for each item in the item_list based on the total size of the item.

        Returns: score (float) - the score of our strategy.
        """
        current_sku_data['predicted_sales'] = current_sku_data['predicted_sales'].fillna(0)
        current_sku_data['error'] = current_sku_data.apply(lambda row: np.abs(
            np.minimum(0, stock_level_per_id_dict.get(row['predicted_sales'], {}).get(row[static_config.sku_str],
                                                                                      general_dist_dict.get(
                                                                                          row[static_config.sku_str], 0)) - row[
                           static_config.sales_str])),
                                                           axis=1)
        mae = current_sku_data.groupby([static_config.sku_str]).agg({static_config.sales_str: 'sum', "error": "mean"}).reset_index()
        mae['miss_sale_error'] = mae['error'] / mae[static_config.sales_str]
        return np.mean(mae['miss_sale_error']), np.mean(mae['error'])

    @staticmethod
    def _item_process(data):
        """
        This function is used to process the item column.
        Args:
            data: the data of the current sku

        Returns:
            data: the data of the current sku
        """
        data[static_config.item_str] = data[static_config.sku_str].str[:-3]
        data[static_config.item_store_str] = data[static_config.item_str] + ', ' + data[static_config.store_str]
        return data

    def main_simulation(self, data_dist_size_item_sku_store, df_all, dict_for_model_simulator_base_stock):
        """
        This function is used to simulate the sales for each item in the item_list and return the optimal stock level for each item in the item_list based on the simulation results.
        the steps of the simulation are:
        1. Predict the sales for each item in the item_list
        2. Determine a range of potential base stock levels based on historical data
        3. Simulate sales for each stock level
        4. Use bootstrapping to estimate a confidence interval for the error
        5. Identify the stock level that minimizes the upper bound of the confidence interval
        6. Return the optimal stock level for each item in the item_list
        Args:
            data_dist_size_item_sku_store (dict) - the distribution of the sku for each item in the item_list based on the total size of the item.

        Returns: optimal_stock_levels (dict) - the optimal stock level for each item in the item_list
        """
        # init
        current_miss_sales, current_error_score, mid_optimal_stock_levels, count_id, error_length = [], [], {}, 0, []
        for item_store in dict_for_model_simulator_base_stock.keys():
            mid_optimal_stock_levels[item_store] = {}
            current_item_data = df_all[df_all[static_config.item_store_str] == item_store]
            num_of_skus = current_item_data[static_config.sku_str].nunique()


            actual_sales = dict_for_model_simulator_base_stock[item_store]['y_test_real']
            train_sales = dict_for_model_simulator_base_stock[item_store]['y_train_real']
            predicted_sales = dict_for_model_simulator_base_stock[item_store]['y_test_pred']
            predicted_sales_train = dict_for_model_simulator_base_stock[item_store]['y_train_pred']
            predicted_sales_train = self.train_model_with_blend_rolling(train_sales, predicted_sales_train)
            predicted_sales = pd.Series(predicted_sales, index=actual_sales.index)
            predicted_sales = pd.DataFrame(predicted_sales)
            predicted_sales_train = pd.DataFrame(predicted_sales_train)
            predicted_sales_train.columns = ["predicted_sales"]
            predicted_sales.columns = ["predicted_sales"]
            y_pred = pd.concat([predicted_sales_train, predicted_sales], axis=0).reset_index()
            y_pred[static_config.date_str] = pd.to_datetime(y_pred[static_config.date_str])
            current_item_data = current_item_data.merge(y_pred, on=[static_config.date_str], how='left')
            min_predicted_sales = 0
            max_predicted_sales = int(max(y_pred["predicted_sales"])) + len(
                data_dist_size_item_sku_store[item_store])
            predicted_sales_ranges = [i for i in range(min_predicted_sales, max_predicted_sales + 1)]
            matrix_dist = self.get_matrix_dist(current_item_data, predicted_sales_ranges,
                                               data_dist_size_item_sku_store[item_store])
            for predicted_sales_, dist_dict in matrix_dist.items():
                fiter_data_sku_dict = self.current_sku_data_to_dict_dist(predicted_sales_train,
                                                                         predicted_sales_,
                                                                         current_item_data, dist_dict)
                dist_weight = self._custom_error(dist_dict, fiter_data_sku_dict)
                stock_level_dict = {
                    key: np.ceil(
                        (((1 - dist_weight) * dist_dict.get(key, 0)) + (dist_weight * fiter_data_sku_dict.get(
                            key, 0))) * (predicted_sales_))
                    for key in dist_dict.keys()}
                mid_optimal_stock_levels[item_store][predicted_sales_] = stock_level_dict
            miss_sales, error_score = self.get_score_miss_sales(mid_optimal_stock_levels[item_store],
                                                                current_item_data,
                                                                data_dist_size_item_sku_store[item_store])
           # print(f"currenct miss_sales : {miss_sales}")
            current_miss_sales.append(miss_sales)
            current_error_score.append(error_score)
            count_id += 1 * num_of_skus

         # print(f"mean miss sales : {np.mean(current_miss_sales)}")
         # print(f"mean error score : {np.mean(current_error_score)}")
         # print(f"count_id : {count_id}")
         # print(f"count_error_length : {len(error_length)}")
         # print(f"error_length : {error_length}")
        return mid_optimal_stock_levels
