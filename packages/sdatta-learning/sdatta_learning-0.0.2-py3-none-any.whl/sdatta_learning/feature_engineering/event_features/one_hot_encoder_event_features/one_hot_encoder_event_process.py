import pandas as pd
from configs import global_static_config as static_config


class OneHotEncoderEventFeaturesGenerator:
    def __init__(self):
        self.date_str = static_config.date_str

    def merge_event_one_hot_encoder_by_date(self, main_data: pd.DataFrame, event_one_hot_date: pd.DataFrame) -> pd.DataFrame:
        """ Merge the event one hot encoder dataframe with the main dataframe by date.

            Args:
                    main_data: The main dataframe.
                    event_one_hot_date: The event one hot encoder dataframe.
            Returns:
                    The merged dataframe.
        """
        type_of_date_column_in_main_data = main_data[self.date_str].dtype
        type_of_event_date_column = event_one_hot_date[self.date_str].dtype
        if type_of_date_column_in_main_data != type_of_event_date_column:
            event_one_hot_date[self.date_str] = event_one_hot_date[self.date_str].astype(type_of_date_column_in_main_data)
        main_data = main_data.merge(event_one_hot_date, on=self.date_str, how='left')
        return main_data
