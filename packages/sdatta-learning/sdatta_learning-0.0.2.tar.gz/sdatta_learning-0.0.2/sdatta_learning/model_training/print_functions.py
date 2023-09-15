from configs import global_static_config as static_config


def print_model_mae_mse(model_str: str, mae: float, mse: float, type_of_training: str):
    """
    print model, mae, mse, type_of_training.
    Args:
        model_str: str of model
        mae:  float of mae
        mse:  float of mse
        type_of_training:  str of type_of_training

    Returns: None

    """
    print(' model: ', model_str, end=' ')
    print(f'{static_config.mae_str} of {type_of_training}: ', mae, end=' ')
    print(f'{static_config.mse_str} of {type_of_training}: ', mse)


def print_description_of_iteration(all_results: dict, id: str):
    """
    print description of iteration.
    Args:
        all_results:  dict of all_results
        id:  str of id

    Returns: None

    """
    print("", str(id) + all_results[id]['description'])

def print_fold_number(fold_num: int):
    """
    print fold_num.
    Args:
        fold_num:  int of fold_num

    Returns: None

    """
    print(' fold: ', fold_num)