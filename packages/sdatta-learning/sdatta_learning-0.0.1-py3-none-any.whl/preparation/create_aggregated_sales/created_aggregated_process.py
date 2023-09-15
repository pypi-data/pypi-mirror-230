import os

from palmers_agents_general.db_handler import PostgresHandler


def create_aggregated_sales_query(table_name, raw_sales_table_name, start_date, end_date, drop_before_create=True):
    drop_before_create = f'DROP TABLE IF EXISTS {table_name};' if drop_before_create else ''
    create_query = f"""
                CREATE TABLE IF NOT EXISTS {table_name} AS
                SELECT date, sku, store, (sku || ', ' || store) AS \"sku, store\", sum(corrected_sales) sales
                FROM {raw_sales_table_name}
                WHERE date >= \'{start_date}\' AND date <= \'{end_date}\'
                GROUP BY date, store, sku
                ORDER BY date ASC;
            """
    return drop_before_create + create_query

def create_aggregated_sales(config_dict):
    table_name = f'{config_dict["pg_schema"]}.f_sales_v_agg_{config_dict["start_date"]}_{config_dict["end_date"]}'.replace(
        '-', '_')
    with PostgresHandler(host=config_dict["pg_host"], port=config_dict["pg_port"], user=config_dict["pg_user"],
                         password=config_dict["pg_password"],
                         dbname=config_dict["pg_database"]) as handler:
        query = create_aggregated_sales_query(table_name, config_dict["raw_sales_table_name"],
                                              config_dict["start_date"],
                                              config_dict["end_date"],
                                              drop_before_create=True)

        handler.execute_update(query, params=None)
    config_dict['agg_sales_table_name'] = table_name
    return table_name, config_dict


# def main():
#     config_dict = {'start_date': '2023-01-01',
#                    'end_date': '2023-08-20',
#                    'raw_sales_table_name': 'dev.f_sales_v_without_outliers_returns_2023_01_01_2023_08_20',
#                    'pg_schema': 'dev',
#                    'stores': ['51', '168', '152', '119', '100'],
#                    'pg_port': os.environ.get('PT_PG_PORT', '5432'),
#                    'pg_user': os.environ.get('PT_PG_USER', 'datatiger'),
#                    'pg_password': os.environ.get('PT_PG_PASSWORD', 'Hwhiupwj6SZ4Sq'),
#                    'pg_host': os.environ.get('PT_PG_HOST', 'sdatta-pg.postgres.database.azure.com'),
#                    'pg_database': os.environ.get('PT_PG_DATABASE', 'postgres'),
#                    }
#
#     table_name = create_aggregated_sales(config_dict)
#     #    print(df.shape[0])
#     print(table_name)
#     print('finished')
#
#
# if __name__ == '__main__':
#     main()
