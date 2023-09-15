import pandas as pd
from matplotlib import pyplot as plt
from src.feature_selection.linear_features import LinearFeatures
from configs.static_config_feature_selection import *
from src.feature_selection.stastical_analysis import StatisticalAnalysis
from src.feature_selection.tests.loader.test_data import data_clearml
from src.feature_selection.mutual_info import MutualInformation
from src.feature_selection.shap_feature_selection import ShapFeatureSelection


class FeatureSelectionReport():
    def __init__(self):
        self.item_str = item_str
        self.store_str = store_str
        self.date_str = date_str
        self.random_state = 42
        self.verbose = False
        self.max_depth = 6
        self.tree_model = None
        if self.tree_model is None:
            self.tree_model = CatBoostRegressor(random_state=self.random_state, verbose=self.verbose,
                                                max_depth=self.max_depth)
    def run_pipline_feature_selection(self, data_sales):
        """
        This function runs the feature selection pipeline and returns the selected features
        Args:
            data_sales: the data frame of the sales data


        Returns:
            selected_features: the list of the selected features
        """
        df_temp = data_sales.drop(columns=[self.item_str, self.store_str])
        shap_feature_importance = ShapFeatureSelection().get_feature_importance(df_temp, self.tree_model)
        mutual_information_feature_importance = MutualInformation().get_mutual_information(df_temp)
        feature_selection_results = {"shap_feature_importance": shap_feature_importance,
                                     "mutual_information_feature_importance": mutual_information_feature_importance}
        statistical_analysis = StatisticalAnalysis(feature_selection_results)
        features_importance = statistical_analysis.get_percentages_of_features()
        features_importance = features_importance
        return list(features_importance)

    def apply_feature_stastics_on_dict_methods(self, example_data):

        data_ = example_data.copy()
        df_temp = data_.drop(columns=[self.item_str, self.store_str])
        shap_feature_importance = ShapFeatureSelection().get_feature_importance(df_temp, self.tree_model)
        mutual_information_feature_importance = MutualInformation().get_mutual_information(df_temp)
        feature_selection_results = {"shap_feature_importance": shap_feature_importance,
                                     "mutual_information_feature_importance": mutual_information_feature_importance}
        statistical_analysis = StatisticalAnalysis(feature_selection_results)
        statistical_analysis.compare_methods()
        statistical_analysis.get_percentages_of_features()
        statistical_analysis.plot_comparison()


    def create_plot_attrs(self, dict_for_plot):
        """
        This function creates the plot attributes for the plot of the linear feature selection
        the following attributes are created:
        weights_exp: the weights of the exponential smoothing
        errors_exp: the errors of the exponential smoothing
        weights_roll: the weights of the rolling blend
        errors_roll: the errors of the rolling blend
        best_weight: the best weight
        best_error: the best error
        it also plots the results
        Args:
            dict_for_plot: the dictionary of the results of the linear feature selection

        """
        weights_exp = [d['w'] for d in dict_for_plot["smoothing_exponential"]]
        errors_exp = [d['error'] for d in dict_for_plot["smoothing_exponential"]]
        weights_roll = [d['w'] for d in dict_for_plot["rolling_blend"]]
        errors_roll = [d['error'] for d in dict_for_plot["rolling_blend"]]
        best_weight = dict_for_plot['best_weight']
        best_error = dict_for_plot['best_error']
        fig, ax = plt.subplots()
        ax.plot(weights_exp, errors_exp, label='Exponential Smoothing')
        ax.plot(weights_roll, errors_roll, label='Rolling Blend')
        ax.axvline(best_weight, color='red', linestyle='--', label='Best Weight')
        ax.axhline(best_error, color='green', linestyle='--', label='Best Error')
        ax.set_xlabel("Weight")
        ax.set_ylabel("Error")
        ax.set_title(f"Linear Feature Selection with best_window: {dict_for_plot['best_window']}")
        ax.legend()
        plt.show()


    def main_report_for_one_id(self, data_sales):
        selected_features = self.run_pipline_feature_selection(data_sales)
        linear_features = LinearFeatures()
        dict_for_plot = linear_features.for_plot_window_and_method(data_sales, selected_features, self.tree_model)
        df_temp = data_sales.drop(columns=[self.item_str, self.store_str])
        shap_feature_importance = ShapFeatureSelection().get_feature_importance(df_temp, self.tree_model)
        mutual_information_feature_importance = MutualInformation().get_mutual_information(df_temp)
        feature_selection_results = {"shap_feature_importance": shap_feature_importance,
                                     "mutual_information_feature_importance": mutual_information_feature_importance}
        statistical_analysis = StatisticalAnalysis(feature_selection_results)
        report_features_model = {
            "compare_methods": statistical_analysis.compare_methods(),
            "plot_comparison": statistical_analysis.plot_comparison(),
            "get_percentages_of_features": statistical_analysis.get_percentages_of_features(),
        }
        report_linear_features = {
            "plot_linear_features": self.create_plot_attrs(dict_for_plot)
        }
        return report_features_model,report_linear_features


if __name__ == '__main__':
    example_data = data_clearml()
    print(example_data)
    #
    report_features_model,report_linear_features = FeatureSelectionReport().main_report_for_one_id(example_data)
    print(report_features_model['compare_methods'])
    print(report_features_model['plot_comparison'])
    print(report_features_model['get_percentages_of_features'])
    print(report_linear_features['plot_linear_features'])


