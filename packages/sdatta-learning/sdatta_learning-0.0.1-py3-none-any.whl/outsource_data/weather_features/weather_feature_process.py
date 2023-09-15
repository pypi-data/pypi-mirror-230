import pandas as pd
from meteostat import Point, Daily
from datetime import datetime, timedelta
from configs import global_static_config as static_config

from src.outsource_data.weather_features import config


class WeatherFeatureGenerator:
    def __init__(self, start_date, end_date, default_latitude: float, default_longitude: float):
        self.start_date = start_date
        self.end_date = end_date
        self.default_latitude = default_latitude
        self.default_longitude = default_longitude
        self.weather_columns = config.weather_columns
        self.tavg_str = config.tavg_str
        self.tmin_str = config.tmin_str
        self.tmax_str = config.tmax_str
        self.pres_str = config.pres_str
        self.prcp_str = config.prcp_str
        self.snow_str = config.snow_str
        self.wspd_str = config.wspd_str
        self.linear_str = config.linear_str
        self.outside_str = config.outside_str
        self.latitude_str = config.latitude_str
        self.longitude_str = config.longitude_str
        self.strptime_format = config.strptime_format
        self.store_str = static_config.store_str
        self.store_id_str = config.store_id_str
        self.date_str = static_config.date_str
        self.index_str = static_config.index_str
        self.weather_cols_to_drop = config.weather_cols_to_drop


    def return_weather_daily_data_for_specific_location(self, latitude: float, longitude: float) -> pd.DataFrame:
        '''
        Retrieve daily weather data for a specific location using the Meteostat API.

        Args:
        start_date (str): A string containing the start date in the format "yyyy-mm-dd".
        end_date (str): A string containing the end date in the format "yyyy-mm-dd".
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.

        Returns:
        pd.DataFrame: A DataFrame containing the daily weather data for the specified location and date range.

        Raises:
        ValueError: If the start date is after the end date.
        '''
        start = datetime.strptime(self.start_date, self.strptime_format)
        end = datetime.strptime(self.end_date, self.strptime_format)

        point = Point(float(latitude), float(longitude))
        data = Daily(point, start, end)
        data = data.fetch()
        if self.tavg_str in data.columns:
            data[self.tavg_str].interpolate(method=self.linear_str, limit_area=self.outside_str, inplace=True)
        if self.tmin_str in data.columns:
            data[self.tmin_str].interpolate(method=self.linear_str, limit_area=self.outside_str, inplace=True)
        if self.tmax_str in data.columns:
            data[self.tmax_str].interpolate(method=self.linear_str, limit_area=self.outside_str, inplace=True)
        if self.pres_str in data.columns:
            data[self.pres_str].interpolate(method=self.linear_str, limit_area=self.outside_str, inplace=True)
        if self.prcp_str in data.columns:
            data[self.prcp_str].fillna(0, inplace=True)
        if self.snow_str in data.columns:
            data[self.snow_str].fillna(0, inplace=True)
        if self.wspd_str in data.columns:
            data[self.wspd_str].fillna(0, inplace=True)
        if data[self.pres_str].isnull().values.any():
            data[self.pres_str] = 0

        data = data.drop(columns=self.weather_cols_to_drop)
        data.interpolate(self.linear_str, inplace=True)
        return data


    def calculate_delta_days(self, start_date_str: str, end_date_str: str) -> timedelta:
        '''
        Calculate the number of days between two dates.
        Args:
            start_date_str:  str containing the start date in the format "yyyy-mm-dd".
            end_date_str: str containing the end date in the format "yyyy-mm-dd".

        Returns: timedelta object containing the number of days between the two dates.

        '''

        start_date = datetime.strptime(start_date_str, self.strptime_format).date()
        end_date = datetime.strptime(end_date_str, self.strptime_format).date()
        delta = end_date - start_date + timedelta(days=1)
        return delta


    def lat_and_long_from_df_stores_location(self, df_stores_location: pd.DataFrame, store: int) -> tuple:
        '''
        Return the latitude and longitude of a store from the df_stores_location DataFrame.
        Args:
            df_stores_location: A DataFrame containing the store locations.
            store: The store id.
        Returns: A tuple containing the latitude and longitude of the store.
        '''

        store_location = df_stores_location[df_stores_location[self.store_str] == store]
        latitude = store_location[self.latitude_str].values[0]
        longitude = store_location[self.longitude_str].values[0]
        return latitude, longitude

    def calculate_lat_and_long_with_outlier_locations(self, df_stores_location: pd.DataFrame, store: int,
                                                      delta: timedelta,
                                                      start_date_str: str, end_date_str: str, ) -> pd.DataFrame:
        """
        Calculate the latitude and longitude of a store. If the store is an outlier, the default latitude and longitude
        Args:
            df_stores_location:   A DataFrame containing the store locations. columns: store_id, latitude, longitude
            store: int containing the store id
            delta: timedelta object containing the number of days between the two dates.
            start_date_str: str containing the start date in the format "yyyy-mm-dd".
            end_date_str: str containing the end date in the format "yyyy-mm-dd".


        Returns: A DataFrame containing the daily weather data for the specified location and date range.

        """

        latitude, longitude = self.lat_and_long_from_df_stores_location(df_stores_location, store)
        df_weather_of_store = self.return_weather_daily_data_for_specific_location(latitude,longitude)[self.weather_columns]
        if (len(df_weather_of_store) < delta.days) or df_weather_of_store.isna().sum().sum() > 0:
            df_weather_of_store = self.return_weather_daily_data_for_specific_location(self.default_latitude,
                                                                                       self.default_longitude)[self.weather_columns]
        return df_weather_of_store

    def return_all_stores_weather(self, df_stores_location: pd.DataFrame) -> pd.DataFrame:
        """
        Return the weather data for all stores in the df_stores_location DataFrame.
        Args:
            df_stores_location: df_stores_location:   A DataFrame containing the store locations. columns: store_id, latitude, longitude


        Returns: A DataFrame containing the daily weather data for all stores in the df_stores_location DataFrame.

        """
        df_all_weather = pd.DataFrame(columns=self.weather_columns)
        delta = WeatherFeatureGenerator.calculate_delta_days(self, self.start_date, self.end_date)
        if self.store_id_str in df_stores_location.columns:
            df_stores_location = df_stores_location.rename(columns={self.store_id_str: self.store_str})
        df_stores_location[self.store_str] = df_stores_location[self.store_str].astype(int)
        for store in df_stores_location[self.store_str].unique():
            df_weather_of_store = WeatherFeatureGenerator.calculate_lat_and_long_with_outlier_locations(self,
                                                                                                        df_stores_location,
                                                                                                        store, delta,
                                                                                                        self.start_date,
                                                                                                        self.end_date)
            df_weather_of_store[self.store_str] = store
            df_all_weather = pd.concat([df_all_weather, df_weather_of_store])
        df_all_weather = df_all_weather.reset_index().rename(columns={self.index_str: self.date_str})
        df_all_weather[self.store_str] = df_all_weather[self.store_str].astype(int)
        return df_all_weather


