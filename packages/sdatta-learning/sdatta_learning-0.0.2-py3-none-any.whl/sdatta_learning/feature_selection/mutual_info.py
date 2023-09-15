from sklearn.feature_selection import mutual_info_regression
import pandas as pd
from src.sdatta_learning.feature_selection.feature_selection_structural_preprocessing import FeatureSelectionStructuralProcessing
from sklearn.impute import SimpleImputer

class MutualInformation:
    def __init__(self, highly_correlated_threshold, threshold_cum_perc):
        self.highly_correlated_threshold = highly_correlated_threshold
        self.threshold_cum_perc = threshold_cum_perc
    def get_mutual_information(self, df, mi_col: str = "MI", start_date: str = "2019-01-01", target: str = "sales",date_col: str = "date"):
        X, y = FeatureSelectionStructuralProcessing(self.highly_correlated_threshold, self.threshold_cum_perc).apply_feature_selection_process(df,target, date_col)
        column_names = X.columns
        imputer = SimpleImputer(strategy='mean')
        X = imputer.fit_transform(X)
        mi = mutual_info_regression(X, y)
        selected_features = pd.DataFrame(mi, index=column_names, columns=[mi_col]).sort_values(by=mi_col,
                                                                                               ascending=False)
        selected_features = selected_features[(selected_features[mi_col] != 0)]
        return selected_features