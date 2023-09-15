
def model_selection_pipline(model_selection_process, dict_of_results, data_with_features, top_features_dict,
                            run_again_on_best_hyparams=False):
    if run_again_on_best_hyparams == False:
        all_ids_final_model = {}
        if ('with tuning' in dict_of_results[list(dict_of_results.keys())[0]]['description']):
            # with tuning
            if ('no cross validation' in dict_of_results[list(dict_of_results.keys())[0]]['description']):
                #  no cv with tuning
                all_ids_final_model = model_selection_process.best_tune_results_with_description_no_cv(dict_of_results)
            elif ('no cross validation' not in dict_of_results[list(dict_of_results.keys())[0]]['description']):
                # with cv with tuning
                all_ids_final_model = model_selection_process.best_tune_results_with_description_with_cv(dict_of_results)
        elif ('with tuning' not in dict_of_results[list(dict_of_results.keys())[0]]['description']):
            # no tuning
            for id in dict_of_results:
                all_ids_final_model.update({id: {}})
                if  ('no cross validation' in dict_of_results[id]['description']) and \
                        ('with tuning' not in dict_of_results[id]['description']):
                    # no cv no tuning
                    all_ids_final_model[id]['final_model'] = model_selection_process.one_model_handle(id, dict_of_results)
                elif ('no cross validation' not in dict_of_results[id]['description']) and (
                        'with tuning' not in dict_of_results[id]['description']):
                    # with cv no tuning
                    all_ids_final_model[id]['final_model'] = model_selection_process.multiple_models_cv_handle(id, dict_of_results)

    else: # run_again_on_best_hyparams == True
        print(" run again on best hyparams on all X")
        all_ids_final_model = model_selection_process.train_again_model_with_best_hyparams_on_all_X(dict_of_results, data_with_features, top_features_dict)
    return all_ids_final_model