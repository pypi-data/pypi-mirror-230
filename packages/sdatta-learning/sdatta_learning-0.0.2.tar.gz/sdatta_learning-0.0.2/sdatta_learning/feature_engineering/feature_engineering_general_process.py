from src.sdatta_learning.feature_engineering.encoders_features.item_store_sales_encoder_features.item_store_sales_encoder_features_pipline import \
    sales_encoder_pipline_just_transform
from src.sdatta_learning.feature_engineering.classic_time_series_features.expand_date_features.expend_date_pipline import \
    expand_date_pipline
from src.sdatta_learning.feature_engineering.classic_time_series_features.lag_features.lag_features_pipline import \
    run_item_pipline_lags_rolling_averages_diffs_ewms, run_store_pipline_lags_rolling_averages_diffs_ewms, \
    run_id_pipline_lags_rolling_averages_diffs_ewms
from src.sdatta_learning.feature_engineering.encoders_features.item_store_sales_encoder_features.item_store_sales_encoder_features_pipline import \
    sales_encoder_pipline_fit_and_transform
from src.utils import *
from src.sdatta_learning.feature_engineering.event_features.one_hot_encoder_event_features.one_hot_encoder_event_pipeline import \
    one_hot_encoder_event_pipline
from src.sdatta_learning.feature_engineering.classic_time_series_features.cumulative_features.cumulative_features_pipline \
    import run_pipline_cumulative
from src.sdatta_learning.feature_engineering.event_features.global_event_features.global_event_features_pipeline import \
    run_pipline_global_events_fit_and_transform
from configs import global_static_config as static_config
import category_encoders as ce


class GeneralFeatureEngineeringProcess:
    def __init__(self,
                 weather_features_bool=True,
                 fill_0_in_sales_gaps_bool=False,
                 rename_palmers_columns_bool=True,
                 add_item_column_from_sku_column_bool=True,
                 add_item_store_id_column_bool=True,
                 parse_columns_bool=True,
                 take_more_than_zero_sales_bool=False,
                 sum_agg_per_item_date_store_bool=True,
                 sales_window_sum_agg_for_all_bool=True,
                 sales_window_sum_agg_just_for_y_bool=True,
                 expand_data_by_date_bool=True,
                 drop_sundays_bool=True,
                 id_lags_features_bool=True,
                 item_lags_features_bool=True,
                 store_lags_features_bool=True,
                 sales_encoder_features_bool=True,
                 one_hot_encoded_events_features_bool=True,
                 cumulative_features_bool=True,
                 global_event_features_bool=True,
                 change_sales_to_future_3_days_sales_bool=True,
                 sales_window_sum_agg_for_all=6,
                 X_columns_types_for_expand_date=['day_of_week', 'month'],
                 freq_list_of_cumulative_features=["D", "W-Mon", 'M', 'Q', 'Y'],
                 lags_features_config_dict={'lag': [1, 2, 3],
                                            'rolling': [2, 3, 4],
                                            'diff': [2, 3, 4],
                                            'ewm': [0.1, 0.5, 0.99]},
                 list_of_columns_expand_date=['day', 'month', 'year', 'day_of_week', 'day_of_year', 'week_of_year',
                                              'quarter', 'day_of_the_month', 'is_weekend_c', 'is_weekend_j'],
                 global_event_features_config_dict={"window_size_list": list(range(1, 31)),
                                                    "lags_list": list(range(1, 31)),
                                                    "pca_num": 2,
                                                    "random_state": 12,
                                                    "sigma": 1,
                                                    "encoder_class_dict": {"MEstimateEncoder": ce.MEstimateEncoder,
                                                                           "CatBoostEncoder": ce.CatBoostEncoder}},
                 item_store_sales_encoder_features_config_dict={
                     "X_columns_types_for_expand_date": ['day_of_week', 'month'],
                     "encoders_types": {'MEST': ce.m_estimate.MEstimateEncoder(),
                                        'CAT': ce.m_estimate.MEstimateEncoder()}},
                 stores_filter_for_one_machine=None):

        self.weather_features_bool = weather_features_bool
        self.fill_0_in_sales_gaps_bool = fill_0_in_sales_gaps_bool
        self.rename_palmers_columns_bool = rename_palmers_columns_bool
        self.add_item_column_from_sku_column_bool = add_item_column_from_sku_column_bool
        self.add_item_store_id_column_bool = add_item_store_id_column_bool
        self.parse_columns_bool = parse_columns_bool
        self.take_more_than_zero_sales_bool = take_more_than_zero_sales_bool
        self.sum_agg_per_item_date_store_bool = sum_agg_per_item_date_store_bool
        self.sales_window_sum_agg_for_all_bool = sales_window_sum_agg_for_all_bool
        self.expand_data_by_date_bool = expand_data_by_date_bool
        self.drop_sundays_bool = drop_sundays_bool
        self.id_lags_features_bool = id_lags_features_bool
        self.item_lags_features_bool = item_lags_features_bool
        self.store_lags_features_bool = store_lags_features_bool
        self.sales_encoder_features_bool = sales_encoder_features_bool
        self.one_hot_encoded_events_features_bool = one_hot_encoded_events_features_bool
        self.cumulative_features_bool = cumulative_features_bool
        self.global_event_features_bool = global_event_features_bool
        self.change_sales_to_future_3_days_sales_bool = change_sales_to_future_3_days_sales_bool
        self.X_columns_types_for_expand_date = X_columns_types_for_expand_date
        self.freq_list_of_cumulative_features = freq_list_of_cumulative_features
        self.lags_features_config_dict = lags_features_config_dict
        self.list_of_columns_expand_date = list_of_columns_expand_date
        self.global_event_features_config_dict = global_event_features_config_dict
        self.item_store_sales_encoder_features_config_dict = item_store_sales_encoder_features_config_dict
        self.stores_filter_for_one_machine = stores_filter_for_one_machine
        self.sales_window_sum_agg_for_all = sales_window_sum_agg_for_all

        print("weather_features_bool", weather_features_bool)
        print("fill_0_in_sales_gaps_bool", fill_0_in_sales_gaps_bool)
        print("rename_palmers_columns_bool", rename_palmers_columns_bool)
        print("add_item_column_from_sku_column_bool", add_item_column_from_sku_column_bool)
        print("add_item_store_id_column_bool", add_item_store_id_column_bool)
        print("parse_columns_bool", parse_columns_bool)
        print("take_more_than_zero_sales_bool", take_more_than_zero_sales_bool)
        print("sum_agg_per_item_date_store_bool", sum_agg_per_item_date_store_bool)
        print("sales_window_sum_agg_for_all_bool", sales_window_sum_agg_for_all_bool)
        print("sales_window_sum_agg_just_for_y_bool", sales_window_sum_agg_just_for_y_bool)
        print("expand_data_by_date_bool", expand_data_by_date_bool)
        print("drop_sundays_bool", drop_sundays_bool)
        print("id_lags_features_bool", id_lags_features_bool)
        print("item_lags_features_bool", item_lags_features_bool)
        print("store_lags_features_bool", store_lags_features_bool)
        print("sales_encoder_features_bool", sales_encoder_features_bool)
        print("one_hot_encoded_events_features_bool", one_hot_encoded_events_features_bool)
        print("cumulative_features_bool", cumulative_features_bool)
        print("global_event_features_bool", global_event_features_bool)
        print("X_columns_types_for_expand_date", X_columns_types_for_expand_date)
        print("freq_list_of_cumulative_features", freq_list_of_cumulative_features)
        print("lags_features_config_dict", lags_features_config_dict)
        print("list_of_columns_expand_date", list_of_columns_expand_date)
        print("global_event_features_config_dict", global_event_features_config_dict)
        print("item_store_sales_encoder_features_config_dict", item_store_sales_encoder_features_config_dict)
        print("stores_filter_for_one_machine", stores_filter_for_one_machine)
        print("sales_window_sum_agg_for_all", sales_window_sum_agg_for_all)


    def get_data_with_future_rows(self, regular_data_df: pd.DataFrame, begin_date: str, end_date: str):
        """
        Adds future rows to the regular data dataframe
        Args:
            regular_data_df: regular data dataframe
            begin_date: begin date of prediction
            end_date: end date of prediction
    
        Returns:
            dataframe with future rows
        notes:
        1) The names of the input columns must be the same as the global_config
        2) for now the begin_date and end_date must be the same as the prediction date but for future it can be an iterative process
        """
        unique_ids = regular_data_df[static_config.item_store_str].unique()
        print(" adding future rows")
        dfs = []
        for date in pd.date_range(begin_date, end_date):
            df = pd.DataFrame(
                {static_config.item_store_str: unique_ids, static_config.date_str: date})
            df[[static_config.item_str, static_config.store_str]] = df[
                static_config.item_store_str].str.split(", ", expand=True)
            dfs.append(df)
        future_rows = pd.concat(dfs)
        regular_data_df = regular_data_df.append(future_rows)
        return regular_data_df

    def loop_feature_generation_for_each_id(self, sales_data, encoders_dict, inference_bool=False):
        all_ids_data_with_features = pd.DataFrame()
        print(" ids:")
        for id in sales_data[static_config.item_store_str].unique():
            print(f" {id}")
            id_data = sales_data[sales_data[static_config.item_store_str] == id]
            if self.fill_0_in_sales_gaps_bool:
                id_data = fill_zero_in_sales_gaps(id_data)
            if self.drop_sundays_bool:
                id_data = drop_sundays(id_data)
            if self.sales_window_sum_agg_for_all_bool:
                id_data = sales_window_agg(id_data,
                                           window=self.sales_window_sum_agg_for_all,
                                           type_of_agg='sum',
                                           inference_bool=inference_bool)
            if self.expand_data_by_date_bool:
                id_data = expand_date_pipline(id_data, self.list_of_columns_expand_date)
            if self.id_lags_features_bool:
                lags_id_features = run_id_pipline_lags_rolling_averages_diffs_ewms(id_data, self.lags_features_config_dict)
                lags_id_features = lags_id_features.drop([static_config.date_str, static_config.item_store_str], axis=1)
                id_data = pd.concat([id_data, lags_id_features], axis=1)
            if self.sales_encoder_features_bool and self.expand_data_by_date_bool:
                X_columns_types_for_expand_date_with_id = self.X_columns_types_for_expand_date.copy()
                X_columns_types_for_expand_date_with_id.append(static_config.id_str)
                if inference_bool == True:
                    encoder_features = sales_encoder_pipline_just_transform(id_data,
                                                                            id,
                                                                            encoders_dict,
                                                                            self.item_store_sales_encoder_features_config_dict)

                else:
                    encoder_features, encoders_dict = sales_encoder_pipline_fit_and_transform(id_data,
                                                                                              id,
                                                                                              encoders_dict,
                                                                                              self.item_store_sales_encoder_features_config_dict)
                encoder_features = encoder_features.drop(X_columns_types_for_expand_date_with_id, axis=1)
                id_data = pd.concat([id_data, encoder_features], axis=1)
            if self.change_sales_to_future_3_days_sales_bool:
                future_3_days_sales = id_data[static_config.sales_str] + id_data[static_config.sales_str].shift(
                    -1) + id_data[static_config.sales_str].shift(-2)
                id_data[static_config.sales_str] = future_3_days_sales
                id_data = id_data[2:]
            all_ids_data_with_features = pd.concat([all_ids_data_with_features, id_data])
        return all_ids_data_with_features, encoders_dict

    def preprocess_for_feature_engineering(self, sales_data: pd.DataFrame):
        if self.rename_palmers_columns_bool:
            print(" renaming columns")
            sales_data = rename_palmers_sales_data_columns(sales_data)
        if self.add_item_column_from_sku_column_bool:
            print(" adding item column")
            sales_data = add_item_column_from_sku_column(sales_data)
        if self.parse_columns_bool:
            print(" parsing columns")
            sales_data = parse_columns(sales_data)
        if self.take_more_than_zero_sales_bool:
            print(" taking only sales more than zero")
            sales_data = take_more_than_zero_sales(sales_data)
        if self.sum_agg_per_item_date_store_bool:
            print(" summing sales per item, date, store")
            sales_data = sum_agg_per_item_date_store(sales_data)
        if self.add_item_store_id_column_bool:
            print(" adding item store id column")
            sales_data = add_item_store_id_col(sales_data)
        return sales_data

    def global_feature_generation(self, all_ids_data_with_features, sales_data, encoders_dict,
                                  weather_data=None, one_hot_encoded_events=None, holiday_data=None,
                                  events_data=None, inference_bool=False):
        if self.item_lags_features_bool:
            print(" adding item lags features")
            item_lags_features = run_item_pipline_lags_rolling_averages_diffs_ewms(all_ids_data_with_features,
                                                                                   self.lags_features_config_dict)
            all_ids_data_with_features = all_ids_data_with_features.merge(item_lags_features,
                                                                          on=[static_config.date_str,
                                                                              static_config.item_str],
                                                                          how=static_config.left_str)
        if self.store_lags_features_bool:
            print(" adding store lags features")
            store_lags_features = run_store_pipline_lags_rolling_averages_diffs_ewms(all_ids_data_with_features,
                                                                                     self.lags_features_config_dict)
            all_ids_data_with_features = all_ids_data_with_features.merge(store_lags_features,
                                                                          on=[static_config.date_str,
                                                                              static_config.store_str],
                                                                          how=static_config.left_str)
        if self.weather_features_bool:
            print(" adding weather features")
            all_ids_data_with_features = all_ids_data_with_features.merge(weather_data, on=[static_config.date_str,
                                                                                            static_config.store_str],
                                                                          how=static_config.left_str)
        if self.one_hot_encoded_events_features_bool:
            print(" adding one hot encoded events features")
            all_ids_data_with_features = one_hot_encoder_event_pipline(all_ids_data_with_features,
                                                                       one_hot_encoded_events)
        if self.cumulative_features_bool:
            print(" adding cumulative features")
            data_for_cumulative = all_ids_data_with_features.copy()[
                [static_config.date_str, static_config.item_store_str, static_config.sales_str]]
            cumulative_features = run_pipline_cumulative(data_for_cumulative, self.freq_list_of_cumulative_features)
            all_ids_data_with_features = all_ids_data_with_features.merge(cumulative_features,
                                                                          on=[static_config.date_str,
                                                                              static_config.item_store_str],
                                                                          how=static_config.left_str)
        if self.global_event_features_bool:
            print(" adding global event features")
            global_event_features, encoders_dict = run_pipline_global_events_fit_and_transform(events_data, sales_data,
                                                                                               holiday_data,
                                                                                               inference_bool=inference_bool,
                                                                                               encoders_dict=encoders_dict,
                                                                                               global_event_features_config_dict=self.global_event_features_config_dict)
            all_ids_data_with_features = all_ids_data_with_features.merge(global_event_features,
                                                                          on=[static_config.date_str],
                                                                          how=static_config.left_str)
        return all_ids_data_with_features, encoders_dict
