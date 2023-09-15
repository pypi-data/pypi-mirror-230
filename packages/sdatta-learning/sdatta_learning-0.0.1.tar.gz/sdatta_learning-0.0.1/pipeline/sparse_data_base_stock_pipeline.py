import pandas as pd


def receive_data_base_stock_pipeline(receive_base_stock_data_process, sales_sparse: pd.DataFrame, stock_sparse: pd.DataFrame,
                                     sales_over_months_for_seasonal_items: pd.DataFrame, min_date, max_date, relevant_ids) -> dict:
    sales_sparse, stock_sparse, relevant_sku_stock_in_stock_interval_time = \
        receive_base_stock_data_process.preprocess_data(sales_sparse, stock_sparse)
    dict_base_stock_results = receive_base_stock_data_process.calculate_base_stock_loop(sales_sparse, stock_sparse,
                                                                          sales_over_months_for_seasonal_items,
                                                                          relevant_ids, min_date, max_date)

    return dict_base_stock_results
