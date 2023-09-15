from src.sdatta_learning.model_training.tuning_functions import *
from src.utils import *
from src.sdatta_learning.model_training.description_functions import *
from src.sdatta_learning.model_training.logging_functions import *
from configs import global_static_config as static_config
from catboost import CatBoostRegressor

class TrainingModelProcess():

    def __init__(self,
                 tune_models_bool=False,
                 add_training_log_bool=False,
                 split_train_test_for_cross_validation_pipeline_bool=False,
                 remote_training_bool=False,
                 parse_columns_bool=False,
                 take_top_features_bool=False,
                 cross_validation_bool=False,
                 split_train_test_pipeline_bool=True,
                 models_to_train={
                     'CatBoostRegressor': CatBoostRegressor(verbose=False, random_state=42, max_depth=6,    )
                 },
                 columns_to_drop_for_X=['sales', 'item', 'store', 'item, store'],
                 column_of_y='sales',
                 location_of_log_file='/Users/guybasson/PycharmProjects/sdatta_packages_new',
                 params_to_tune={
                     'CatBoostRegressor': {'verbose': [False],
                         'max_depth': [4, 5],
                         'n_estimators': [100],
                     }

                 },
                 cv_type='SeparatedBlocked',
                 n_cv_splits=2,
                 val_percent_blocked=0.25,
                 val_size_timeseries=50,
                 len_of_fold=100,
                 min_len_for_cross_validation=100,
                 split_date_ratio=0.8,
                 ):

        self.tune_models_bool = tune_models_bool
        self.add_training_log_bool = add_training_log_bool
        self.split_train_test_for_cross_validation_pipeline_bool = split_train_test_for_cross_validation_pipeline_bool
        self.remote_training_bool = remote_training_bool
        self.parse_columns_bool = parse_columns_bool
        self.take_top_features_bool = take_top_features_bool
        self.cross_validation_bool = cross_validation_bool
        self.split_train_test_pipeline_bool = split_train_test_pipeline_bool
        self.models_to_train = models_to_train
        self.columns_to_drop_for_X = columns_to_drop_for_X
        self.column_of_y = column_of_y
        self.location_of_log_file = location_of_log_file
        self.params_to_tune = params_to_tune
        self.cv_type = cv_type
        self.n_cv_splits = n_cv_splits
        self.val_percent_blocked = val_percent_blocked
        self.val_size_timeseries = val_size_timeseries
        self.len_of_fold = len_of_fold
        self.min_len_for_cross_validation = min_len_for_cross_validation
        self.split_date_ratio = split_date_ratio

        print("tune_models_bool: ", self.tune_models_bool)
        print("add_training_log_bool: ", self.add_training_log_bool)
        print("split_train_test_for_cross_validation_pipeline_bool: ", self.split_train_test_for_cross_validation_pipeline_bool)
        print("remote_training_bool: ", self.remote_training_bool)
        print("parse_columns_bool: ", self.parse_columns_bool)
        print("take_top_features_bool: ", self.take_top_features_bool)
        print("cross_validation_bool: ", self.cross_validation_bool)
        print("split_train_test_pipeline_bool: ", self.split_train_test_pipeline_bool)
        print("models_to_train: ", self.models_to_train)
        print("columns_to_drop_for_X: ", self.columns_to_drop_for_X)
        print("column_of_y: ", self.column_of_y)
        print("location_of_log_file: ", self.location_of_log_file)
        print("params_to_tune: ", self.params_to_tune)
        print("cv_type: ", self.cv_type)
        print("n_cv_splits: ", self.n_cv_splits)
        print("val_percent_blocked: ", self.val_percent_blocked)
        print("val_size_timeseries: ", self.val_size_timeseries)
        print("len_of_fold: ", self.len_of_fold)
        print("min_len_for_cross_validation: ", self.min_len_for_cross_validation)
        print("split_date_ratio: ", self.split_date_ratio)

        if self.cross_validation_bool == False and self.tune_models_bool == True and self.split_train_test_pipeline_bool == False:
            raise Exception("You can't tune models without cross validation or split train test pipeline")

    def no_cross_validation_pipeline_with_split_train_test(cls, all_results, id, X_train, y_train, X_test, y_test, logger=None):
        all_results = no_cross_validation_description(all_results, id)
        type_of_training = static_config.test_str
        if cls.tune_models_bool == False:
            all_results = no_tuning_description(all_results, id)
            id_result = {}
            print_description_of_iteration(all_results, id)  # print description of iteration
            if logger is not None:
                log_description_of_iteration(all_results, id, logger)
            for model_str, model_name in zip(cls.models_to_train.keys(), range(len(cls.models_to_train))):
                trained_model = train_model(X_train, y_train, cls.models_to_train[model_str])
                id_result = predict_and_return_results(trained_model, model_str, X_test, y_test, type_of_training, logger)
            all_results[id]['results'] = id_result
        else:  # tune_models_bool == True
            all_results = with_tuning_description(all_results, id)
            print_description_of_iteration(all_results, id)  # print description of iteration
            if logger is not None:
                log_description_of_iteration(all_results, id, logger)
            for model_str, model_num in zip(cls.models_to_train.keys(), range(len(cls.models_to_train))):
                model_copy = cls.models_to_train[model_str]
                hyperparams_combinations = get_hyperparameter_combinations(cls.params_to_tune[model_str])
                for i, hyperparams in enumerate(hyperparams_combinations):
                    model_with_hyperparams = create_model_with_hyperparameters(model_copy, hyperparams)
                    trained_model = train_model(X_train, y_train, model_with_hyperparams)
                    id_result = predict_and_return_results(trained_model, model_str, X_test, y_test,
                                                           type_of_training, logger)
                    id_result.update({'params_of_tune_combination': hyperparams,})
                    key = 'results_of_tune_combination_' + str(i)
                    if key not in all_results[id]:
                        all_results[id][key] = id_result
                    else:
                        all_results[id][key].update(id_result)
        return all_results

    def no_cross_validation_pipeline_no_split_train_test(cls, all_results, id, X, y, logger=None):
        all_results = no_cross_validation_description(all_results, id)
        if cls.tune_models_bool == False:
            all_results = no_tuning_description(all_results, id)
            id_result = {}
            print_description_of_iteration(all_results, id)  # print description of iteration
            if logger is not None:
                log_description_of_iteration(all_results, id, logger)
            for model_str, model_name in zip(cls.models_to_train.keys(), range(len(cls.models_to_train))):
                trained_model = train_model(X, y, cls.models_to_train[model_str])
                id_result = {f'model_{model_str}': trained_model}
            all_results[id]['results'] = id_result
        else:  # tune_models_bool == True
            all_results = with_tuning_description(all_results, id)
            print_description_of_iteration(all_results, id)  # print description of iteration
            if logger is not None:
                log_description_of_iteration(all_results, id, logger)
            for model_str, model_num in zip(cls.models_to_train.keys(), range(len(cls.models_to_train))):
                model_copy = cls.models_to_train[model_str]
                hyperparams_combinations = get_hyperparameter_combinations(cls.params_to_tune[model_str])
                for i, hyperparams in enumerate(hyperparams_combinations):
                    model_with_hyperparams = create_model_with_hyperparameters(model_copy, hyperparams)
                    trained_model = train_model(X, y, model_with_hyperparams)
                    id_result = {f'model_{model_str}': trained_model}
                    id_result.update({'params_of_tune_combination': hyperparams,})
                    key = 'results_of_tune_combination_' + str(i)
                    if key not in all_results[id]:
                        all_results[id][key] = id_result
                    else:
                        all_results[id][key].update(id_result)

        return all_results

    def cross_validation_pipeline(cls, all_results, id, X, y, logger=None):
        all_results = cross_validation_types_description(all_results,
                                       id,
                                       cv_type=cls.cv_type,
                                       n_cv_splits=cls.n_cv_splits,
                                       val_percent_blocked=cls.val_percent_blocked,
                                       val_size_timeseries=cls.val_size_timeseries,
                                       len_of_fold=cls.len_of_fold)
        X_trains, y_trains, X_vals, y_vals = create_ts_folds(X=X, y=y, cv_type=cls.cv_type,
                                                             n_splits=cls.n_cv_splits,
                                                             val_percent=cls.val_percent_blocked,
                                                             val_size=cls.val_size_timeseries,
                                                             len_of_fold=cls.len_of_fold)
        if any(all(val == row[0] for val in row) for row in y_trains): # y_trains are the same (no cross validation will be performed)
            print(' some y_trains are the same. No cross validation will be performed')
            if cls.split_train_test_pipeline_bool:
                X_train, X_test, y_train, y_test = create_X_y_train_test_split(X, y, split_date=cls.split_date)  # create X_train, X_test, y_train, y_test
                if len(set(y_train)) == 1:
                    cls.ids_no_models.append(id)
                else:
                    all_results = cls.no_cross_validation_pipeline_with_split_train_test(all_results, id, X_train,
                                                                                         y_train, X_test, y_test,
                                                                                         logger=logger)
            else:
                cls.ids_no_models.append(id)
        #        else:
         #           all_results = cls.no_cross_validation_pipeline_no_split_train_test(all_results, id, X, y, logger = logger)
            return all_results
        else: # y_trains are not the same (cross validation will be performed)
            all_results = add_description_of_train_test_split_for_cross_validation_pipeline(all_results=all_results, id=id,
            split_train_test_for_cross_validation_pipeline_bool=cls.split_train_test_for_cross_validation_pipeline_bool)
            type_of_training = static_config.val_str
            print("type_of_training", type_of_training)
            if cls.tune_models_bool == False:
                all_results = no_tuning_description(all_results, id)
                print_description_of_iteration(all_results, id)  # print description of iteration
                if logger is not None:
                    log_description_of_iteration(all_results, id, logger)
                for model_str, model_num in zip(cls.models_to_train.keys(), range(len(cls.models_to_train))):
                    for j in range(cls.n_cv_splits):
                        print_fold_number(j)
                        if logger is not None:
                            log_fold_number(j, logger)
                        X_train , y_train , X_val , y_val = X_trains[j], y_trains[j], X_vals[j], y_vals[j]
                        model_copy = cls.models_to_train[model_str]
                        trained_model = train_model(X_train, y_train, model_copy)
                        id_result = predict_and_return_results(trained_model, model_str, X_val, y_val,
                                                               type_of_training, logger)
                        id_result.update({'start_date_of_fold': X_train.index[0].strftime('%Y-%m-%d'),
                                                      'end_date_of_fold': X_train.index[-1].strftime('%Y-%m-%d')})
                        key = 'results_of_fold_' + str(j)
                        if key not in all_results[id]:
                            all_results[id][key] = id_result
                        else:
                            all_results[id][key].update(id_result)
            else:  # tune_models_bool == True
                all_results = with_tuning_description(all_results, id)
                print_description_of_iteration(all_results, id)  # print description of iteration
                if logger is not None:
                    log_description_of_iteration(all_results, id, logger)
                for model_str, model_num in zip(cls.models_to_train.keys(), range(len(cls.models_to_train))):
                    for j in range(cls.n_cv_splits):
                        print_fold_number(j)
                        if logger is not None:
                            log_fold_number(j, logger)
                        X_train , y_train , X_val , y_val = X_trains[j], y_trains[j], X_vals[j], y_vals[j]
                        model_copy = cls.models_to_train[model_str]
                        hyperparams_combinations = get_hyperparameter_combinations(cls.params_to_tune[model_str])
                        for i, hyperparams in enumerate(hyperparams_combinations):
                            model_with_hyperparams = create_model_with_hyperparameters(model_copy, hyperparams)
                            trained_model = train_model(X_train, y_train, model_with_hyperparams)
                            id_result = predict_and_return_results(trained_model, model_str, X_val, y_val,
                                                                   type_of_training, logger)
                            id_result.update({'params_of_tune_combination': hyperparams,
                                              'start_date_of_fold': X_train.index[0].strftime('%Y-%m-%d'),
                                              'end_date_of_fold': X_train.index[-1].strftime('%Y-%m-%d')})
                            key = 'results_of_tune_combination_' + str(i) + '_fold_' + str(j)
                            if key not in all_results[id]:
                                all_results[id][key] = id_result
                            else:
                                all_results[id][key].update(id_result)
            return all_results


    def ids_loop_pipeline(cls, data_with_all_features, dict_of_top_features=None):
        cls.ids_no_models = []
        if cls.add_training_log_bool:
            logger = create_logger(cls.location_of_log_file)
        else:
            logger = None
        if cls.remote_training_bool:
            pass
        if cls.parse_columns_bool:
            data_with_all_features = parse_columns(data_with_all_features)
        all_results = {}
        print(" ids:")
        len_of_ids = len(data_with_all_features[static_config.item_store_str].unique())
        i = 1
        for id in data_with_all_features[static_config.item_store_str].unique():
            print("id number: ", i, " out of ", len_of_ids)
            i += 1
            all_results[id] = {}
            id_data = data_with_all_features[data_with_all_features[static_config.item_store_str] == id]

            max_date = id_data.date.max()
            min_date = id_data.date.min()
            split_date = (
                        min_date + pd.DateOffset(days=int((max_date - min_date).days * cls.split_date_ratio))).strftime(
                '%Y-%m-%d')
            cls.split_date = split_date
            X, y = create_X_and_y(df=id_data, columns_to_drop_for_X=cls.columns_to_drop_for_X,
                                  column_of_y=cls.column_of_y) #  create X and y
            if cls.take_top_features_bool or dict_of_top_features != None:  # take top features after feature selection
                X = take_top_features(X, id, dict_of_top_features)  # take top features
            if cls.cross_validation_bool == False or len(X) <= cls.min_len_for_cross_validation:  # no cross validation
                if cls.split_train_test_pipeline_bool:  # split train and test
                    X_train, X_test, y_train, y_test = create_X_y_train_test_split(X, y, split_date=cls.split_date)  # create X_train, X_test, y_train, y_test
                    if len(set(y_train)) == 1:
                        cls.ids_no_models.append(id)
                    else:
                        all_results = cls.no_cross_validation_pipeline_with_split_train_test(all_results, id, X_train, y_train, X_test, y_test, logger = logger)
                else:  # no split train and test just X and y
                    if len(set(y)) == 1:
                        cls.ids_no_models.append(id)
                    else:
                        all_results = cls.no_cross_validation_pipeline_no_split_train_test(all_results, id, X, y, logger=logger)
            elif cls.cross_validation_bool == True:  # cross validation
                all_results = cls.cross_validation_pipeline(all_results, id, X, y, logger=logger)
            all_results = add_description_of_split_train_test_pipeline(all_results, id,  split_train_test_pipeline_bool=cls.split_train_test_pipeline_bool,
                                                 split_date=cls.split_date)
            all_results = add_models_list_description(all_results, id, models_to_train=cls.models_to_train)  # add models_base_stock_tasks list description
        return all_results, cls.ids_no_models



