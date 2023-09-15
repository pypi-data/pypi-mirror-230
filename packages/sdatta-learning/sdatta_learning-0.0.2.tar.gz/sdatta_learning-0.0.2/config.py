class Config:
    def __init__(self, **kwargs):
        self.config = {}
        self.update_config(**kwargs)
        self.defaults = {}

        # Set default values
        self.set_defaults()

    def set_defaults(self):
        """
        Set default values for the configuration.
        This method can be overridden in subclasses to define static default values.
        """
        pass

    def update_config(self, **kwargs):
        """
        Update the configuration with the provided values.
        This method can be overridden in subclasses to add custom logic for dynamic configuration updates.
        """
        for key, value in kwargs.items():
            if isinstance(value, dict):
                if key not in self.config or not isinstance(self.config[key], Config):
                    self.config[key] = Config(**value)
                else:
                    self.config[key].update_config(**value)
            else:
                self.config[key] = value

    def get_config(self):
        return self.config

    def get_param(self, param_name):
        keys = param_name.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, Config):  # If the value is a Config object, access its underlying dictionary
                value = value.config
            if key in value:
                value = value[key]
            else:
                return self.defaults.get(param_name)  # Return default value if parameter not found
        return value

    def set_param(self, param_name, param_value):
        keys = param_name.split('.')
        current_config = self.config
        for key in keys[:-1]:
            if key not in current_config or not isinstance(current_config[key], Config):
                current_config[key] = Config()
            current_config = current_config[key].config  # Access the underlying dictionary
        current_config[keys[-1]] = param_value

    def remove_param(self, param_name):
        keys = param_name.split('.')
        current_config = self.config
        for key in keys[:-1]:
            if key not in current_config or not isinstance(current_config[key], Config):
                return
            current_config = current_config[key].config  # Access the underlying dictionary
        if keys[-1] in current_config:
            del current_config[keys[-1]]


class MyConfig(Config):
    def __init__(self, **kwargs):
        self.global_config = {}
        super().__init__(**kwargs)

    def update_config(self, **kwargs):
        for key, value in kwargs.items():
            self.global_config[key] = value
        super().update_config(global_config=self.global_config)
    def set_defaults(self):
        self.defaults = {
    'feature_engineering_configs': {
        "classic_time_series_features_configs": {
            'cumulative_features_config': {
                "normalized_date_col": "normalized_date"
            },
            'expand_date_features': {
                'day_str': 'day',
                'month_str': 'month',
                'year_str': 'year',
                'day_of_week_str': 'day_of_week',
                'day_of_year_str': 'day_of_year',
                'name_of_day_str': 'name_of_day',
                'week_of_year_str': 'week_of_year',
                'quarter_str': 'quarter',
                'day_of_the_month_str': 'day_of_the_month',
                'is_weekend_c_str': 'is_weekend_c',
                'is_weekend_j_str': 'is_weekend_j'
            }
        },
        "encoders_features_configs": {
            'item_store_sales_encoder_features_config': {
                'encoders_str': 'encoders',
                'category_str': 'category',
                'X_columns_types_str': 'X_columns_types'
            }
        },
        "event_features_configs": {
            "item_store_sales_encoder_features_config": {
                "max_date_str": 'max_date',
                "min_date_str": 'min_date',
                "date_min_col_list_str": "min_date_list",
                "holiday_col": "holiday_name",
                "holiday_col_type": "type",
                "duration_list_col": "duration_list",
                "event_num": 'num_event_id_list',
                "event_col_even": "event_id_list",
                "trend_col": 'rolling_7_mean',
                "event_col_list": ["event_id_list", "sub_event_id_list"],
                "type_functions": ["mean", "std", "median"],
                "duration_list_cols_str": ['duration_list_mean_event', 'duration_list_median_event'],
                "weekend_col": "is_weekend",
                "column_list_map_id": ['event_id', 'duration', 'min_date', 'sub_event_id', 'is_old', "max_date"],
                "cols_to_encode": ["type_holiday_name", "num_sub_event_id_list", "cumulative_sum_sales", "PC1", "PC2",
                                   "comments", "fft_real", "fft_imag", "num_event_id_list", "duration_list_mean_event",
                                   "duration_list_median_event", "duration_list_std_event", 'is_weekend',
                                   "ind_change_combo_event", 'is_sunday', 'is_tomorrow_event', "is_2_days_event"],
                "cols_to_encode_at_once": ["num_sub_event_id_list", "num_event_id_list", "PC1", "PC2", "fft_real",
                                           "fft_imag", "cumulative_sum_sales", "duration_list_mean_event",
                                           "duration_list_std_event", "duration_list_median_event", 'is_tomorrow_event',
                                           "is_2_days_event"],
                "cols_days_for_interaction": ['day_of_week', 'week_of_year', 'quarter', 'is_weekend',
                                              "ind_change_combo_event", 'is_sunday', "is_holday"],
                "type_encoder_list": ["MEstimateEncoder", "CatBoostEncoder"],
                "year_str": 'year',
                "month_str": 'month',
                "day_str": 'day',
                "day_of_week_str": 'day_of_week',
                "week_of_year_str": 'week_of_year',
                "quarter_str": 'quarter',
                "is_weekend_str": 'is_weekend'
            }
        },
        "outsource_data_configs": {
            "weather_features_configs": {
                "max_date_str": 'max_date',
                "min_date_str": 'min_date',
                "date_min_col_list_str": "min_date_list",
                "latitude_str": 'latitude',
                "longitude_str": 'longitude',
                "store_id_str": 'store_id',
                "strptime_format": '%Y-%m-%d',
                "tavg_str": 'tavg',
                "tmin_str": 'tmin',
                "tmax_str": 'tmax',
                "prcp_str": 'prcp',
                "snow_str": 'snow',
                "wspd_str": 'wspd',
                "pres_str": 'pres',
                "tsun_str": 'tsun',
                "linear_str": 'linear',
                "outside_str": 'outside',
                "weather_cols_to_drop": ["tsun", "pres"],
                "weather_columns": ['tavg', 'tmin', 'tmax', 'prcp', 'snow', 'wspd']
            }
        }
    }
}



        for key, value in self.defaults.items():
            if key not in self.config:
                self.config[key] = value

config = MyConfig(Unnamed_0_col = "Unnamed: 0",
                    sales_str = "sales",
                    date_str = "date",
                    item_store_str = "item, store",
                    item_str = "item",
                    store_str = "store",
                    sku_store_str = 'sku, store',
                    sku_str = 'sku',
                    id_str = 'id',
                    index_str = 'index',
                    outlet_str = 'outlet',
                    mat_no_str = 'mat_no',
                    quantity_str = 'quantity',
                    left_str = 'left',
                    test_str = 'test',
                    val_str = 'val',
                    mae_str = 'MAE',
                    mse_str = 'MSE',
                    palmers_week_str = 'Palmers Week',
                    from_date_str = 'from_date',
                    to_date_str = 'to_date',
                    item_name_str = 'item_name',
                    three_days_sales_str = '3_days_sales',
                    stock_str = 'stock')
full_config = config.get_config()
print(full_config)

