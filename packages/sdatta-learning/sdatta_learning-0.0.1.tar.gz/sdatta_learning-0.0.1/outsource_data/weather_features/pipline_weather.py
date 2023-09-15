from src.outsource_data.weather_features.weather_feature_process import WeatherFeatureGenerator
from src.utils import get_min_max_date

def run_pipline_weather(store_location_df, min_date, max_date, default_latitude, default_longitude):
    """
    Run the weather feature generation pipeline.
    Returns: A DataFrame containing the weather features for all stores.

    """
    weather_process = WeatherFeatureGenerator(default_latitude=default_latitude, default_longitude=default_longitude,
                                                start_date=min_date, end_date=max_date)
    df_stores_weather = weather_process.return_all_stores_weather(store_location_df)
    return df_stores_weather

