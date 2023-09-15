import pandas as pd
import copy

def train_model(X: pd.DataFrame, y: pd.Series, model: object) -> object:
    """
    train model.
    Args:
        X: df of X
        y:  series of y
        model:

    Returns:   fitted_model

    """
    fitted_model = copy.deepcopy(model)
    fitted_model.fit(X, y)
    return fitted_model