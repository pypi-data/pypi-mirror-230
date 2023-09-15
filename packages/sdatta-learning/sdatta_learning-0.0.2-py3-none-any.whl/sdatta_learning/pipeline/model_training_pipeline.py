

def model_training_pipline(training_model_process, data_with_all_features, dict_of_top_features=None):
    all_results, ids_no_model = training_model_process.ids_loop_pipeline(data_with_all_features, dict_of_top_features)
    return all_results, ids_no_model




