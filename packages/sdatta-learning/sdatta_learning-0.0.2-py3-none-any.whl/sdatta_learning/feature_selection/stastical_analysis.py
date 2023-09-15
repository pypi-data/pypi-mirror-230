import matplotlib.pyplot as plt


class StatisticalAnalysis:
    def __init__(self, feature_selection_results: dict):
        """
        Args:
            feature_selection_results: a dictionary where keys are the names of the feature selection methods
            and values are the corresponding feature importance dataframes
        """
        self.feature_selection_results = feature_selection_results

    def compare_methods(self):
        """
        Prints the top n features for each method
        """
        for method_name, feature_importance_df in self.feature_selection_results.items():
            print(f"Top 10 features for {method_name}:")
            print(feature_importance_df[:10])

    def get_percentages_of_features(self,threshold: float = 0.55):
        """
        This function calculates the percentage of cumulative feature importance for each method and cuts off the features that
        contribute to the first threshold% of the cumulative feature importance. It then calculates the intersection of the
        features selected by each method and prints the number of common features and the common features themselves.
        Args:
            threshold: the percentage of cumulative feature importance to be considered
        Returns:
            dict_features_cutoff: a dictionary where keys are the names of the feature selection methods
        """
        dict_features_cutoff = {}
        feature_sets = []
        for method_name, feature_importance_df in self.feature_selection_results.items():
            selected_features = feature_importance_df[
                (feature_importance_df.cumsum() / feature_importance_df.sum()) <= threshold].index.tolist()
            dict_features_cutoff[method_name] = feature_importance_df[(feature_importance_df.cumsum() / feature_importance_df.sum())<= threshold].index.tolist()
            feature_sets.append(set(selected_features))
            # print(f"Top {threshold}% features for {method_name}: number of features: {len(dict_features_cutoff[method_name])}")
        common_features = set.intersection(*feature_sets)
        return common_features

    def plot_comparison(self):
        """
        Creates a bar plot comparing the top n features from each method
        """
        n_methods = len(self.feature_selection_results)
        fig, axes = plt.subplots(n_methods, 1, figsize=(10, 6 * n_methods))

        for i, (method_name, feature_importance_df) in enumerate(self.feature_selection_results.items()):
            feature_importance_df[:10].plot(kind='bar', legend=False, ax=axes[i])
            axes[i].set_title(f"Top 10 features for {method_name}")
            axes[i].set_ylabel('Importance')

        plt.tight_layout()
        plt.show()