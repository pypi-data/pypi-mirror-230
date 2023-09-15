from configs import global_static_config as static_config
from src.feature_selection.shap_feature_selection import ShapFeatureSelection
from src.feature_selection.mutual_info import MutualInformation
from src.feature_selection.stastical_analysis import StatisticalAnalysis
from src.feature_selection.feature_selection_structural_preprocessing import FeatureSelectionStructuralProcessing
from src.feature_selection.linear_features import LinearFeatures
from catboost import CatBoostRegressor
import pandas as pd


class FeatureSelectionProcess:
    def __init__(self, random_state=42, verbose=False, max_depth=6,
                 tree_model=None, weights=None, split_date_ratio=0.8,
                 window_size=4, highly_correlated_threshold=0.7, threshold_cum_perc=0.55,take_top_n_features_if_empty=5,
                 log_location='/Users/guybasson/PycharmProjects/sdatta_packages_new'):
        """
        This class is the main class for the feature selection process
        """
        self.random_state = random_state
        self.verbose = verbose
        self.max_depth = max_depth
        self.tree_model = tree_model
        self.weights = weights
        self.window_size = window_size
        self.highly_correlated_threshold = highly_correlated_threshold
        self.threshold_cum_perc = threshold_cum_perc
        self.log_location = log_location
        self.all_data_split_date_ratio = split_date_ratio
        if self.tree_model is None:
            self.tree_model = CatBoostRegressor(random_state=self.random_state, verbose=self.verbose,
                                                max_depth=self.max_depth)
        if self.weights is None:
            self.weights = [0.1, 0.2, 0.3, 0.4]

        self.take_top_n_features_if_empty = take_top_n_features_if_empty

        print("random_state: ", self.random_state)
        print("verbose: ", self.verbose)
        print("max_depth: ", self.max_depth)
        print("tree_model: ", self.tree_model)
        print("weights: ", self.weights)
        print("all_data_split_date_ratio: ", self.all_data_split_date_ratio)
        print("window_size: ", self.window_size)
        print("highly_correlated_threshold: ", self.highly_correlated_threshold)
        print("threshold_cum_perc: ", self.threshold_cum_perc)
        print("log_location: ", self.log_location)
        print("take_top_n_features_if_empty: ", self.take_top_n_features_if_empty)




    def run_pipline_feature_selection(self, data_sales, id, model, logger=None):
        """
        This function runs the feature selection pipeline and returns the selected features
        Args:
            data_sales: the data frame of the sales data

        Returns:
            selected_features: the list of the selected features
        """

        df_temp = data_sales.drop(columns=[static_config.item_str, static_config.store_str])
        shap_feature_importance = ShapFeatureSelection(self.highly_correlated_threshold, self.threshold_cum_perc).get_feature_importance(df_temp,
                                                                                                                model)
        top_shap_feature_importance = FeatureSelectionStructuralProcessing(self.highly_correlated_threshold, self.threshold_cum_perc).get_percentages_of_features(shap_feature_importance['SHAP'])
        for row in top_shap_feature_importance.itertuples():
            logger.info("SHAP feature importance for id %s: %s", id, row)
        mutual_information_feature_importance = MutualInformation(self.highly_correlated_threshold, self.threshold_cum_perc).get_mutual_information(df_temp)
        top_mutual_information_feature_importance = FeatureSelectionStructuralProcessing(self.highly_correlated_threshold, self.threshold_cum_perc).get_percentages_of_features(mutual_information_feature_importance['MI'])
        for row in top_mutual_information_feature_importance.itertuples():
            logger.info("Mutual information feature importance for id: %s: %s", id, row)
        feature_selection_results = {"shap_feature_importance": top_shap_feature_importance,
                                     "mutual_information_feature_importance": top_mutual_information_feature_importance}
        statistical_analysis = StatisticalAnalysis(feature_selection_results)
        features_importance = statistical_analysis.get_percentages_of_features()
        if len(features_importance) == 0:
            features_importance = shap_feature_importance.index[:self.take_top_n_features_if_empty]
        logger.info("Percentage importance of features for id: %s: %s", id, features_importance)
        return list(features_importance)
        # split percentage in better name is split_date_percentage

    def run_pipline_linear_feature(self, data_sales, features_importance: list, model, ):
        """
        This function runs the linear feature selection pipeline and returns the best method, weight and window
        Args:
            data_sales: the data frame of the sales data
            features_importance: the list of the selected features

        Returns:
            best_method: the best method
            best_weight: the best weight
            best_window: the best window
        """
        max_date = pd.to_datetime(data_sales[static_config.date_str].max())
        min_date = pd.to_datetime(data_sales[static_config.date_str].min())
        split_date = (
                min_date + pd.DateOffset(days=int((max_date - min_date).days * self.all_data_split_date_ratio))).strftime(
            '%Y-%m-%d')
        best_method, best_weight, best_window = LinearFeatures().find_best_window_and_method(data_sales,
                                                                                             features_importance, model,
                                                                                             split_date,
                                                                                             self.window_size,
                                                                                             self.weights)
        return best_method, best_weight, best_window



