import warnings
from src.strategy_base_stock.sparse_data_handling.receive_data_handling.calculations import *
import configs.global_static_config as static_config
warnings.filterwarnings("ignore")


class ReceiveDataBaseStockDataProcess:
    def __init__(self, big_base_stock_value_base_stock_need_to_handel=20,
                 huge_base_stock = 1000,
                 ratio_threshold_between_sales_and_stock=0.5,
                 ratio_threshold_between_sales_and_stock_large_base_stock=0.2,
                 num_of_days_for_seasonal_train=365,
                 num_of_days_for_non_seasonal_train=150,
                 num_of_min_rows_for_calculation_base_stock=80,
                    freq='D'):
        self.big_base_stock_value_base_stock_need_to_handel = big_base_stock_value_base_stock_need_to_handel
        self.huge_base_stock = huge_base_stock
        self.ratio_threshold_between_sales_and_stock = ratio_threshold_between_sales_and_stock
        self.ratio_threshold_between_sales_and_stock_large_base_stock = ratio_threshold_between_sales_and_stock_large_base_stock
        self.num_of_days_for_seasonal_train = num_of_days_for_seasonal_train
        self.num_of_days_for_non_seasonal_train = num_of_days_for_non_seasonal_train
        self.freq = freq
        self.num_of_min_rows_for_calculation_base_stock = num_of_min_rows_for_calculation_base_stock

    def preprocess_data(self, sales_sparse: pd.DataFrame, stock_sparse: pd.DataFrame) -> tuple:
        """
        Preprocess data for base stock calculation
        Args:
            sales_sparse: df with the following columns: [date, 'sku, store', sku, store, sales]
            stock_sparse: df with the following columns: ['sku, store', sku, store, from_date, to_date, stock]

        return:
            sales_sparse: df with the following columns: [date, sku_store, sales]
            stock_sparse: df with the following columns: [sku_store, from_date, to_date, stock]
            sales_over_months_for_seasonal_items: df with the following columns: [sku_store, sales_over_months] with
            seasonal items
        """
        sales_sparse['date'] = pd.to_datetime(sales_sparse['date'])
        sales_sparse, stock_sparse = rename_and_filter_relevant_columns(sales_sparse, stock_sparse)
        stock_sparse = add_sku_store_column(stock_sparse)
        max_sales_date = pd.to_datetime(sales_sparse['date'].max()).strftime('%Y-%m-%d')
        stock_sparse["to_date"] = stock_sparse["to_date"].astype(str).replace('2099-12-31', max_sales_date)
        sales_sparse = add_sku_store_column(sales_sparse)
        sales_sparse = date_parse_sales_data(sales_sparse)
        stock_sparse = date_parse_stock_data(stock_sparse)
        start_date_of_interval = (pd.to_datetime(stock_sparse['to_date'].max()) - pd.Timedelta(days=700)).strftime(
            '%Y-%m-%d')
        relevant_sku_stock_in_stock_interval_time = generate_relevant_sku_stock_in_stock_interval_time(sales_sparse,
                                                                                                       stock_sparse,
                                                                                                       start_date_of_interval)
        return sales_sparse, stock_sparse, relevant_sku_stock_in_stock_interval_time


    def get_base_stock(self, train: pd.DataFrame) -> float:
        """
        Get base stock for large base stock items
        Args:
            train: df with the following columns: [date, "sku, store", 3_days_sales, sales, stock]

        Returns: base stock value

        """
        base_stock_train_value = calculate_base_stock(train, self.ratio_threshold_between_sales_and_stock)
        if base_stock_train_value > self.big_base_stock_value_base_stock_need_to_handel:
            # raise error if base stock is less than config.big_base_stock_value_base_stock_need_to_handel
            if base_stock_train_value <= self.big_base_stock_value_base_stock_need_to_handel:
                raise ValueError("base stock is less than config.big_base_stock_value_base_stock_need_to_handel")
            # raise if value is too big
            if base_stock_train_value > self.huge_base_stock:
                raise ValueError("base stock is too big")
            base_stock_train_value = \
                handle_big_base_stock(train, self.ratio_threshold_between_sales_and_stock_large_base_stock)
        return base_stock_train_value


    def calculate_base_stock_loop(self,sales_sparse: pd.DataFrame, stock_sparse: pd.DataFrame,
                                  sales_over_months_for_seasonal_items: pd.DataFrame,
                                  relevant_ids: list,
                                  min_date, max_date) -> dict:
        """
        Run pipline for base stock calculation
        Args:
            sales_sparse:  df with the following columns: [date, "sku, store", sales , sku]
            **date is in the format of datetime( to_date)
            stock_sparse:  df with the following columns: [sku_store, from_date, to_date, stock]
            sales_over_months_for_seasonal_items:  df with the following columns: [item, sales_over_months] with


        Returns:
            results: dict with the key of sku_store and the value of base stock value


        """
        if "valid_from_date" in stock_sparse.columns:
            stock_sparse = stock_sparse.rename(columns={"valid_from_date": "from_date"})
        if "valid_to_date" in stock_sparse.columns:
            stock_sparse = stock_sparse.rename(columns={"valid_to_date": "to_date"})
        print("1", stock_sparse)
        results = {}
        i = 0
        start_date_of_to_date_in_stock = (pd.to_datetime(stock_sparse['to_date'].max()) - pd.Timedelta(days=365)).strftime(
            '%Y-%m-%d')
        len_filtered_data = len(relevant_ids)
        print(" ids:")
        for sku_store in relevant_ids:
            results[sku_store] = {}
            i += 1

            item = generate_item_column(sku_store)
            stock_sku_store = filter_data_sku_store_and_start_date(stock_sparse, sku_store, start_date_of_to_date_in_stock)
            sales_sku_store, df_sku_store_sales_stock = generate_sku_store_sales_stock(sku_store, sales_sparse,
                                                                                       stock_sku_store, self.freq)
            if len(df_sku_store_sales_stock) > 0 and len(sales_sku_store) > 0:
                df_sku_store_sales_stock = merge_sales_and_stock(sales_sku_store, df_sku_store_sales_stock)
                if item in sales_over_months_for_seasonal_items[static_config.item_str].unique().astype(str):
                    train = generate_train_slice(df_sku_store_sales_stock, self.num_of_days_for_seasonal_train)
                else:
                    train = generate_train_slice(df_sku_store_sales_stock, self.num_of_days_for_non_seasonal_train)
                train = add_3_days_column(train)
                train = train[(train[static_config.date_str] <= max_date) & (train[static_config.date_str] >= min_date)]
                if len(train) >= self.num_of_min_rows_for_calculation_base_stock:
                    base_stock_train_value = self.get_base_stock(train)
                    results[sku_store]['base_stock'] = base_stock_train_value
                    if item in sales_over_months_for_seasonal_items[static_config.item_str].unique().astype(str):
                        results[sku_store]['description'] = "base stock calculated for seasonal item"
                    else:
                        results[sku_store]['description'] = "base stock calculated for non seasonal item"
                else:
                    results[sku_store]['base_stock'] = train[static_config.sales_str].max() + 1
                    results[sku_store]['description'] = "not enough train data so base stock is max sales + 1"

            elif ((len(df_sku_store_sales_stock) == 0) and (len(sales_sku_store) > 0)):
                results[sku_store]['base_stock'] = max(sales_sku_store[static_config.sales_str] + 1)
                results[sku_store]['description'] = "stock data is empty and base stock is max sales + 1"

            elif (len(sales_sku_store) == 0) and (len(df_sku_store_sales_stock) > 0):
                results[sku_store]['base_stock'] = df_sku_store_sales_stock[static_config.stock_str].min()
                results[sku_store]['description'] = "sales data is empty and base stock is min stock"

            else:
                results[sku_store]['base_stock'] = np.nan
                results[sku_store]['description'] = "sales and stock data are empty so base stock is nan"

            print("", i, "/",  len_filtered_data, "id:",sku_store, "base stock:", results[sku_store]['base_stock'] ,
                  "description:", results[sku_store]['description'])
        return results

    def calculate_base_stock_with_sales_stock_data_fixed(self, all_sales_stock: pd.DataFrame,
                                                       sales_over_months_for_seasonal_items: pd.DataFrame,
                                                         list_of_ids) -> dict:
        """
        Run pipline for base stock calculation
        """
        results = {}
        len_ids = len(list_of_ids)
        i = 0
        for id in list_of_ids:
            item = all_sales_stock[all_sales_stock[static_config.sku_store_str] == id]["item"].iloc[0]
            results[id] = {}
            i += 1
            print("i", i, "out of", len_ids)
            df_id_sales_stock = all_sales_stock[all_sales_stock[static_config.sku_store_str] == id]
            id_sales = df_id_sales_stock[static_config.sales_str]
            if len(df_id_sales_stock) > 0 and len(id_sales) > 0:
                if item in sales_over_months_for_seasonal_items[static_config.item_str].unique().astype(str):
                    train = generate_train_slice(df_id_sales_stock,
                                                 self.num_of_days_for_seasonal_train)
                else:
                    train = generate_train_slice(df_id_sales_stock,
                                                 self.num_of_days_for_non_seasonal_train)
                train = add_3_days_column(train)
                if len(train) >= self.num_of_min_rows_for_calculation_base_stock:
                    base_stock_train_value = self.get_base_stock(train)
                    results[id]['base_stock'] = base_stock_train_value
                    if item in sales_over_months_for_seasonal_items[static_config.item_str].unique().astype(str):
                        results[id]['description'] = "base stock calculated for seasonal item"
                    else:
                        results[id]['description'] = "base stock calculated for non seasonal item"
                else:
                    results[id]['base_stock'] = train[static_config.sales_str].max() + 1
                    results[id]['description'] = "not enough train data so base stock is max sales + 1"
            else:
                results[id]['base_stock'] = np.nan
                results[id]['description'] = "sales or stock data is empty"

            print("", i, "/", len_ids, "id:", id, "base stock:", results[id]['base_stock'], "max_id_sales", id_sales.max(),
                  "description:", results[id]['description'])
        return results