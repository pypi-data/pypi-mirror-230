
import pandas as pd
from clearml import Dataset
from configs import global_static_config as static_config


def df_from_dataset_clearml(dataset_name: str, dataset_project: str, file_name: str,
                            drop_col: str = static_config.Unnamed_0_col) -> pd.DataFrame:
    """
    This function gets a dataset from clearml and returns a pandas dataframe
    Args:
        dataset_name:   dataset name
        dataset_project:   dataset project
        file_name:  file name
        drop_col:   column to drop

    Returns: pandas dataframe

    """
    df_dataset = Dataset.get(dataset_project=dataset_project, dataset_name=dataset_name)
    df_dataset_folder = df_dataset.get_local_copy()
    df = pd.read_csv(df_dataset_folder + '/' + file_name)
    if drop_col in df.columns:
        df = df.drop(columns=[drop_col])
    return df