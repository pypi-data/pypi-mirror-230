from src.feature_engineering.event_features.global_event_features.global_event_features_process import EventFeatureGenerator
from src.utils import *
from src.feature_engineering.event_features.global_event_features.global_event_features_process import config
from configs import global_static_config as static_config


def preprocess_part_1(event_preprocess: EventFeatureGenerator,
                      data_sales_process1_1: pd.DataFrame,
                      data_event: pd.DataFrame):
    """
    preprocess part 1 for event features pipeline
    Args:
        event_preprocess:   EventFeatureGenerator
        data_sales_process1_1:  pd.DataFrame - data_sales_process1_1
        data_event:  pd.DataFrame - data_event

    Returns: data_sales_process10

    """
    data_event_process = event_preprocess.calculate_duration(data_event)
    data_sales_process2 = event_preprocess.identify_event(data_event_process, data_sales_process1_1)
    data_sales_process3 = event_preprocess.map_event_to_list(data_sales_process2, data_event_process,
                                                             config.column_list_map_id, static_config.date_str)
    data_sales_process4 = event_preprocess.add_stat_durations(data_sales_process3, config.duration_list_col)
    data_sales_process5 = event_preprocess.length_list_event(data_sales_process4, config.event_col_list)
    data_sales_process6 = event_preprocess.diff_col(data_sales_process5, static_config.sales_str,
                                                    static_config.date_str)
    data_sales_process7 = event_preprocess.event_frequency(data_sales_process6, static_config.date_str, config.event_num)
    data_sales_process8 = event_preprocess.indicate_event_combination_change(data_sales_process7, config.event_col_even)
    data_sales_process10 = event_preprocess.log_col(data_sales_process8)
    return data_sales_process10


def preprocess_part_2(event_preprocess: EventFeatureGenerator,
                      data_sales_process10: pd.DataFrame,
                      data_hol: pd.DataFrame):
    """
    preprocess part 2 for event features pipeline
    Args:
        event_preprocess:  EventFeatureGenerator
        data_sales_process10:  pd.DataFrame - data_sales_process10
        data_hol:  pd.DataFrame - data_hol

    Returns: data_sales_process27

    """
    data_sales_process11 = event_preprocess.calcuate_amount_days_pass_from_start_of_event(data_sales_process10,
                                                                                          static_config.date_str,
                                                                                          config.date_min_col_list_str)
    data_sales_process12 = event_preprocess.calcuate_amount_days_pass_from_start_of_event_most_new(data_sales_process11,
                                                                                                   config.date_min_col_list_str,
                                                                                                   static_config.date_str)
    data_sales_process13 = event_preprocess.merge_df(data_sales_process12, data_hol, static_config.date_str)
    data_sales_process14 = event_preprocess.identify_date_occasion(data_sales_process13, config.holiday_col,
                                                                   static_config.date_str)
    data_sales_process15 = event_preprocess.feature_combine_str(data_sales_process14, config.holiday_col_type, config.holiday_col)
    data_sales_process16 = event_preprocess.add_cumulative_sum_column_for_targe(data_sales_process15,
                                                                                static_config.sales_str)
    data_sales_process17 = event_preprocess.fft_features(data_sales_process16, static_config.sales_str)
    data_sales_process18 = event_preprocess.time_series_shape_features(data_sales_process17, static_config.sales_str)
    data_sales_process21 = event_preprocess.convert_str_indicator(data_sales_process18, config.weekend_col)
    return data_sales_process21


def preprocess_part_3(event_preprocess: EventFeatureGenerator,
                      data_sales_process21: pd.DataFrame
                      , year_forecast: int
                      , pca_num : int, task):
    """
    preprocess part 3 for event features pipeline
    Args:
        event_preprocess:  EventFeatureGenerator
        data_sales_process21:  pd.DataFrame - data_sales_process21
        year_forecast: year forecast
        pca_num: pca components number
        task:  task of clearml

    Returns:

    """
    data_sales_process22 = event_preprocess.extract_features_pca(data_sales_process21, static_config.date_str,
                                                                 year_forecast, pca_num,
                                                                 static_config.sales_str, task=task)
    data_sales_process23 = event_preprocess.process_next_days_events(data_sales_process22, static_config.sales_str)
    data_sales_process24 = event_preprocess.apply_encodings(data_sales_process23, config.type_encoder_list, config.cols_to_encode,
                                                            static_config.sales_str, year_forecast)
    print(event_preprocess.encoders_dict.keys())
    data_sales_process25 = event_preprocess.apply_encodings_at_once(data_sales_process24, config.type_encoder_list,
                                                                    config.cols_to_encode, static_config.sales_str,
                                                                    year_forecast=year_forecast,task=task)
    data_sales_process26 = event_preprocess.columns_interactions_encoder(data_sales_process25, config.cols_to_encode_at_once,
                                                                         config.cols_days_for_interaction,
                                                                         static_config.sales_str,
                                                                         config.type_encoder_list, year_forecast, task=task)
    data_sales_process27 = event_preprocess.remove_expend_dates(data_sales_process26)
    encoders_dict = event_preprocess.encoders_dict
    return data_sales_process27, encoders_dict


def run_pipline_global_events_fit_and_transform(data_event, data_sales, data_hol, inference_bool=False,
                                global_event_features_config_dict=None, encoders_dict=None, task=None):
    """
    This function is the main function of the event feature process pipeline
    , it is responsible for the entire process of the event feature process pipeline.
    Args:
        data_event: The event data frame.
        data_sales: The sales data frame.
        data_hol: The holiday data frame.
        inference_bool: inference mode.
        task: The task object.
    return:
        data_final_event: The data frame after the event feature process pipeline.
    """
    event_preprocess = EventFeatureGenerator(inference_bool=inference_bool, encoders_dict=encoders_dict,
                                             global_event_features_config_dict=global_event_features_config_dict)
    data_sales_process1 = aggregate_data_by_date(data_sales)
    data_sales_process1_1 = event_preprocess.process_date_column(data_sales_process1, static_config.date_str)
    year_forecast = find_max_year(data_sales_process1_1)
    data_sales_process10 = preprocess_part_1(event_preprocess, data_sales_process1_1, data_event)
    data_sales_process21 = preprocess_part_2(event_preprocess, data_sales_process10, data_hol)
    data_sales_process27, encoders_dict = preprocess_part_3(event_preprocess, data_sales_process21, year_forecast, event_preprocess.pca_num, task)
    object_columns = data_sales_process27.select_dtypes(include=['object']).columns
    data_sales_process27 = data_sales_process27.drop(object_columns, axis=1)
    data_sales_process27 = data_sales_process27.drop(columns=[static_config.sales_str])
    data_final_event = data_sales_process27.copy()
    return data_final_event, encoders_dict


