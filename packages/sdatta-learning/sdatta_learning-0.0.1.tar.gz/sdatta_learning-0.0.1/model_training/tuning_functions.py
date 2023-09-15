from itertools import product
import copy


def get_hyperparameter_combinations(param_grid: dict) -> list:
    """
    Returns a list of dictionaries, where each dictionary contains a
    hyperparameter combination based on the given dictionary of
    hyperparameters and their values.
    """
    param_names = list(param_grid.keys())
    param_values = list(param_grid.values())
    param_combinations = product(*param_values)
    return [dict(zip(param_names, p)) for p in param_combinations]



def create_model_with_hyperparameters(model, hyperparameters: dict) -> object:
    """
    Returns a new model object with the given hyperparameters.
    """
    model_new = copy.copy(model)
    model_new.set_params(**hyperparameters)
    return model_new
