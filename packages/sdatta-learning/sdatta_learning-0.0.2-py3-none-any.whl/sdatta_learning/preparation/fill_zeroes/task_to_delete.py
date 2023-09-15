import os

from palmers_agents_general.db_handler import PostgresHandler


def get_sales_between_dates(store_list, pg_host, pg_port, pg_user, pg_password, pg_database, agg_sales_table_name,
                            start_date, end_date):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        select_query = f"""SELECT DISTINCT * 
                          FROM {agg_sales_table_name} 
                          WHERE store in %s
                          AND date >= \'{start_date}\' AND date <= \'{end_date}\'
                        """

        sales_df = handler.read_sql_query(select_query, params=(tuple(store_list),))
    return sales_df


def get_stock_between_dates(store_list, pg_host, pg_port, pg_user, pg_password, pg_database, pg_schema, start_date,
                            end_date):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        select_query = f"""SELECT * 
                          FROM {pg_schema}.mbew
                          WHERE bwkey in %s
                          AND valid_to_date >= \'{start_date}\' AND valid_from_date <= \'{end_date}\'
                        """

        sales_df = handler.read_sql_query(select_query, params=(tuple(store_list),))
    return sales_df

def get_sales_between_dates(pg_host, pg_port, pg_user, pg_password, pg_database, table_name,
                            start_date, end_date):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        query = f"""SELECT DISTINCT * 
                          FROM {table_name} 
                          WHERE date >= \'{start_date}\' AND date <= \'{end_date}\'
                        """

        sales_df = handler.read_sql_query(query, params=None)
    return sales_df


def main():
    config_dict = {'start_date': '2022-01-01',
                   'end_date': '2023-01-01',
                   'sales_filled_table_name': 'dev.sales_filled_2023_07_31_09_27_13',
                   'pg_schema': 'dev',
                   'stores': ['51', '168', '152', '119', '100'],
                   'pg_port': os.environ.get('PT_PG_PORT', '5432'),
                   'pg_user': os.environ.get('PT_PG_USER', 'datatiger'),
                   'pg_password': os.environ.get('PT_PG_PASSWORD', 'Hwhiupwj6SZ4Sq'),
                   'pg_host': os.environ.get('PT_PG_HOST', 'sdatta-pg.postgres.database.azure.com'),
                   'pg_database': os.environ.get('PT_PG_DATABASE', 'postgres'),
                   }

    sales_df = get_sales_between_dates(config_dict['stores'],
                                       config_dict['pg_host'],
                                       config_dict['pg_port'],
                                       config_dict['pg_user'],
                                       config_dict['pg_password'],
                                       config_dict['pg_database'],
                                       config_dict['sales_filled_table_name'],
                                       config_dict['start_date'],
                                       config_dict['end_date'])
    print(sales_df.head())
    print('finished')


if __name__ == '__main__':
    main()
