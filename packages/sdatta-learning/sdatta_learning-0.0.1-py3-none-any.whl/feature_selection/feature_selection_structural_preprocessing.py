import pandas as pd
import numpy as np
from src.model_training.data_spliter import create_X_and_y

class FeatureSelectionStructuralProcessing:
    def __init__(self, highly_correlated_threshold, threshold_cum_perc,columns_to_drop_for_X=None,
                    column_of_y='sales'):
        self.highly_correlated_threshold = highly_correlated_threshold
        self.threshold_cum_perc = threshold_cum_perc
        self.columns_to_drop_for_X = columns_to_drop_for_X
        self.column_of_y = column_of_y
        if self.columns_to_drop_for_X is None:
            self.columns_to_drop_for_X = ['sales', 'item', 'store', 'item, store']

    def filter_data_by_date(self, df: pd.DataFrame, start_date: str, date: str = "date") -> pd.DataFrame:
        """
        Filter data by date
        Args:
            start_date:  Date string in the format of YYYY-MM-DD
        Returns:
            filtered pandas DataFrame
        """
        return df[df[date] >= start_date]

    def sort_by_date(self, df: pd.DataFrame, date: str = "date") -> pd.DataFrame:
        """
        Sort data by date
        Returns:
            sorted pandas DataFrame
        """
        return df.sort_values(by=date)

    def remove_highly_correlated_features(self, df):
        """
        Remove highly correlated features from the dataframe.

        Generates a correlation matrix and removes columns where the
        correlation exceeds the threshold.

        Args:
            df (pd.DataFrame): Input dataframe

        Returns:
            pd.DataFrame: DataFrame with highly correlated features removed.
        """
        corr_matrix = df.corr().abs()
        to_drop = set()
        for i in range(len(corr_matrix.columns)):
            for j in range(i):
                if abs(corr_matrix.iloc[i, j]) >= self.highly_correlated_threshold:
                    col_name = corr_matrix.columns[i]
                    to_drop.add(col_name)
        if len(to_drop) > 0:
            return df.drop(columns=list(to_drop))
        else:
            return df

    def apply_feature_selection_process(self, df, target_col: str, date_col: str):
        """
        Apply the full feature selection process to the dataframe.

        Args:
            df (pd.DataFrame): Input dataframe
            target_col (str): Name of target column
            date_col (str): Name of date column

        Returns:
            X (pd.DataFrame): Transformed feature dataframe
            y (pd.DataFrame): Target dataframe
        """
        df = self.sort_by_date(df)
        X, y = create_X_and_y(df=df, columns_to_drop_for_X=self.columns_to_drop_for_X,
                                  column_of_y=self.column_of_y)
        df_numeric = X.select_dtypes(include=[np.number])
        df_numeric = df_numeric.drop(columns=df_numeric.select_dtypes(include='timedelta64').columns.tolist())
        X = X[df_numeric.columns]
        X = self.remove_highly_correlated_features(X)
        return X, y

    def get_percentages_of_features(self, feature_importance_series):
        """
        This function calculates the percentage of cumulative feature importance and cuts off the features that
        contribute to the first threshold% of the cumulative feature importance.

        Args:
            feature_importance_series: A pandas Series where the index is the feature name and the value is its importance.

        Returns:
            selected_features: a list of features that contribute to the threshold% of cumulative feature importance.
        """

        # Sort the series by importance values in descending order
        sorted_features = feature_importance_series.sort_values(ascending=False)

        # Determine which features contribute to the first self.threshold_cum_perc% of cumulative feature importance
        selected_features = sorted_features[
            (sorted_features.cumsum() / sorted_features.sum()) <= self.threshold_cum_perc
            ].index.tolist()
        return feature_importance_series.loc[selected_features].to_frame()
