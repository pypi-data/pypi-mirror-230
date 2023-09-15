import logging
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from src.sdatta_learning.model_training.print_functions import print_model_mae_mse
from src.sdatta_learning.model_training.logging_functions import log_model_mae_mse
from configs import global_static_config as static_config


def predict_and_return_results(trained_model: object,
                               model_str,
                               X_test: pd.DataFrame,
                               y_test: pd.Series,
                               type_of_training: str,
                               log_file: logging.Logger=None,
                               log_bool: bool= None) -> dict:
    """
    predict and return results.
    Args:
        trained_model:  trained_model
        model_str:  str
        X_test:  pd.DataFrame
        y_test:  pd.Series
        type_of_training: type of training
        num_of_model:   int
        log_file:  log_file
        log_bool:  bool

    Returns:   id_result

    """
    y_pred = trained_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    print_model_mae_mse(model_str, mae, mse, type_of_training)
    if log_bool:
        log_model_mae_mse(model_str, mae, mse, type_of_training, log_file)
    id_result = {f'model_{model_str}': trained_model, static_config.mae_str: mae, static_config.mse_str: mse}
    return id_result