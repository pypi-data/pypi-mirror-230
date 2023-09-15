import os
from datetime import datetime

import pandas as pd
from palmers_agents_general.db_handler import PostgresHandler

#TODO: use the module palmers_agents_general.db_handler instead.
#TODO: export this function into a module and import it, instead of copying the code.
def create_table_and_insert_rows_from_df(table_name, table_schema, df, pg_user, pg_password, pg_host, pg_port, pg_database, drop_before_create=False, comment=None):
        from sqlalchemy import create_engine
        import io

        engine = create_engine(
            f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}', connect_args={'options': f'-csearch_path={table_schema}'})
        df.head(0).to_sql(table_name, engine, if_exists='replace' if drop_before_create else 'append', index=False)

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

def get_sales_between_dates(store_list, pg_host, pg_port, pg_user, pg_password, pg_database, table_name, start_date, end_date):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        select_query = f"""SELECT DISTINCT * 
                          FROM {table_name} 
                          WHERE store in %s
                          AND date >= \'{start_date}\' AND date <= \'{end_date}\'
                        """

        sales_df = handler.read_sql_query(select_query, params=(tuple(store_list),))
    return sales_df
#TODO: export this function into a module and import it, instead of copying the code.
def calc_sparse_rate(df: pd.DataFrame, start_date: str, id_col: str, date_col: str, sales_col: str, avg_factor: int = 7, minimum_sparse_val: float=0.3) -> dict:
    """
    this function calculates the sparse rate of the sales column and the sparse rate of the average of the sales column.
    the sparse rate is the rate of nonzero values in the column.
    the function returns a dictionary of 4 dataframes:
    1. sparse_sales - the rows where the sparse rate of the sales column is lower than the minimum_sparse_val
    2. non_sparse_sales - the rows where the sparse rate of the sales column is higher than the minimum_sparse_val
    3. sparse_{avg_factor}d_sales - the rows where the sparse rate of the average of the sales column is lower than the minimum_sparse_val
    4. non_sparse_{avg_factor}d_sales - the rows where the sparse rate of the average of the sales column is higher than the minimum_sparse_val
    Args:
        df: (pd.DataFrame) the dataframe to calculate the sparse rate on - multivariate time series
        start_date: (str) the date to start the calculation from
        id_col: (str) the name of the id column
        date_col: (str) the name of the date column
        sales_col: (str) the name of the sales column
        avg_factor: (int) the average factor to calculate the average of the sales column
        minimum_sparse_val: (float) the minimum sparse rate to filter the dataframes by
    Returns:
        res: (dict) a dictionary of 4 dataframes:
            1. sparse_sales - the rows where the sparse rate of the sales column is lower than the minimum_sparse_val
            2. non_sparse_sales - the rows where the sparse rate of the sales column is higher than the minimum_sparse_val
            3. sparse_{avg_factor}d_sales - the rows where the sparse rate of the average of the sales column is lower than the minimum_sparse_val
            4. non_sparse_{avg_factor}d_sales - the rows where the sparse rate of the average of the sales column is higher than the minimum_sparse_val
    Notes:
        1. the function assumes that the dataframe is sorted by the (id, date) columns multiindex convention but not grouped by them.
        2. the function assumes that the dataframe has all the columns mentioned in the arguments with the respective names and types.
        3. the dataframe is assumed to contain both the zero sales and the nonzero sales
        4. the dataframe is assumed to be aggregated by the id column and the date column
    """
    res = {}
    df = df[df[date_col] >= start_date]
    df['date'] = pd.to_datetime(df[date_col])
    df[f'{avg_factor}d_sales'] = df.groupby(id_col)[sales_col].rolling(avg_factor).mean().reset_index(0, drop=True)
    df['sparse_rate_sales'] = df.groupby(id_col)[sales_col].transform(lambda x: len(x[x !=0])/len(x))
    df[f'{avg_factor}d_sales'] = df.groupby(id_col)[sales_col].rolling(avg_factor).mean().reset_index(0, drop=True)
    df[f'sparse_rate_{avg_factor}d_sales'] = df.groupby(id_col)[f'{avg_factor}d_sales'].transform(lambda x: len(x[x != 0])/len(x))
    res['sparse_sales'] = df[df['sparse_rate_sales'] <= minimum_sparse_val]
    res['non_sparse_sales'] = df[df['sparse_rate_sales'] > minimum_sparse_val]
    res[f'sparse_{avg_factor}d_sales'] = df[df[f'sparse_rate_{avg_factor}d_sales'] <= minimum_sparse_val]
    res[f'non_sparse_{avg_factor}d_sales'] = df[df[f'sparse_rate_{avg_factor}d_sales'] > minimum_sparse_val]
    return res


def get_artikelstamm_table(table_name,sku_list, pg_host, pg_port, pg_user, pg_password, pg_database):
    with PostgresHandler(host=pg_host, port=pg_port, user=pg_user, password=pg_password,
                         dbname=pg_database) as handler:
        select_query = f"""SELECT  * 
                          FROM {table_name}
                          WHERE article in %s
                        """

        artikelstamm = handler.read_sql_query(select_query, params=(tuple(sku_list),))
    return artikelstamm
#
# config_dict = {'start_date': '2023-08-23',
#                'end_date': '2023-09-01',
#                'item_status_table': 'dev.items_status_pipe',
#                'pg_schema': 'dev',
#                'stores': ['51'],
#                'pg_port': os.environ.get('PT_PG_PORT', '5432'),
#                'pg_user': os.environ.get('PT_PG_USER', 'datatiger'),
#                'pg_password': os.environ.get('PT_PG_PASSWORD', 'Hwhiupwj6SZ4Sq'),
#                'pg_host': os.environ.get('PT_PG_HOST', 'sdatta-pg.postgres.database.azure.com'),
#                'pg_database': os.environ.get('PT_PG_DATABASE', 'postgres'),
#                'id_col': 'sku, store',
#                'date_col': 'date',
#                'sales_col': 'sales',
#                'avg_factor': 7,
#                'minimum_sparse_val': 0.3,
#                'sales_table_name': os.environ.get('PT_SALES_TABLE_NAME', 'public.f_sales_v'),
#                'artikelstamm_table_name': 'l_artikelstamm',}
# sku_list = ['100060035000001', '100518540000001']
# if __name__ == '__main__':
#     artikelstamm_table = get_artikelstamm_table(table_name=config_dict['artikelstamm_table_name'],
#                                                 sku_list=sku_list,
#                                                 pg_host=config_dict['pg_host'],
#                                                 pg_port=config_dict['pg_port'],
#                                                 pg_user=config_dict['pg_user'],
#                                                 pg_password=config_dict['pg_password'],
#                                                 pg_database=config_dict['pg_database'])
#     print(artikelstamm_table)