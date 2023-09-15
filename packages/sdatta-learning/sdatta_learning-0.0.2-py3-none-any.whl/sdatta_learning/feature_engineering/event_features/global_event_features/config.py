from category_encoders import MEstimateEncoder, CatBoostEncoder


max_date_str = 'max_date' # max date column name
min_date_str = 'min_date' # min date column name
date_min_col_list_str = "min_date_list" # min date list column name
holiday_col = "holiday_name" # holiday column name
holiday_col_type = "type" # holiday type column name
duration_list_col = "duration_list" # duration list column name
event_num = 'num_event_id_list' # number of events column name
event_col_even = "event_id_list" # event column name
trend_col = 'rolling_7_mean' # trend column name
event_col_list = ["event_id_list", "sub_event_id_list"] # list of event columns
type_functions = ["mean", "std", "median"] # list of functions to calculate the statistics on
duration_list_cols_str = ['duration_list_mean_event', 'duration_list_median_event'] # list of duration list columns
weekend_col = "is_weekend" # weekend column name
column_list_map_id = ['event_id', 'duration', 'min_date',  'sub_event_id', 'is_old', "max_date"]
cols_to_encode = ["type_holiday_name", "num_sub_event_id_list", "cumulative_sum_sales", "PC1", "PC2", "comments",
                  "fft_real", "fft_imag", "num_event_id_list", "duration_list_mean_event",
                  "duration_list_median_event",
                  "duration_list_std_event", 'is_weekend',
                  "ind_change_combo_event", 'is_sunday','is_tomorrow_event',"is_2_days_event"]  # list of columns to encode
cols_to_encode_at_once = ["num_sub_event_id_list", "num_event_id_list", "PC1",
                          "PC2", "fft_real", "fft_imag", "cumulative_sum_sales", "duration_list_mean_event",
                          "duration_list_std_event",
                          "duration_list_median_event",'is_tomorrow_event',"is_2_days_event"] # list of columns to encode at once
cols_days_for_interaction = ['day_of_week', 'week_of_year', 'quarter', 'is_weekend', "ind_change_combo_event",
                            'is_sunday', "is_holday"] # list of columns to create interaction with
type_encoder_list = ["MEstimateEncoder", "CatBoostEncoder"] # list of encoders to use
year_str = 'year' # year column name
month_str = 'month' # month column name
day_str = 'day' # day column name
day_of_week_str = 'day_of_week' # day of week column name
week_of_year_str = 'week_of_year' # week of year column name
quarter_str = 'quarter' # quarter column name
is_weekend_str = 'is_weekend' # is weekend column name