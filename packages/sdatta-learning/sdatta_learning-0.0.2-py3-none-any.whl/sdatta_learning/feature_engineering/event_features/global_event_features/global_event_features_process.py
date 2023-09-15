from typing import List
import pandas as pd
import numpy as np
from scipy.fftpack import fft
from scipy.signal import argrelextrema
from sklearn.decomposition import PCA
from src.sdatta_learning.feature_engineering.event_features.global_event_features import config
import warnings
from configs import global_static_config as static_config


class EventFeatureGenerator:
    """
    Class for generating global features event from events data.
    Attributes:
        max_date_str: The max date column name.
        min_date_str: The min date column name.
        date_str: The date column name.
        duration_list_cols_str: The duration list columns name.
        sales_str: The sales column name.
    """

    def __init__(self, inference_bool: bool = False, global_event_features_config_dict: dict = None, encoders_dict: dict = None):
        self.max_date_str = config.max_date_str
        self.min_date_str = config.min_date_str
        self.date_str = static_config.date_str
        self.duration_list_cols_str = config.duration_list_cols_str
        self.sales_str = static_config.sales_str
        self.year_str = config.year_str
        self.month_str = config.month_str
        self.day_str = config.day_str
        self.day_of_week_str = config.day_of_week_str
        self.week_of_year_str = config.week_of_year_str
        self.quarter_str = config.quarter_str
        self.is_weekend = config.is_weekend_str
        self.inference_bool = inference_bool
        self.window_size_list = global_event_features_config_dict['window_size_list']
        self.lags_list = global_event_features_config_dict['lags_list']
        self.pca_num = global_event_features_config_dict['pca_num']
        self.random_state = global_event_features_config_dict['random_state']
        self.sigma = global_event_features_config_dict['sigma']
        self.encoder_class_dict = global_event_features_config_dict['encoder_class_dict']
        self.encoders_dict = encoders_dict

    def process_date_column(self, df_sales: pd.DataFrame, date_col: str=static_config.date_str) -> pd.DataFrame:
        """
        Process date column
        Args:
            df_sales: pandas DataFrame
            date_col: name of date column
        Returns: pandas DataFrame
        """
        df_sales[date_col] = pd.to_datetime(df_sales[date_col])
        df_sales[self.year_str] = df_sales[date_col].dt.year
        df_sales[self.month_str] = df_sales[date_col].dt.month
        df_sales[self.day_str] = df_sales[date_col].dt.day
        df_sales[self.day_of_week_str] = df_sales[date_col].dt.dayofweek
        df_sales[self.week_of_year_str] = df_sales[date_col].apply(lambda x: x.isocalendar()[1])
        df_sales[self.quarter_str] = df_sales[date_col].dt.quarter
        df_sales[self.is_weekend] = df_sales[date_col].dt.dayofweek.isin([5, 6]).astype(int)
        return df_sales

    def calculate_duration(self, df_event: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the duration between two dates in a DataFrame of events.
        Args:
            df_event: A pandas DataFrame containing the event dates.


        Returns:
            A pandas DataFrame with a new 'duration' column containing the duration between the two dates.
        """
        warnings.filterwarnings("ignore")
        df_event = df_event[(df_event['event_id'] != -1)]
        df_event[self.max_date_str], df_event[self.min_date_str] = pd.to_datetime(df_event[self.max_date_str]), \
            pd.to_datetime(df_event[self.min_date_str])
        df_event['duration'] = df_event[self.max_date_str] - df_event[self.min_date_str]
        return df_event

    def identify_event(self, df_event: pd.DataFrame, df_sales: pd.DataFrame) -> pd.DataFrame:
        """
        Identify event dates in sales data and create an is_event column in sales DataFrame.

        Args:
        df_event (pd.DataFrame): DataFrame containing the event dates.
        df_sales (pd.DataFrame): DataFrame containing the sales data.
        date_col (str): Column name for date in df_sales.
        min_date (str): Column name for start event date in df_event.
        end_event_date (str): Column name for end event date in df_event.

        Returns:
        A pandas DataFrame containing the sales data with an is_event column added.
        """
        df_sales['is_event'] = 0
        for index, event in df_event.iterrows():
            mask = df_sales[self.date_str].isin(
                pd.date_range(start=event[self.min_date_str], end=event[self.max_date_str]))
            df_sales.loc[mask, 'is_event'] = 1
        return df_sales

    def get_event_id_list(self, df_temp: pd.DataFrame, row: pd.Series, col: str) -> List[str]:
        """
        Get list of event ids for a given date and event type.
        Args:
            df_temp:
            row:
            col:

        Returns:

        """
        df_event_row = df_temp[df_temp[self.date_str] == row[self.date_str]][f"{col}_list"].tolist()
        return df_event_row

    def map_event_to_list(self, df_sales: pd.DataFrame, df_event: pd.DataFrame,
                          column_list_map_id: List[str], date_col: str) -> pd.DataFrame:
        """
        Map event to list of event ids for a given date and event type.
        Args:
            df_sales:   DataFrame containing the sales data.
            df_event:   DataFrame containing the event dates.
            column_list_map_id: List of columns to map to list.

        Returns:

        """
        for col in column_list_map_id:
            temp_list = []
            for index, event in df_event.iterrows():
                dates = pd.date_range(start=event[self.min_date_str], end=event[self.max_date_str])
                for date in dates:
                    temp_list.append({date_col: date, f"{col}_list": event[col]})
            df_temp = pd.DataFrame(temp_list)
            df_sales[f"{col}_list"] = df_sales.apply(
                lambda row: EventFeatureGenerator.get_event_id_list(self, df_temp, row, col), axis=1)
            del temp_list
        return df_sales

    def add_stat_durations(self, df_sales: pd.DataFrame, duration_list_col_str: str) -> pd.DataFrame:
        """
        Adds statistical measures of the durations of events in a column of a pandas DataFrame.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the event column.

        Returns:
            pd.DataFrame: DataFrame with three new columns:
                - '{event_col}_mean_event': the mean duration of events in the event column, for each row in the
                DataFrame.
                - '{event_col}_median_event': the median duration of events in the event column, for each row in the
                DataFrame.
                - '{event_col}_std_event': the standard deviation of the duration of events in the event column, for
                each row in the DataFrame.
        """
        df_sales[f"{duration_list_col_str}_mean_event"] = df_sales.apply(lambda x: np.mean(x[duration_list_col_str]),
                                                                         axis=1)
        df_sales[f"{duration_list_col_str}_mean_event"] = df_sales[f"{duration_list_col_str}_mean_event"].dt.days
        df_sales[f"{duration_list_col_str}_median_event"] = df_sales.apply(
            lambda x: np.median(x[duration_list_col_str]),
            axis=1)
        df_sales[f"{duration_list_col_str}_median_event"] = df_sales[f"{duration_list_col_str}_median_event"].dt.days
        df_sales[f"{duration_list_col_str}_std_event"] = df_sales.apply(
            lambda x: np.std([d.total_seconds() for d in x[duration_list_col_str]]), axis=1)
        return df_sales

    def length_list_event(self, df_sales: pd.DataFrame, event_col_list: List[str]) -> pd.DataFrame:
        """
        Calculates the length of each list in a column of a pandas DataFrame, for a specified list of columns.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the event column.
            event_col_list (List[str]): The list of columns to calculate the length of.

        Returns:
            pd.DataFrame: DataFrame with a new column called 'num_{col}' for each column in event_col_list.
            These columns represent the length of each list in the corresponding event column, for each row in the DataFrame.
        """
        for col in event_col_list:
            df_sales[f"num_{col}"] = df_sales.apply(lambda x: len(x[col]), axis=1)
        return df_sales

    def diff_col(self, df_sales: pd.DataFrame, target_col: str, date_col: str) -> pd.DataFrame:
        """
        Calculates the rate of change in a column of a pandas DataFrame over time, based on a date column.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the target column.
            target_col (str): The name of the column representing the target variable.
            date_col (str): The name of the column representing the dates.

        Returns:
            pd.DataFrame: DataFrame with a new column called '{target_col}_diff'.
            This column represents the rate of change in the target column over time, based on the day-to-day difference
            in the target variable and the number of days between each row in the date column.
        """
        diff = df_sales[target_col].astype(np.int64).diff().dropna()
        days_diff = pd.to_datetime(df_sales[date_col]).dt.day.diff().dropna()
        rate_of_change = diff / days_diff
        df_sales[f"{target_col}_diff"] = rate_of_change.shift()
        df_sales[f"{target_col}_diff"] = df_sales[f"{target_col}_diff"].replace([np.inf, -np.inf], 0)
        return df_sales

    def event_frequency(self, df_sales: pd.DataFrame, date_col: str, event_num: str) -> pd.DataFrame:
        """
        Calculates the frequency of events in a pandas DataFrame, based on a specified date column and event count column.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the event column.
            date_col (str): The name of the column representing the dates.
            event_num (str): The name of the column representing the event counts ->'num_event_id_list'

        Returns:
            pd.DataFrame: DataFrame with a new column called 'event_frequency'.
            This column represents the average number of events per week, based on the event count and number of weeks in the date column.
        """
        if df_sales[date_col].dtype != 'datetime64[ns]':
            df_sales[date_col] = pd.to_datetime(df_sales[date_col])
        df_sales['event_frequency'] = (df_sales[event_num] / df_sales[date_col].dt.isocalendar().week.nunique()) \
            .shift(1).fillna(0)
        return df_sales

    def indicate_event_combination_change(self, df_sales: pd.DataFrame, event_col_even: str) -> pd.DataFrame:
        """
        Indicates whether the combination of events has changed from the previous row in a pandas DataFrame.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the event column.
            event_col_even (str): The name of the column representing the events.

        Returns:
            pd.DataFrame: DataFrame with a new column called 'ind_change_combo_event'.
            This column represents whether the combination of events in the current row is different from the previous row (1),
            or not (0).
        """
        df_sales["ind_change_combo_event"] = np.where(df_sales[event_col_even].shift() != df_sales[event_col_even], 1, 0)
        df_sales.loc[0, "ind_change_combo_event"] = 0
        return df_sales

    def log_col(self, df_sales: pd.DataFrame) -> pd.DataFrame:
        """
        Applies the natural logarithm to a specified column in a pandas DataFrame.
        but skips the operation for any zero values.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the target column.

        Returns:
            pd.DataFrame:DataFrame with a new column called '{target_col}_log'.
            This column represents the natural logarithm of the specified target column,
            except for any zero values which are left unchanged.
        """
        warnings.filterwarnings("ignore")
        df_sales[f"{self.sales_str}_log"] = np.where(df_sales[self.sales_str] == 0, 0, np.log(df_sales[self.sales_str]))
        df_sales[f"{self.sales_str}_log"] = df_sales[f"{self.sales_str}_log"].shift(1).fillna(0)
        return df_sales

    def calcuate_amount_days_pass_from_start_of_event(self, df_sales: pd.DataFrame, date_col: str,
                                                      date_min_col_list: str) -> pd.DataFrame:
        """
        Calculates the number of days that have passed since the start of an event in a pandas DataFrame.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the event column.
            date_min_col_list (str): The name of the column representing the start of the event     -> "date_min_list"
            date_col (str): The name of the column representing the dates.

        Returns:
            pd.DataFrame: DataFrame with a new column called 'amount_of_days_pass_from_start_of_event'.
            This column represents the number of days that have passed since the start of the event, for each row in the DataFrame.
        """
        df_sales["amount_of_days_pass_from_start_of_event"] = df_sales.apply(
            lambda x: np.abs(pd.to_datetime(x[date_col]) - pd.to_datetime(x[date_min_col_list])), axis=1)
        return df_sales

    def calcuate_amount_days_pass_from_start_of_event_most_new(self, df_sales: pd.DataFrame, event_col: str,
                                                               date_col: str) -> pd.DataFrame:
        """
        Calculates the number of days that have passed since the start of an event, for the most recent event in a
        pandas DataFrame.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the event column.
            event_col (str): The name of the column representing the events -> "min_date_list"
            date_col (str): The name of the column representing the dates.

        Returns:
            pd.DataFrame: DataFrame with a new column called 'amount_of_days_pass_from_start_of_event_most_new'.
            This column represents the number of days that have passed since the start of the most recent event, for
            each row in the DataFrame.
        """
        df_sales["amount_of_days_pass_from_start_of_event_most_new"] = df_sales.apply(
            lambda x: np.min(pd.to_datetime(x[date_col]) - pd.to_datetime(x[event_col])), axis=1)
        df_sales["amount_of_days_pass_from_start_of_event_most_new"] = pd.to_timedelta(
            df_sales["amount_of_days_pass_from_start_of_event_most_new"]).dt.days
        return df_sales

    def merge_df(self, df_sales: pd.DataFrame, df_holiday: pd.DataFrame, key: str) -> pd.DataFrame:
        """
        Merges two pandas DataFrames based on a common key.
        1: df1 = df_sales
        2: df2 = df_holidays
        key: 'date'

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the first set of columns.
            df_holiday (pd.DataFrame): The pandas DataFrame containing the second set of columns.
            key (str): The name of the key column to merge on.

        Returns:
            df_merge    pd.DataFrame: A new DataFrame that contains all columns from both input DataFrames, merged
            on the specified key. The merge type is left join (i.e., all rows from df1 are retained, and
            matching rows from df2 are included where available).
        """
        df_sales[key] = pd.to_datetime(df_sales[key])
        df_holiday[key] = pd.to_datetime(df_holiday[key], format="%d/%m/%Y")
        df_sales = df_sales.merge(df_holiday, on=key, how="left")
        return df_sales

    def identify_date_occasion(self, df_sales: pd.DataFrame, holiday_col: str, date_col: str) -> pd.DataFrame:
        """
        Identifies holidays in a pandas DataFrame based on a specified column.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the holiday column.
            holiday_col (str): The name of the column representing the holidays -> "holiday_name"
            date_col (str): The name of the column representing the dates -> "date"

        Returns:
            pd.DataFrame: DataFrame with a new column called 'is_holiday'. This column
            represents whether each row is a holiday (1) or not (0), based on whether the holiday column
            is null or not.
        """
        df_sales["is_holday"] = np.where(df_sales[holiday_col].isnull(), 0, 1)
        df_sales["is_sunday"] = np.where(df_sales[date_col].dt.day_name() == "Sunday", 1, 0)
        return df_sales

    def feature_combine_str(self, df_sales: pd.DataFrame, holiday_col_type: str, holiday_col: str) -> pd.DataFrame:
        """
        Combines the values of two columns in a pandas DataFrame into a new column as a string.
        col1='type',col2='holiday_name' -> 'type_holiday_name'
        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the two columns to combine.
            holiday_col_type (str): The name of the first column to combine -> "holiday_type"
            holiday_col (str): The name of the second column to combine -> "holiday_name"

        Returns:
            pd.DataFrame: DataFrame with a new column called '{col1}_{col2}'. This column
            represents the concatenation of the values of col1 and col2 as strings, separated by an underscore.
        """
        df_sales[f"{holiday_col_type}_{holiday_col}"] = df_sales[holiday_col_type].map(str) + "_" + df_sales[
            holiday_col].map(str)
        return df_sales

    def calculate_rolling_functions(self, df_sales: pd.DataFrame, target_col: str, window_size_list: List[int],
                                    type_functions: List[str]) -> pd.DataFrame:
        """
        Calculates the moving average trend for a specified column in a pandas DataFrame.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the target column.
            target_col (str): The name of the column for which to calculate the trend.
            window_size_list (int): list size of the rolling window to use when calculating the trend.
            type_functions (List[str]): The type of trend to calculate. This can be any function
                from the numpy library that can be applied to a rolling window.

        Returns:
            pd.DataFrame: DataFrame with a new column called 'trend'. This column represents
            the moving average trend of the specified target column over the rolling window.
        """
        for type_function in type_functions:
            for window_size in window_size_list:
                df_sales[f'rolling_{window_size}_{type_functions}'] = df_sales[target_col].rolling(
                    window=window_size).apply(
                    getattr(np, type_function)).shift(1).fillna(0)
        return df_sales

    def add_cumulative_sum_column_for_targe(self, df_sales: pd.DataFrame, col: str) -> pd.DataFrame:
        """
        Adds a cumulative sum column to a pandas DataFrame.
        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the target column.
            col (str): The name of the column to calculate the cumulative sum for.

        Returns:
            pd.DataFrame: DataFrame with a new column called 'cumulative_sum'. This column
            represents the cumulative sum of the specified column.
        """
        df_sales[f'cumulative_sum_{col}'] = df_sales[col].cumsum()
        df_sales[f'cumulative_sum_{col}'] = df_sales[f'cumulative_sum_{col}'].shift(1).fillna(0)
        return df_sales

    def fft_features(self, df_sales: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Extracts spectral analysis features using Fast Fourier Transform (FFT).

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the target column.
            target_col (str): The name of the column representing the target variable.

        Returns:
            pd.DataFrame: DataFrame with two new columns: 'fft_real' and 'fft_imag'.
            These columns represent the real and imaginary parts of the FFT output, respectively.
        """
        df_temp = fft(df_sales[target_col].shift(1).fillna(0).values)
        df_sales['fft_real'] = np.real(df_temp)
        df_sales['fft_imag'] = np.imag(df_temp)
        return df_sales

    def extract_trend_change(self, df_sales: pd.DataFrame, trend_col: str) -> pd.DataFrame:
        """
        Extracts trend changes in a pandas DataFrame based on peaks in a specified trend column.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the trend column.
            trend_col (str): The name of the column representing the trend -> 'rolling_7_mean'

        Returns:
            pd.DataFrame: DataFrame with a new column called 'trend_change' indicating
            trend changes. If the value in the trend column is a local maximum (peak), the value in the
            'trend_change' column will be set to 1. Otherwise, it will be set to 0.
        """
        peaks_extract = argrelextrema(np.array(df_sales[trend_col].shift(1).fillna(0).values), np.greater)
        df_sales['trend_change'] = 0
        df_sales.loc[peaks_extract[0], 'trend_change'] = 1
        return df_sales

    def time_series_shape_features(self, df_sales: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Calculates shape-based features of a time series and adds them as columns to the input dataframe.

        Args:
            df_sales (pd.DataFrame): The pandas DataFrame containing the target column.
            target_col (str): The name of the column in the input dataframe that contains the target variable.

        Returns:
            pd.DataFrame: A pandas dataframe with the same columns as the input dataframe, but with additional columns
            for the calculated shape-based features.
        """
        df_sales['skewness'] = df_sales[target_col].shift(1).fillna(0).skew()
        df_sales['kurtosis'] = df_sales[target_col].shift(1).fillna(0).kurt()
        df_sales['slope'] = np.polyfit(df_sales.index, df_sales[target_col].shift(1).fillna(0).values, 1)[0]
        return df_sales

    def add_lagged_feature_to_time_series_of_column(self, df_sales: pd.DataFrame, cols: list[str],
                                                    lags_list: List[int]) -> pd.DataFrame:
        """
        Add a lagged feature to a time series dataframe.

        Args:
            df_sales (pd.DataFrame): The input time series data as a pandas dataframe.
            cols (list[str]): The name of the column in the input dataframe that contains the target variable.
            lags_list (List[int]): A list of integers representing the lags to be added.

        Returns:
            The dataframe with the lagged feature added.


        """

        for col in cols:
            for lag in lags_list:
                df_sales[f'{col}_lag_{lag}'] = df_sales[col].shift(lag)
        return df_sales

    def convert_str_indicator(self, df_sales: pd.DataFrame, weekend_col: list[str]) -> pd.DataFrame:
        """
        Converts boolean columns in a pandas DataFrame to binary integer columns (0 or 1).
        Args:
            df_sales (pd.DataFrame): The input DataFrame.
            weekend_col (list[str]): The name of the column to be converted.

        Returns:
            The input DataFrame with the specified columns converted to binary integer format.
        """

        df_sales[weekend_col] = np.where(df_sales[weekend_col] is True, 1, 0)
        return df_sales

    def extract_features_pca(self, df_sales: pd.DataFrame, date_col: str, year_forecast: int,
                             pca_num: int, target_col: str, task=None) -> pd.DataFrame:
        """
        Perform Principal Component Analysis (PCA) on a subset of numerical columns in a DataFrame, and append the
        resulting
        principal components to the original DataFrame.

        Args:
            df_sales (pd.DataFrame): The input DataFrame.
            year_forecast (int): The year after which to exclude data from PCA analysis.
            pca_num (int): The number of principal components to retain.

        Returns:
            pd.DataFrame: The input DataFrame with additional columns corresponding to the retained principal components.
        """
        df_pca = df_sales[df_sales[date_col].dt.year < year_forecast].copy()
        pca_artifacts = {}
        df_numeric = df_pca.select_dtypes(include=[np.number])
        df_numeric = df_numeric.drop(columns=[target_col])
        df_numeric = df_numeric.drop(columns=df_numeric.select_dtypes(include='timedelta64').columns.tolist())
        df_numeric_imputed = df_numeric.fillna(0)
        if self.inference_bool is False:
            pca = PCA(n_components=pca_num)
            pca.fit(df_numeric_imputed)
            if 'global_event_encoders' not in self.encoders_dict.keys():
                self.encoders_dict['global_event_encoders'] = {}
            self.encoders_dict['global_event_encoders']['global_event_encoder_PCA_encoder'] = pca
        else:
            pca = self.encoders_dict['global_event_encoders']['global_event_encoder_PCA_encoder']
        df_setup_process = df_sales.copy()
        pca_components = pca.transform(df_setup_process[df_numeric_imputed.columns].fillna(0))
        columns_pca = [f"PC{i}" for i in range(1, pca_num + 1)]
        pca_df = pd.DataFrame(pca_components, columns=columns_pca)
        df_sales[columns_pca] = pca_df
        pca_artifacts['pca_weights'] = {'pca': pca, 'columns': df_numeric_imputed.columns.tolist(),
                                        "columns_after_apply": columns_pca}
        if task is not None:
            task.upload_artifact(artifact_object=pca_artifacts, name='pca_dict')
        return df_sales

    def process_next_days_events(self, df_sales: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Process next days events
        Args:
            df_sales:  The input DataFrame.
            target_col:  The target column name.

        Returns: The input DataFrame with additional columns corresponding to the next days events.

        """
        df_sales['is_tomorrow_event'] = df_sales['is_event'].shift(-1)
        df_sales['is_2_days_event'] = df_sales['is_event'].shift(-2)
        df_sales[target_col] = df_sales[target_col].shift(-1) + df_sales[target_col].shift(-2)
        y_process = df_sales["is_2_days_event"].dropna()
        df_sales_next = df_sales.loc[y_process.index]
        return df_sales_next

    def apply_encodings(self, df_sales: pd.DataFrame, type_encoder_list: List[str], cols_to_encode: List[str],
                        target_col: str, year_forecast: int, sigma=1, random_state=12) -> pd.DataFrame:
        """
        Applies a set of target encoders to specified columns in a pandas DataFrame.

        Args:
            df_sales (pd.DataFrame): The input DataFrame.
            type_encoder_list (List[str]): A list of strings representing the type of encoder to be applied.
            cols_to_encode (List[str]): A list of strings representing the columns to be encoded.
            target_col (str): The name of the column in the input dataframe that contains the target variable.
            year_forecast (int): The year after which to exclude data from PCA analysis.
            sigma (int): The standard deviation of the normal distribution used to add noise to the encoded values.
            random_state (int): The random state to be used by the encoder.


        Returns:
            pd.DataFrame: The encoded DataFrame.
        """
        df_filtered = df_sales[df_sales.date.dt.year < year_forecast].copy()
        encoder_artifacts = {}
        for encoder_type in type_encoder_list:
            encoder_class = self.encoder_class_dict[encoder_type]
            for col in cols_to_encode:
                encoder = encoder_class(cols=[col], sigma=sigma, random_state=random_state)

                if encoder_type == "CatBoostEncoder":
                    if self.inference_bool == False:
                        encoder.fit(df_filtered[col].astype(str), df_filtered[target_col])
                        self.encoders_dict['global_event_encoders'][f'global_event_encoder_{encoder_type}_of_{col}'] = encoder

                    else:
                        encoder = self.encoders_dict['global_event_encoders'][f'global_event_encoder_{encoder_type}_of_{col}']
                        # encoder_artifacts[f'{encoder_type}_of_{col}'] = {'encoder': encoder, 'random_state': random_state,
                        #                                                  'sigma': sigma, 'columns': col,
                        #                                                  "columns_after_apply": f'{encoder_type}_of_{col}'}
                    df_sales[f'{encoder_type}_of_{col}'] = encoder.transform(df_sales[col], df_sales[target_col])
                else:
                    if self.inference_bool == False:
                        encoder.fit(df_filtered[col], df_filtered[target_col])
                        self.encoders_dict['global_event_encoders'][f'global_event_encoder_{encoder_type}_of_{col}'] = encoder
                    else:
                        encoder = self.encoders_dict['global_event_encoders'][f'global_event_encoder_{encoder_type}_of_{col}']
                   # encoder_artifacts[f'{encoder_type}_of_{col}'] = {'encoder': encoder, 'random_state': random_state,
                   #                                                  'sigma': sigma, 'columns': col,
                   #                                                  "columns_after_apply": f'{encoder_type}_of_{col}'}
                    df_sales[f'{encoder_type}_of_{col}'] = encoder.transform(df_sales[col], df_sales[target_col])
        # if task is not None:
            # task.upload_artifact(artifact_object=encoder_artifacts, name='apply_encodings_dict')
        return df_sales

    def apply_encodings_at_once(self, df_sales: pd.DataFrame, type_encoder_list: List[str], cols_to_encode: List[str],
                                target_col: str, year_forecast: int, task=None) -> pd.DataFrame:
        """
        Apply multiple category encoders to the same set of columns at once.

        Args:
            df_sales (pd.DataFrame): The input DataFrame.
            type_encoder_list (List[str]): A list of target encoders to apply to the specified columns.
            cols_to_encode (List[str]): A list of column names to encode.
            target_col (str): The name of the target column.
            year_forecast (int): The year until which to include data.
            task: The task object.



        Returns:
            pd.DataFrame: A new dataframe with the encoded columns added.
        """
        df_filtered = df_sales[df_sales.date.dt.year < year_forecast].copy()
        encoder_artifacts = {}
        for encoder_type in type_encoder_list:
            encoder_class = self.encoder_class_dict[encoder_type]
            encoder = encoder_class(cols=cols_to_encode
                                    , sigma=self.sigma
                                    , random_state=self.random_state)
            encoder_artifacts = self.condition_func_for_apply_encodings_at_once(df_sales,
                                                   encoder_type,
                                                   encoder,
                                                   df_filtered,
                                                   cols_to_encode,
                                                   target_col,
                                                   encoder_artifacts)

        if task is not None:
            task.upload_artifact(artifact_object=encoder_artifacts, name='apply_encodings_at_once')
        return df_sales

    def columns_interactions_encoder(self, df_sales: pd.DataFrame, cols_to_encode_at_once: List[str],
                                     cols_days_for_interaction: List[str], target_col: str,
                                     type_encoder_list: List[str], year_forecast: int, task=None) -> pd.DataFrame:
        """
        Apply feature interaction encoding on specified columns and then encode the new columns using a list of
        categorical encoders.

        Args:
            df_sales (pd.DataFrame): The input dataframe to be encoded.
            cols_to_encode_at_once (List[str]): A list of columns to be encoded at once.
            cols_days_for_interaction (List[str]): A list of columns to be used for feature interaction.
            target_col (str): The name of the target column to encode against.
            type_encoder_list (List[str]): A list of category encoder types to be applied ->["GLMMEncoder",
            "MEstimateEncoder","CatBoostEncoder"]
            year_forecast (int): The year forecast limit to use for training data.


        Returns:
            pd.DataFrame: A new DataFrame with feature interaction columns and encoded columns using specified
            categorical encoders.

        """
        interactions_columns = []
        for col1 in cols_to_encode_at_once:
            for col2 in cols_days_for_interaction:
                df_sales[f"{col1}_interactions_{col2}"] = df_sales[f"{col1}"] * df_sales[f"{col2}"]
                interactions_columns.append(f"{col1}_interactions_{col2}")
        df_filtered = df_sales[df_sales.date.dt.year < year_forecast].copy()
        encoder_artifacts = {}
        for encoder_type in type_encoder_list:
            encoder_class = self.encoder_class_dict[encoder_type]
            encoder = encoder_class(cols=interactions_columns, sigma=self.sigma, random_state=self.random_state)
            encoder_artifacts = self.condition_func_for_apply_encodings(df_sales, encoder_type, encoder, df_filtered,
                                                                        interactions_columns, target_col,
                                                                        encoder_artifacts, self.random_state, self.sigma)
        if task is not None:
            task.upload_artifact(artifact_object=encoder_artifacts, name='columns_interactions_encoder')
        return df_sales

    def condition_func_for_apply_encodings_at_once(self, df_sales: pd.DataFrame,
                                                   encoder_type: str,
                                                   encoder: object,
                                                   df_filtered: pd.DataFrame,
                                                   cols_to_encode: List[str],
                                                   target_col: str,
                                                   encoder_artifacts: dict) -> dict:
        """
        Apply encodings at once condition function.
        Args:
            df_sales:  dataframe to apply encodings on.
            encoder_type:  type of encoder to apply.
            encoder:  encoder object to apply.
            df_filtered:  dataframe to apply encodings on.
            cols_to_encode:   columns to apply encodings on.
            target_col:  target column to apply encodings on.
            encoder_artifacts:  dictionary to save encoder artifacts.


        Returns: dictionary with encoder artifacts.

        """
        if encoder_type == "CatBoostEncoder":
            if self.inference_bool is False:
                encoder.fit(df_filtered[cols_to_encode].astype(str), df_filtered[target_col])
                self.encoders_dict['global_event_encoders'][f'encodings_at_once_{encoder_type}'] = encoder
            else:
                encoder = self.encoders_dict['global_event_encoders'][f'encodings_at_once_{encoder_type}']
            encoded_df = encoder.transform(df_sales[cols_to_encode], df_sales[target_col])
            for col in encoded_df.columns:
                df_sales[f'{encoder_type}_of_all_{col}'] = encoded_df[col]
            keep_cols_after_apply = []
            for col in encoded_df.columns:
                keep_cols_after_apply.append(f'{encoder_type}_of_all_{col}')
            encoder_artifacts[f'{encoder_type}'] = {'encoder': encoder, 'random_state': self.random_state,
                                                    'sigma': self.sigma, 'columns': cols_to_encode,
                                                    "columns_after_apply": keep_cols_after_apply}
        else:
            if self.inference_bool is False:
                encoder.fit(df_filtered[cols_to_encode], df_filtered[target_col])
                self.encoders_dict['global_event_encoders'][f'encodings_at_once_{encoder_type}'] = encoder
            else:
                encoder = self.encoders_dict['global_event_encoders'][f'encodings_at_once_{encoder_type}']
            encoded_df = encoder.transform(df_sales[cols_to_encode], df_sales[target_col])
            for col in encoded_df.columns:
                df_sales[f'{encoder_type}_of_all_{col}'] = encoded_df[col]
            keep_cols_after_apply = []
            for col in encoded_df.columns:
                keep_cols_after_apply.append(f'{encoder_type}_of_all_{col}')
            encoder_artifacts[f'{encoder_type}'] = {'encoder': encoder, 'random_state': self.random_state,
                                                    'sigma': self.sigma, 'columns': cols_to_encode,
                                                    "columns_after_apply": keep_cols_after_apply}
        return encoder_artifacts

    def condition_func_for_apply_encodings(self, df_sales: pd.DataFrame, encoder_type: str,
                                           encoder: object,
                                           df_filtered: pd.DataFrame,
                                           interactions_columns: List[str], target_col: str,
                                           encoder_artifacts: dict,
                                           random_state: int, sigma: int) -> dict:
        """
        Apply categorical encoders condition function.
        Args:
            df_sales:  dataframe to be encoded
            encoder_type:   type of encoder to be applied
            encoder:  encoder object
            df_filtered:  filtered dataframe
            interactions_columns:  columns to be encoded
            target_col:  target column
            encoder_artifacts:  dictionary to store encoder artifacts
            random_state:  random state
            sigma:  sigma value

        Returns: dictionary with encoder artifacts

        """
        if encoder_type == "CatBoostEncoder":
            if self.inference_bool is False:
                encoder.fit(df_filtered[interactions_columns].astype(str), df_filtered[target_col])
                self.encoders_dict['global_event_encoders'][f'global_event_encoder_encodings_{encoder_type}'] = encoder
            else:
                encoder = self.encoders_dict['global_event_encoders'][f'global_event_encoder_encodings_{encoder_type}']
            encoded_df = encoder.transform(df_sales[interactions_columns], df_sales[target_col])
            keep_cols_after_apply = []
            for col in encoded_df.columns:
                keep_cols_after_apply.append(f'{encoder_type}_of_all_{col}')
            encoder_artifacts[f'{encoder_type}'] = {'encoder': encoder, 'random_state': random_state,
                                                    'sigma': sigma, 'columns': interactions_columns,
                                                    "columns_after_apply": keep_cols_after_apply}
            for col in encoded_df.columns:
                df_sales[f'{encoder_type}_of_all_{col}'] = encoded_df[col]
        else:
            if self.inference_bool is False:
                encoder.fit(df_filtered[interactions_columns], df_filtered[target_col])
                self.encoders_dict['global_event_encoders'][f'global_event_encoder_encodings_{encoder_type}'] = encoder
            else:
                encoder = self.encoders_dict['global_event_encoders'][f'global_event_encoder_encodings_{encoder_type}']
            encoded_df = encoder.transform(df_sales[interactions_columns], df_sales[target_col])
            keep_cols_after_apply = []
            for col in encoded_df.columns:
                keep_cols_after_apply.append(f'{encoder_type}_of_all_{col}')
            encoder_artifacts[f'{encoder_type}'] = {'encoder': encoder, 'random_state': random_state,
                                                    'sigma': sigma, 'columns': interactions_columns,
                                                    "columns_after_apply": keep_cols_after_apply}
            for col in encoded_df.columns:
                df_sales[f'{encoder_type}_of_all_{col}'] = encoded_df[col]
        return encoder_artifacts

    def remove_expend_dates(self, df_sales: pd.DataFrame) -> pd.DataFrame:
        """
        Remove expend dates from the dataframe.
        Args:
            df_sales: dataframe to remove expend dates from.

        Returns: dataframe without expend dates.

        """
        columns_to_check = [self.year_str, self.month_str, self.day_str, self.day_of_week_str, 'week_of_year', 'quarter']
        if all(column in df_sales.columns for column in columns_to_check):
            df_sales = df_sales.drop(columns=columns_to_check)

        return df_sales

