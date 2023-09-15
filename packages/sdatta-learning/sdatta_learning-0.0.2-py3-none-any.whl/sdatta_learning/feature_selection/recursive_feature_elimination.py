from sklearn.feature_selection import RFE
import pandas as pd
from src.sdatta_learning.feature_selection.feature_selection_structural_preprocessing import \
    FeatureSelectionStructuralProcessing
from configs.static_config_feature_selection import *


class RecursiveFeatureElimination:
    def __init__(self, highly_correlated_threshold, threshold_cum_perc,n_features_to_select=None):
        """
        Args:
            n_features_to_select: Number of features to select. If `None`, half of the features are selected.
        """
        self.n_features_to_select = n_features_to_select
        self.rfe_str = 'RFE'
        self.sales_str = sales_str
        self.date_str = date_str
        self.highly_correlated_threshold = highly_correlated_threshold
        self.threshold_cum_perc = threshold_cum_perc

    def select_features(self, df, model, start_date: str = "2019-01-01"):
        """
        Fit the model and select features
        Returns:
            DataFrame of selected features
        """
        X, y = FeatureSelectionStructuralProcessing(self.highly_correlated_threshold, self.threshold_cum_perc).apply_feature_selection_process(df, start_date, self.sales_str,
                                                                                        self.date_str)
        estimator = model
        selector = RFE(estimator, n_features_to_select=self.n_features_to_select)
        selector = selector.fit(X, y)
        selected_features = pd.DataFrame(selector.ranking_,
                                         index=X.columns,
                                         columns=[self.rfe_str]).sort_values(by=self.rfe_str, ascending=False)
        selected_features = selected_features[selected_features[self.rfe_str] > 1]
        return selected_features
