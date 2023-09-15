import os
import logging
import datetime

def create_logger(location_of_logs):
    if not os.path.exists(location_of_logs+ '/logs'):
        os.makedirs(location_of_logs+ '/logs')
    if not os.path.exists(location_of_logs+ '/logs/feature_selection'):
        os.makedirs(location_of_logs+ '/logs/feature_selection')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) # Set logging level to INFO
    # name of log with time and date
    file_handler = logging.FileHandler(
        location_of_logs+ '/logs/feature_selection/' + str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + '.log')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

