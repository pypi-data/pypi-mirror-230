import os

import pandas as pd
from palmers_agents_general.db_handler import PostgresHandler

from src.preparation.fill_zeroes.fill_sales_with_zeroes import fill_sales_with_zeroes


def get_sales_between_dates(store_list, pg_host, pg_port, pg_user, pg_password, pg_database, agg_sales_table_name, start_date, end_date):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        select_query = f"""SELECT DISTINCT * 
                          FROM {agg_sales_table_name} 
                          WHERE store in %s
                          AND date >= \'{start_date}\' AND date <= \'{end_date}\'
                        """

        sales_df = handler.read_sql_query(select_query, params=(tuple(store_list),))
    return sales_df

def get_stock_between_dates(store_list, pg_host, pg_port, pg_user, pg_password, pg_database, pg_schema, start_date, end_date):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        select_query = f"""SELECT * 
                          FROM {pg_schema}.mbew
                          WHERE bwkey in %s
                          AND valid_to_date >= \'{start_date}\' AND valid_from_date <= \'{end_date}\'
                        """

        stock_df = handler.read_sql_query(select_query, params=(tuple(store_list),))
    return stock_df

#TODO: use the module palmers_agents_general.db_handler instead.
def create_table_and_insert_rows_from_df(table_name, table_schema, df, pg_user, pg_password, pg_host, pg_port, pg_database, drop_before_create=True, comment=None):
        from sqlalchemy import create_engine
        import io

        engine = create_engine(
            f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}', connect_args={'options': f'-csearch_path={table_schema}'})
        df.head(0).to_sql(table_name, engine, if_exists='replace' if drop_before_create else 'append', index=False)  # truncates the table

        conn = engine.raw_connection()
        cur = conn.cursor()

        # Adding a comment to the table
        table_comment_sql = f"COMMENT ON TABLE {table_name} IS '{comment}';"
        cur.execute(table_comment_sql)

        output = io.StringIO()
        df.to_csv(output, sep='\t', header=False, index=False)
        output.seek(0)
        contents = output.getvalue()
        cur.copy_from(output, table_name, null="")  # null values become ''
        conn.commit()
        cur.close()
        conn.close()






