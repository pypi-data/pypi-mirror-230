import shap
import pandas as pd
import numpy as np
from src.sdatta_learning.feature_selection.feature_selection_structural_preprocessing import \
    FeatureSelectionStructuralProcessing
from configs import global_static_config as static_config


class ShapFeatureSelection:
    def __init__(self, highly_correlated_threshold, threshold_cum_perc):
        self.shap_str = 'SHAP'
        self.sales_str = static_config.sales_str
        self.date_str = static_config.date_str
        self.highly_correlated_threshold = highly_correlated_threshold
        self.threshold_cum_perc = threshold_cum_perc


        pass

    def get_feature_importance(self, df, model):
        X, y = FeatureSelectionStructuralProcessing(self.highly_correlated_threshold, self.threshold_cum_perc).apply_feature_selection_process(df, self.sales_str, self.date_str)
        model = model.fit(X, y)
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        feature_importance = pd.DataFrame(np.abs(shap_values).mean(axis=0), index=X.columns,
                                          columns=[self.shap_str]).sort_values(by=self.shap_str, ascending=False)
        feature_importance = feature_importance[(feature_importance[self.shap_str] != 0)]
        return feature_importance
