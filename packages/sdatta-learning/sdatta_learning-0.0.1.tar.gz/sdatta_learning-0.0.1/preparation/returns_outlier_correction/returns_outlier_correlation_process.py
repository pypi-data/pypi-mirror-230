from palmers_agents_general.db_handler import PostgresHandler

def create_f_sales_v_without_outliers_returns_query(start_date, end_date, table_name, sales_table_name,
                                                    drop_before_create=True):
    drop_before_create = f'DROP TABLE IF EXISTS {table_name};' if drop_before_create else ''
    create_query = f"""
                WITH
                    group_data AS (
                        SELECT mat_no AS sku, outlet AS store, quantity AS sales, date, time,
                            LAG(quantity) OVER (
                                PARTITION BY outlet, mat_no, date
                                ORDER BY (date || ' ' || time)::timestamp
                                RANGE BETWEEN INTERVAL '2 hours' PRECEDING AND CURRENT ROW
                            ) AS prior_purchase_quantity,
                            LAG((date || ' ' || time)::timestamp) OVER (
                                PARTITION BY outlet, mat_no, date
                                ORDER BY (date || ' ' || time)::timestamp
                            ) AS prior_purchase_time
                        FROM {sales_table_name}
                        WHERE date >= \'{start_date}\' AND date <= \'{end_date}\' 
                    ),
                    interim_data AS (
                        SELECT sku, store, sales, date, time,
                            CASE
                                WHEN sales < 0 AND
                                     ((date || ' ' || time)::timestamp - prior_purchase_time <= INTERVAL '2 hours') AND
                                     (prior_purchase_quantity + sales >= 0)
                                THEN TRUE
                                ELSE FALSE
                            END AS prior_purchase_within_two_hours
                        FROM group_data
                    ),
                final_data AS (
                        SELECT
                            sku, store, date, time,sales,
                            CASE
                                WHEN sales < 0 AND NOT prior_purchase_within_two_hours THEN 0
                                ELSE sales
                            END AS corrected_sales
                        FROM interim_data
                    )
                SELECT *
                INTO {table_name}
                FROM final_data;
            """
    return drop_before_create + create_query


def create_f_sales_without_outliers(config_dict):
    table_name = f'{config_dict["pg_schema"]}.f_sales_v_without_outliers_returns_{config_dict["start_date"]}_{config_dict["end_date"]}'.replace(
        '-', '_')

    with PostgresHandler(host=config_dict["pg_host"], port=config_dict["pg_port"], user=config_dict["pg_user"],
                         password=config_dict["pg_password"],
                         dbname=config_dict["pg_database"]) as handler:
        query = create_f_sales_v_without_outliers_returns_query(config_dict["start_date"],
                                                                config_dict["end_date"],
                                                                table_name,
                                                                sales_table_name=config_dict["sales_table_name"],
                                                                drop_before_create=True)

        df = handler.execute_update(query, params=None)
    config_dict['raw_sales_table_name'] = table_name
    return table_name, config_dict


# def main():
#     config_dict = config.params
#     # config_dict['start_date'] = '2023-07-23'
#     #    config_dict['end_date'] = '2023-07-23'
#     table_name = create_f_sales_without_outliers(config_dict)
#     print(table_name)
#     print('finished')
#
#
# if __name__ == '__main__':
#     main()
