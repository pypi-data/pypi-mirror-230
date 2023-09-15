
import os
import logging
import datetime
from configs import global_static_config as static_config


def create_logger(location_of_log_file) -> logging.Logger:
    """
    create logger for logging training results.
    Returns:   logger

    """
    if not os.path.exists(location_of_log_file + '/logs'):
        os.makedirs(location_of_log_file + '/logs')
    if not os.path.exists(location_of_log_file + '/logs/training_model'):
        os.makedirs(location_of_log_file + '/logs/training_model')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO) # Set logging level to INFO
    # name of log with time and date
    file_handler = logging.FileHandler(
        location_of_log_file + '/logs/training_model/training_results_' +
        str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + '.log')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

def log_model_mae_mse(model_str: str, mae: float, mse: float, type_of_training: str, log_file: logging.Logger):
    """
    log model, mae, mse, type_of_training to log_file.
    Args:
        model_str:  str of model
        mae:  float of mae
        mse:  float of mse
        type_of_training:  str of type_of_training
        log_file:  logging.Logger of log_file

    Returns: None

    """
    log_file.info('model: ' + str(model_str) + ' ' + f'MAE of {type_of_training}: ' + str(mae) + ' ' + f'MSE of {type_of_training}: ' + str(mse) )

def log_description_of_iteration(all_results: dict, id: str, log_file: logging.Logger):
    """
    log description of iteration to log_file.
    Args:
        all_results:  dict of all_results
        id:  str of id
        log_file:  logging.Logger of log_file

    Returns: None

    """
    log_file.info(f"{static_config.item_store_str}:" + str(id) + all_results[id]['description'])

def log_fold_number(fold_num: int, log_file: logging.Logger):
    """
    log fold_num to log_file.
    Args:
        fold_num: int of fold_num
        log_file:  logging.Logger of log_file

    Returns: None

    """
    log_file.info('fold: ' + str(fold_num) )