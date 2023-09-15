from src.sdatta_learning.model_training.process_functions import TrainingModelProcess
from src.sdatta_learning.pipeline.model_training_pipeline import model_training_pipline

class ModelSelectionProcess:
    def __init__(self, cv_models_handel='TopNMAEModel', top_n=2, metric_for_find_best_in_tune='MAE',
                 train_again_on_all_X_with_best_hyperparameters=False, ):
        self.cv_models_handel = cv_models_handel
        self.top_n = top_n
        self.metric_for_find_best_in_tune = metric_for_find_best_in_tune
      #  self.train_again_on_all_X_with_best_hyperparameters = train_again_on_all_X_with_best_hyperparameters

        print("cv_models_handel: ", self.cv_models_handel)
        print("top_n: ", self.top_n)
    def one_model_handle(self, id, dict_of_results):
        # find keys that start with model_ in dict_of_results[id]['results']
        # find the results key that start with "results" in dict_of_results[id]
        result_key = [key for key in dict_of_results[id] if key.startswith('results')][0]
        key_of_model = [key for key in dict_of_results[id][result_key] if key.startswith('model_')]
        model = dict_of_results[id][result_key][key_of_model[0]]
        return model

    def best_tune_results_with_description_no_cv(self, data):
        """Extract the best tune result for each ID based on the specified metric and include description."""
        best_results = {}

        for key, value in data.items():
            best_result = {}
            best_metric_value = float('inf')  # start with a very large value

            for sub_key, sub_value in value.items():
                if 'results_of_tune_combination' in sub_key:
                    if sub_value[self.metric_for_find_best_in_tune] < best_metric_value:
                        best_metric_value = sub_value[self.metric_for_find_best_in_tune]
                        # Finding the model key
                        model_key = next(
                            k for k in sub_value if k.startswith('model_'))
                        best_result['final_model'] = sub_value[model_key]
                        best_result['best_params_of_tune_combination'] = sub_value['params_of_tune_combination']
            best_results[key] = best_result

        return best_results

    def best_tune_results_with_description_with_cv(self, data):
        output = {}
        for key, value in data.items():
            description = value['description']
            best_results = {}
            tune_combinations = {}

            # Extracting tune combinations
            for inner_key, inner_value in value.items():
                if "results_of_tune_combination" in inner_key:
                    tune_id = "_".join(inner_key.split("_")[3:5])
                    if tune_id not in tune_combinations:
                        tune_combinations[tune_id] = []
                    tune_combinations[tune_id].append(inner_value)

            # Calculating average MAE for each tune combination
            avg_mae = {}
            for tune, results in tune_combinations.items():
                total_mae = sum([res[self.metric_for_find_best_in_tune] for res in results])
                avg_mae[tune] = total_mae / len(results)

            # Sorting the tune combinations by average MAE
            sorted_tunes = sorted(avg_mae, key=avg_mae.get)
            best_tune = sorted_tunes[0]

            # Extracting the results for the best tune combination
            params = {}
            for inner_key, inner_value in value.items():
                if best_tune in inner_key:
                    best_results[inner_key] = inner_value

            output[key] = {
                'description': description,
                **best_results
            }
        all_ids_final_model = {}
        for id in output:
            all_ids_final_model[id] = {}

            all_ids_final_model[id]['final_model'] = self.multiple_models_cv_handle(id, output)
            # find all key of output[id] that start with results
            keys_of_results = [key for key in output[id] if key.startswith('results_')]
            all_ids_final_model[id]['best_params_of_tune_combination'] = output[id][keys_of_results[0]][
                'params_of_tune_combination']
        return all_ids_final_model


    def multiple_models_cv_handle(self, id, dict_of_results):

        models = []
        end_dates = []
        maes = []
        keys_of_results = [key for key in dict_of_results[id] if key.startswith('results_')]
        for key_of_result in keys_of_results:
            model = dict_of_results[id][key_of_result]
            models.append(model)
            end_dates.append(model['end_date_of_fold'])
            maes.append(model['MAE'])
        # Sort models_base_stock_tasks based on end date
        sorted_indices = sorted(range(len(end_dates)), key=lambda k: end_dates[k])
        sorted_models = [models[i] for i in sorted_indices]
        sorted_models_objects = [model[key] for model in sorted_models for key in model if key.startswith('model_')]
        # Assign weights based on the order (more recent models_base_stock_tasks get higher weights)
        total_models = len(sorted_models_objects)
        weights = [i / total_models for i in range(1, total_models + 1)]
        # TODO: check if the weights are correct for each model
        if self.cv_models_handel == 'TimeWeightedModel':
            final_model = TimeWeightedModel(sorted_models_objects, weights)
        elif self.cv_models_handel == 'MAEWeightedModel':
            final_model = MAEWeightedModel(sorted_models_objects, maes)
        elif self.cv_models_handel == 'MAETimeWeightedModel':
            final_model = MAETimeWeightedModel(sorted_models_objects, maes, end_dates)
        elif self.cv_models_handel == 'TopNMAEModel':
            final_model = TopNMAEModel(sorted_models_objects, maes, self.top_n)
        elif self.cv_models_handel == 'TopLastFoldModel':
            final_model = TopLastFoldModel(sorted_models_objects, end_dates, self.top_n)
        else:
            raise ValueError('Invalid model handle: {}'.format(self.cv_models_handel))
        return final_model


    def train_again_model_with_best_hyparams_on_all_X(self, dict_of_results, data_with_features, top_features_dict):
        dict_of_final_models = {}

        for id, _results in dict_of_results.items():
            best_mae = float('inf')  # initialize with a high value
            best_params = None
            best_model = None
            best_model_name = None
            print('id: ', id)
            # Loop through the results of each tuning combination for the stock task
            for key, results in _results.items():
                if 'MAE' in results and results['MAE'] < best_mae:
                    # Find the model key
                    model_key = next((k for k in results.keys() if k.startswith("model_")), None)
                    if model_key:
                        best_mae = results['MAE']
                        best_model = results[model_key]
                        if 'params_of_tune_combination' in results:
                           best_params = results['params_of_tune_combination']
                        else:
                            best_params = best_model.get_params()
                        best_model_name = model_key

            model_class = type(best_model)
            uninitialized_model = model_class(**best_params)
            model_to_train = {best_model_name: uninitialized_model}

            training_model_process = TrainingModelProcess(tune_models_bool=False,
                                                          add_training_log_bool=False,
                                                          split_train_test_for_cross_validation_pipeline_bool=False,
                                                          remote_training_bool=False,
                                                          parse_columns_bool=False,
                                                          take_top_features_bool=True,
                                                          cross_validation_bool=False,
                                                          split_train_test_pipeline_bool=False,
                                                          models_to_train=model_to_train,
                                                          columns_to_drop_for_X=['sales', 'item', 'store', 'item, store'],
                                                          column_of_y='sales')
            id_data_with_features = data_with_features[data_with_features['item, store'] == id]
            all_results_and_models, _ = model_training_pipline(training_model_process=training_model_process,
                                                            data_with_all_features=id_data_with_features,
                                                            dict_of_top_features=top_features_dict)
            model = self.one_model_handle(id, all_results_and_models)
            dict_of_final_models[id] = {'final_model': model, 'best_params_of_tune_combination': best_params}
        return dict_of_final_models