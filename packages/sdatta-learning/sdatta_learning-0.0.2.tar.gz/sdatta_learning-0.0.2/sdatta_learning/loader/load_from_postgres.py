
from palmers_agents_general.db_handler import PostgresHandler
import warnings


def get_sales_between_dates(store_list, pg_host, pg_port, pg_user, pg_password, pg_database, agg_sales_table_name, start_date, end_date):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        select_query = f"""SELECT DISTINCT * 
                          FROM {agg_sales_table_name} 
                          WHERE store in %s
                          AND date >= \'{start_date}\' AND date <= \'{end_date}\'
                        """

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sales_df = handler.read_sql_query(select_query, params=(tuple(store_list),))
    return sales_df

def get_stock_between_dates(store_list, pg_host, pg_port, pg_user, pg_password, pg_database, pg_schema, start_date, end_date):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        select_query = f"""SELECT * 
                          FROM {pg_schema}.mbew
                          WHERE bwkey in %s
                          AND valid_to_date <= \'{end_date}\' AND valid_from_date >= \'{start_date}\'
                        """

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            stock_df = handler.read_sql_query(select_query, params=(tuple(store_list),))
    return stock_df



def get_sales_between_dates_and_stores(pg_host, pg_port, pg_user, pg_password, pg_database, start_date, end_date, formatted_stores):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        query = f"""SELECT * 
                     FROM f_sales_v
                     WHERE date >= '{start_date}' AND date <= '{end_date}' AND outlet IN ({formatted_stores})
                   """
        sales_sparse = handler.read_sql_query(query, params=None)
    return sales_sparse



def get_stock_between_dates_and_stores(pg_host, pg_port, pg_user, pg_password, pg_database, start_date, formatted_stores):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                             dbname=pg_database) as handler:
            query = f"""SELECT * 
                         FROM mbew
                         WHERE valid_to_date >= '{start_date}' AND bwkey IN ({formatted_stores})
                       """
            stock_sparse = handler.read_sql_query(query, params=None)
    return stock_sparse


def get_items_status_table(pg_host, pg_port, pg_user, pg_password, pg_database):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        query = """SELECT * 
                   FROM items_status
                """
        ids_status = handler.read_sql_query(query, params=None)
    return ids_status



def get_sales_for_models_between_dates_and_stores(table_name, pg_host, pg_port, pg_user, pg_password, pg_database, start_date, end_date, formatted_stores):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        query = f"""SELECT * 
                     FROM {table_name}
                     WHERE date >= '{start_date}' AND date <= '{end_date}' AND store IN ({formatted_stores})
                   """
        data = handler.read_sql_query(query, params=None)
    return data