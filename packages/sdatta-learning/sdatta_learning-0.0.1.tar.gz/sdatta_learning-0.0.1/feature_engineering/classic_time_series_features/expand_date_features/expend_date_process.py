import pandas as pd
from src.feature_engineering.classic_time_series_features.expand_date_features import config
from configs import global_static_config as static_config


class ExpandDateFeatureGenerator:
    def __init__(self, list_of_columns_expand_date):
        self.list_of_columns_expand_date = list_of_columns_expand_date
        self.day_str = config.day_str
        self.month_str = config.month_str
        self.year_str = config.year_str
        self.day_of_week_str = config.day_of_week_str
        self.week_of_year_str = config.week_of_year_str
        self.quarter_str = config.quarter_str
        self.day_of_year_str = config.day_of_year_str
        self.name_of_day_str = config.name_of_day_str
        self.day_of_the_month_str = config.day_of_the_month_str
        self.is_weekend_c_str = config.is_weekend_c_str
        self.is_weekend_j_str = config.is_weekend_j_str


    def expand_data_by_date(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Expend the data by date.

        Args:
            df: The dataframe to expend.

        Returns:
            The expended dataframe.

        *Note:
            Dataframe must have columns: store, item, date, sales.
        """
        df[static_config.date_str] = pd.to_datetime(df[static_config.date_str])
        df = df.set_index(static_config.date_str)
        if self.day_str in self.list_of_columns_expand_date:
             df[self.day_str] = df.index.day
        if self.month_str in self.list_of_columns_expand_date:
             df[self.month_str] = df.index.month
        if self.year_str in self.list_of_columns_expand_date:
             df[self.year_str] = df.index.year
        if self.day_of_week_str in self.list_of_columns_expand_date:
             df[self.day_of_week_str] = df.index.dayofweek
        if self.day_of_year_str in self.list_of_columns_expand_date:
             df[self.day_of_year_str] = df.index.dayofyear
        if self.name_of_day_str in self.list_of_columns_expand_date:
              df[self.name_of_day_str] = df.index.strftime("%A")
        if self.week_of_year_str in self.list_of_columns_expand_date:
              df[self.week_of_year_str] = df.index.isocalendar().week.apply(int)
        if self.quarter_str in self.list_of_columns_expand_date:
              df[self.quarter_str] = df.index.quarter
        if self.day_of_the_month_str in self.list_of_columns_expand_date:
              df[self.day_of_the_month_str] = df.index.days_in_month
        if self.is_weekend_c_str in self.list_of_columns_expand_date:
              df[self.is_weekend_c_str] = df[self.day_of_week_str].apply(lambda x: 1 if x in [5, 6] else 0)
        if self.is_weekend_j_str in self.list_of_columns_expand_date:
              df[self.is_weekend_j_str] = df[self.day_of_week_str].apply(lambda x: 1 if x in [4, 5] else 0)
        df = df.reset_index()
        return df