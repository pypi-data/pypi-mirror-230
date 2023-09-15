from src.preparation.create_aggregated_sales.created_aggregated_process import *
from src.preparation.returns_outlier_correction.returns_outlier_correlation_process import *
from src.preparation.the_sorting_bonnet.the_sorting_bonnet_process import *
from src.preparation.fill_zeroes.fill_zeros_process import *
def created_aggregated_pipeline(config_dict):
    print(" created aggregated")
    table_name, config_dict = create_aggregated_sales(config_dict)
    print(' created_aggregated_table_name:', table_name)
    print(' finished')
    return config_dict

def returns_outlier_correlation_pipeline(config_dict):
    print(" returns outlier correlation")
    table_name, config_dict = create_f_sales_without_outliers(config_dict)
    print(' returns_outlier_correlation_table_name:', table_name)
    print(' finished')
    return config_dict



def the_sorting_bonnet_pipeline(config_dict, sales_df, drop_before_create_bool=True):
    print(" the sorting bonnet")
    # sales_df = get_sales_between_dates(config_dict['stores'],
    #                                    config_dict['pg_host'],
    #                                    config_dict['pg_port'],
    #                                    config_dict['pg_user'],
    #                                    config_dict['pg_password'],
    #                                    config_dict['pg_database'],
    #                                    config_dict['sales_filled_table'],
    #                                    config_dict['start_date'],
    #                                    config_dict['end_date'])
    sales_df['item'] = sales_df['sku'].str[:-3]
    sales_df['item, store'] = sales_df['item'].astype(str) + ', ' + sales_df['store'].astype(str)
    sales_df_g = sales_df.groupby([config_dict['item_store_col'], 'date']).agg({'sales': 'sum'}).reset_index()
    id_column = config_dict['item_store_col']
    date_column = config_dict['date_col']
    sales_df.sort_values(by=[id_column, date_column], inplace=True)
    print(" calculate sparse rate")
    res = calc_sparse_rate(sales_df_g, config_dict['start_date'], id_col=config_dict['item_store_col'], date_col=config_dict['date_col']
                     , sales_col=config_dict['sales_col'], avg_factor=config_dict['avg_factor'], minimum_sparse_val=config_dict['minimum_sparse_val'])
    print(" get sparse and non sparse sales")
    avg_factor = config_dict['avg_factor']
    sparse_sales = res[f'sparse_{avg_factor}d_sales'][[id_column]].drop_duplicates()
    non_sparse_sales = res[f'non_sparse_{avg_factor}d_sales'][[id_column]].drop_duplicates()

    # add column named item which trims the last 3 digits from the sku
    # add columns named models_type which is equal 'models' for sparse sales and 'base_stock' for the other
    # sparse_sales['item'] = sparse_sales['sku'].str[:-3]
    # non_sparse_sales['item'] = non_sparse_sales['sku'].str[:-3]
    sparse_sales['models_type'] = 'base_stock'
    non_sparse_sales['models_type'] = 'models'

    data = pd.concat([sparse_sales, non_sparse_sales])
    data = sales_df.merge(data[['item, store', 'models_type']], on=['item, store'], how='left')
    sku_list = data['sku'].astype(str).unique().tolist()
    print(" take artikelstamm table")
    artikelstamm_table = get_artikelstamm_table(table_name=config_dict['artikelstamm_table_name'],
                                                sku_list=sku_list,
                                                pg_host=config_dict['pg_host'],
                                                pg_port=config_dict['pg_port'],
                                                pg_user=config_dict['pg_user'],
                                                pg_password=config_dict['pg_password'],
                                                pg_database=config_dict['pg_database'])
    print(" merge artikelstamm table with fashion grade")
    data = pd.merge(data, artikelstamm_table[['article', 'fashiongrade']], left_on='sku', right_on='article', how='left')
    data = data.drop(columns=['article']).rename(columns={'fashiongrade': 'fashion_grade'})
    data['fashion_grade'] = data['fashion_grade'].fillna('no grade')
    data['last_update_time'] = datetime.now()
    create_table_and_insert_rows_from_df(table_name=config_dict['item_status_table'].split('.')[1],
                                           table_schema=config_dict['pg_schema'],
                                           df=data,
                                           pg_user=config_dict['pg_user'],
                                           pg_password=config_dict['pg_password'],
                                           pg_host=config_dict['pg_host'],
                                           pg_port=config_dict['pg_port'],
                                           pg_database=config_dict['pg_database'],
                                           drop_before_create=drop_before_create_bool,
                                           comment=None)
    # show all columns in df
    pd.set_option('display.max_columns', None)

    print(' finished')
    return data


def fill_zeroes_pipeline(config_dict, drop_before_create_bool=True):

    print(" fill zeroes")
    sales_df = get_sales_between_dates(config_dict['stores'],
                                       config_dict['pg_host'],
                                       config_dict['pg_port'],
                                       config_dict['pg_user'],
                                       config_dict['pg_password'],
                                       config_dict['pg_database'],
                                       config_dict['agg_sales_table_name'],
                                       config_dict['start_date'],
                                       config_dict['end_date'])

    stock_df = get_stock_between_dates(config_dict['stores'],
                                        config_dict['pg_host'],
                                        config_dict['pg_port'],
                                        config_dict['pg_user'],
                                        config_dict['pg_password'],
                                        config_dict['pg_database'],
                                       'public',
                                        config_dict['start_date'],
                                        config_dict['end_date'])

    id_list = None
    sales_with_zeroes_df = fill_sales_with_zeroes(sales_df, stock_df, config_dict['start_date'], config_dict['end_date'], id_list=id_list)

    timestamp = pd.Timestamp.now().strftime("%Y_%m_%d_%H_%M_%S")
    create_sales_with_zeroes_table_name = f'sales_filled_{timestamp}'
    if len(create_sales_with_zeroes_table_name) > 63:
        create_sales_with_zeroes_table_name = create_sales_with_zeroes_table_name[:63]

    print(" create_sales_with_zeroes_table_name:", create_sales_with_zeroes_table_name)

    stores_encoded = '_'.join(config_dict['stores'])
    comment = f'{config_dict["start_date"]}_{config_dict["end_date"]}_{stores_encoded}'

    create_table_and_insert_rows_from_df(create_sales_with_zeroes_table_name, config_dict['pg_schema'],
                                         sales_with_zeroes_df, config_dict['pg_user'], config_dict['pg_password'],
                                         config_dict['pg_host'], config_dict['pg_port'], config_dict['pg_database'],
                                         drop_before_create=drop_before_create_bool, comment=comment)

    print(' finished')
    config_dict['sales_filled_table'] = 'dev.' + create_sales_with_zeroes_table_name
    #TODO: enrich with price, other.
    return config_dict, sales_with_zeroes_df