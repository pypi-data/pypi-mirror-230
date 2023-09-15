

def feature_engineering_for_training_pipeline(feature_engineering_process, sales_data, weather_data=None,
                                              one_hot_encoded_events=None, holiday_data=None, events_data=None,
                                              values_filter_for_one_machine=None,
                                              values_column_to_filter='store'):
    encoders_dict = {}
    sales_data = feature_engineering_process.preprocess_for_feature_engineering(sales_data=sales_data)
    if values_filter_for_one_machine is not None:
        relevant_store_sales_data = sales_data[sales_data[values_column_to_filter].astype(int).isin(values_filter_for_one_machine)]
        all_ids_data_with_features, encoders_dict = feature_engineering_process.loop_feature_generation_for_each_id(
            sales_data=relevant_store_sales_data, encoders_dict=encoders_dict)
    else:
        all_ids_data_with_features, encoders_dict = feature_engineering_process.loop_feature_generation_for_each_id(
            sales_data=sales_data, encoders_dict=encoders_dict)
    all_ids_data_with_features, encoders_dict = feature_engineering_process.global_feature_generation(
        all_ids_data_with_features=all_ids_data_with_features, sales_data=sales_data, encoders_dict=encoders_dict,
        one_hot_encoded_events=one_hot_encoded_events, holiday_data=holiday_data, events_data=events_data, weather_data=weather_data)

    # drop rows with nan in sales column
    all_ids_data_with_features = all_ids_data_with_features.dropna(subset=['sales'])
    return all_ids_data_with_features, encoders_dict





def feature_engineering_for_inference_pipeline(feature_engineering_process, sales_data, encoders_dict,
                                                  future_begin_date, future_end_date,
                                               weather_data=None, one_hot_encoded_events=None,
                                               holiday_data=None, events_data=None,
                                               values_filter_for_one_machine=None,
                                               values_column_to_filter='store'):
    sales_data = feature_engineering_process.preprocess_for_feature_engineering(sales_data=sales_data)
    sales_data = feature_engineering_process.get_data_with_future_rows(regular_data_df=sales_data,
                                                                       begin_date=future_begin_date,
                                                                       end_date=future_end_date)
    if values_filter_for_one_machine is not None:
        relevant_store_sales_data = sales_data[
            sales_data[values_column_to_filter].astype(int).isin(values_filter_for_one_machine)]
        all_ids_data_with_features, _ = feature_engineering_process.loop_feature_generation_for_each_id(
            sales_data=relevant_store_sales_data, encoders_dict=encoders_dict, inference_bool=True)
    else:
        all_ids_data_with_features, _ = feature_engineering_process.loop_feature_generation_for_each_id(
            sales_data=sales_data, encoders_dict=encoders_dict, inference_bool=True)
    all_ids_data_with_features, encoders_dict = feature_engineering_process.global_feature_generation(
        all_ids_data_with_features=all_ids_data_with_features, sales_data=sales_data, encoders_dict=encoders_dict,
        one_hot_encoded_events=one_hot_encoded_events, holiday_data=holiday_data, events_data=events_data, weather_data=weather_data,
        inference_bool=True)
    return all_ids_data_with_features
