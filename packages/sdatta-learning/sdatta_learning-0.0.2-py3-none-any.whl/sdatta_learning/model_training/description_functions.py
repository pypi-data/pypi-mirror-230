
def no_cross_validation_description(all_results: dict, id: str) -> dict:
    """
    add to all_results[id]['description'] the description of no cross validation.
    Args:
        all_results: dict of all results
        id:  str of id

    Returns:   all_results

    """
    if 'description' not in all_results[id]:
        all_results[id]['description'] = ""
    all_results[id]['description'] = "|no cross validation|"
    return all_results
def cross_validation_types_description(all_results: dict,
                                       id: str,
                                       cv_type: str,
                                       n_cv_splits: int,
                                       val_percent_blocked: float,
                                       val_size_timeseries: int,
                                       len_of_fold: int) -> dict:
    """
    add to all_results[id]['description'] the description of cross validation.
    Args:
        all_results: dict of all results
        id: str of id
        cv_type: str of type of cross validation
        n_cv_splits: int of number of splits(folds)
        val_percent_blocked: float of percent of validation data from each fold
        val_size_timeseries:  int of size of validation data from each fold

    Returns:  all_results

    """
    if 'description' not in all_results[id]:
        all_results[id]['description'] = ""
    all_results[id]['description'] = "|cross validation:" + str(cv_type) + "|"
    if cv_type == 'FixedWindowBlocked':
        all_results[id]['description'] += f"with val_percent_blocked:" + str(val_percent_blocked) + f" n_cv_splits: {n_cv_splits}" + f" len_of_fold: {len_of_fold}" + "|"
    elif cv_type == 'SeparatedBlocked':
        all_results[id]['description'] += f"with val_percent_blocked:" + str(val_percent_blocked) + f" n_cv_splits: {n_cv_splits}" + "|"
    elif cv_type == 'TimeSeriesSplit':
        all_results[id]['description'] += f"with val_size_timeseries:" + str(val_size_timeseries) + f" n_cv_splits: {n_cv_splits}" + "|"
    return all_results

def add_description_of_train_test_split_for_cross_validation_pipeline(all_results: dict, id: str,
                                                                      split_train_test_for_cross_validation_pipeline_bool: bool) -> dict:
    """
    add to all_results[id]['description'] the description of split_train_test_for_cross_validation_pipeline_bool.
    Args:
        all_results:    dict of all results
        id:        str of id
        split_train_test_for_cross_validation_pipeline_bool:  bool of split_train_test_for_cross_validation_pipeline_bool

    Returns:

    """
    if 'description' not in all_results[id]:
        all_results[id]['description'] = ""
    if split_train_test_for_cross_validation_pipeline_bool == True:
        all_results[id]['description'] += "the date is split to train and test from X and y(from train make the new train and validation)|"
    else:
        all_results[id]['description'] += "the date is not split, it is just X and y(no test)|"
    return all_results

def with_tuning_description(all_results: dict, id: str) -> dict:
    """
    add to all_results[id]['description'] the description of with tuning.
    Args:
        all_results: dict of all results
        id: str of id

    Returns: all_results

    """
    if 'description' not in all_results[id]:
        all_results[id]['description'] = ""
    all_results[id]['description'] += "with tuning|"
    return all_results

def no_tuning_description(all_results: dict, id: str) -> dict:
    """
    add to all_results[id]['description'] the description of no tuning.
    Args:
        all_results:  dict of all results
        id:  str of id

    Returns: all_results

    """
    if 'description' not in all_results[id]:
        all_results[id]['description'] = ""
    all_results[id]['description'] += "no tuning|"
    return all_results

def add_models_list_description(all_results: dict, id: str, models_to_train: dict) -> dict:
    """
    add to all_results[id]['description'] the description of models_to_train.
    Args:
        all_results:    dict of all results
        id:     str of id
        models_to_train:    dict of models_to_train

    Returns:    all_results

    """
    if 'description' not in all_results[id]:
        all_results[id]['description'] = ""
    all_results[id]['description'] += "models_base_stock_tasks: "
    for nodel_name in models_to_train:
        all_results[id]['description'] += nodel_name + ", "
    # delete ", " from the end of the string
    all_results[id]['description'] = all_results[id]['description'][:-2]
    all_results[id]['description'] += "|"
    return all_results

def add_description_of_split_train_test_pipeline(all_results: dict, id: str, split_train_test_pipeline_bool=False,
                                                 split_date=None) -> dict:
    """
    add to all_results[id]['description'] the description of split_train_test_pipeline_bool.
    Args:
        all_results:
        id:

    Returns:

    """
    if 'description' not in all_results[id]:
        all_results[id]['description'] = ""
    if split_train_test_pipeline_bool:
        all_results[id]['description'] += "date of begin of test: " + str(split_date) + "|"
    else:
        all_results[id]['description'] += "no test|"
    return all_results