import pandas as pd
from configs import global_static_config as static_config

def get_set_of_sku_that_been_sold_up_to_n_in_the_last_m_years_in_span_of_q_days(sku_data, n=3, m=1, q=3):
    """
    This function will return a set of sku that been sold up to 3 (amount) in the last year in span of 3 days
    Args:
        sku_data: a dataframe of the sku data\
        n: the amount of sales
        m: the number of years
        q: the number of days

    Returns:
        a set of skus that been sold up to 3 (amount) in the last year in span of 3 days
    """
    max_date = sku_data[static_config.date_str].max()
    split_date_ = max_date - pd.DateOffset(years=m, days=q)
    sku_data_temp = sku_data[sku_data[static_config.date_str] >= split_date_]
    sku_data_temp[f'{q}d_sales'] = sku_data_temp.groupby([static_config.sku_store_str])[static_config.sales_str].rolling(n).sum().reset_index().fillna(sku_data[static_config.sales_str])[static_config.sales_str]
    sku_data_temp = sku_data_temp[sku_data_temp[f'{q}d_sales'] <= n]
    return set(sku_data_temp[static_config.sku_store_str].unique())


def get_set_of_skus_that_were_not_sold_in_the_past_n_years(n, sku_data):
    """
    This function will return a set of skus that were not sold in the past n years
    Args:
        n: the number of years
        sku_data: a dataframe of the sku data

    Returns:
        a set of skus that were not sold in the past n years
    """

    return set(sku_data[static_config.sku_store_str].unique()) - set(sku_data[sku_data[static_config.date_str] >= (sku_data[static_config.date_str].max() - pd.DateOffset(years=n))][static_config.sku_store_str].unique())


def get_remainder(sku_sales_data, n=3, m=1, q=3):
    """
    This function will return a remainder list:
    the remainder list is a dictionary of the following structure:
    {weak_selling_sku: set_of_sku_ids, slow_moving_sku: set_of_sku_ids, dead_sku: set_of_sku_ids}
    Args:
        n: the amount of sales
        m: the number of years
        q: the number of days

    Returns:
        a remainder list, a dictionary of the following structure:
        {weak_selling_sku: set_of_sku_ids, slow_moving_sku: set_of_sku_ids, dead_sku: set_of_sku_ids}

    Note:
        the sku sales data is loaded from clearml, it has the following columns:
        "sku, store", date, sales
    """
    set_of_skus_that_were_not_sold_in_the_past_2_years = get_set_of_skus_that_were_not_sold_in_the_past_n_years(2, sku_sales_data)
    set_of_skus_that_were_not_sold_in_the_past_1_years = get_set_of_skus_that_were_not_sold_in_the_past_n_years(1, sku_sales_data)
    set_of_sku_that_been_sold_up_to_3_in_the_last_year_in_span_of_3_days = get_set_of_sku_that_been_sold_up_to_n_in_the_last_m_years_in_span_of_q_days(sku_sales_data, n=n, m=m, q=q)
    weak_selling_skus = set_of_sku_that_been_sold_up_to_3_in_the_last_year_in_span_of_3_days - set_of_skus_that_were_not_sold_in_the_past_1_years
    weak_selling_skus = sku_sales_data[(sku_sales_data[static_config.sku_store_str].isin(weak_selling_skus)) & (sku_sales_data[static_config.date_str] >= (sku_sales_data[static_config.date_str].max() - pd.DateOffset(years=1)))]
    weak_selling_skus[f'{n}d_sales'] = weak_selling_skus.groupby(static_config.sku_store_str)[static_config.sales_str].rolling(n).sum().reset_index(0, drop=True).fillna(weak_selling_skus[static_config.sales_str])
    weak_selling_skus = weak_selling_skus.groupby([static_config.sku_store_str])[f'{n}d_sales'].max().to_dict()
    slow_moving_sku = set_of_skus_that_were_not_sold_in_the_past_1_years - set_of_skus_that_were_not_sold_in_the_past_2_years
    return {"weak_selling_sku": weak_selling_skus,
            "slow_moving_sku": slow_moving_sku,
            "dead_sku": set_of_skus_that_were_not_sold_in_the_past_2_years,
            "sku_id_tuned": set(set(weak_selling_skus.keys()) | set(slow_moving_sku) | set(set_of_skus_that_were_not_sold_in_the_past_2_years))}


def tune_weak_selling_level_prediction(dict_of_predictions, weak_selling_sku):
    """
    This function takes 2 dictionaries of the following structure:
    dict_of_predictions = {item_id: {prediction_level: {sku: base_stock_level}}}
    weak_selling_sku = {sku_id: max_sales_in_the_past_year}
    the function will tune the dict_of_predictions by taking the minimum value between the base_stock_level and the max_sales_in_the_past_year, each time for each prediction level.
    if base_stock_level is greater than max_sales_in_the_past_year, the results will count this difference as a remainder in a dictionary format in the following structure:
    {item_id: {prediction_level: {sku: base_stock_level - max_sales_in_the_past_year}}}


    Args:
        weak_selling_sku: a dictionary of the following structure: {sku_id: max_sales_in_the_past_year}
        dict_of_predictions: a dictionary of the following structure: {item_id: {prediction_level: {sku: base_stock_level}}}

    Returns:
        2 dictionaries of the following structure:
        dict_of_predictions = {tem_id: {prediction_level: {sku: base_stock_level}}} (tuned)
        remainder = {item_id: {prediction_level: sum({sku: base_stock_level - max_sales_in_the_past_year})}} (the difference between the base_stock_level and the max_sales_in_the_past_year
        in case base_stock_level is greater than max_sales_in_the_past_year)
    """
    remainder = {}
    for item_id, prediction_level_dict in dict_of_predictions.items():
        store = item_id.split(", ")[1]
        for prediction_level, sku_dict in prediction_level_dict.items():
            for sku, base_stock_level in sku_dict.items():
                sku_id = str(sku) + ", " + str(store)
                if sku_id in weak_selling_sku:
                    if base_stock_level > weak_selling_sku[sku_id]:
                        if item_id not in remainder:
                            remainder[item_id] = {}
                        if prediction_level not in remainder[item_id]:
                            remainder[item_id][prediction_level] = 0
                        remainder[item_id][prediction_level] += base_stock_level - weak_selling_sku[sku_id]
                        dict_of_predictions[item_id][prediction_level][sku] = weak_selling_sku[sku_id]
    return dict_of_predictions, remainder


def tune_slow_moving_level_prediction(dict_of_predictions, slow_moving_sku_id_set, threshold=2):
    """
    This function takes a dictionary of the following structure:
    dict_of_predictions = {item_id: {prediction_level: {sku: base_stock_level}}}

    The function will tune the dict_of_predictions by taking the minimum value between the base_stock_level and the threshold, each time for each prediction level.
    if base_stock_level is greater than threshold, the results will count this difference as a remainder in a dictionary format in the following structure:
    {item_id: {prediction_level: {sku: base_stock_level - threshold}}}

    Args:
        dict_of_predictions: a dictionary of the following structure: {item_id: {prediction_level: {sku: base_stock_level}}}
        slow_moving_sku_id_set: a set of sku ids that are considered slow moving
        threshold: the threshold to tune the base_stock_level to

    Returns:
        a dictionary and a remainder dictionary of the following structure:
        dict_of_predictions = {item_id: {prediction_level: {sku: base_stock_level}}} (tuned)
        remainder = {item_id: {prediction_level: sum({sku: base_stock_level - threshold})}} (the difference between the base_stock_level and the threshold

    """
    remainder = {}
    for item_id, prediction_level_dict in dict_of_predictions.items():
        store = item_id.split(", ")[1]
        for prediction_level, sku_dict in prediction_level_dict.items():
            for sku, base_stock_level in sku_dict.items():
                if str(sku) + ", " + str(store) in slow_moving_sku_id_set:
                    if base_stock_level > threshold:
                        if item_id not in remainder:
                            remainder[item_id] = {}
                        if prediction_level not in remainder[item_id]:
                            remainder[item_id][prediction_level] = 0
                        remainder[item_id][prediction_level] += base_stock_level - threshold
                        dict_of_predictions[item_id][prediction_level][sku] = threshold
    return dict_of_predictions, remainder


def remainder_sum(list_of_remainders):
    """
    This function takes a list of dictionaries of the following structure:
    list_of_remainders = [{item_id: {prediction_level: remainder}}]
    This function will sum the remainders for each item_id and prediction_level and return a dictionary of the following structure:
    {item_id: {prediction_level: sum(remainder)}}
    Args:
        list_of_remainders: a list of dictionaries of the following structure: {item_id: {prediction_level: remainder}}

    Returns:
        a dictionary of the following structure: {item_id: {prediction_level: sum(remainder)}}

    *Note:
    not all the dictionaries contains the same item_id and prediction_level, the function will sum all the remainders for each item_id and prediction_level.
    if a dictionary doesn't contain a specific item_id and prediction_level, its summation will be 0.
    """
    remainder_dict = {}
    for remainder in list_of_remainders:
        for item_id, prediction_level_dict in remainder.items():
            for prediction_level, remainder_value in prediction_level_dict.items():
                if item_id not in remainder_dict:
                    remainder_dict[item_id] = {}
                if prediction_level not in remainder_dict[item_id]:
                    remainder_dict[item_id][prediction_level] = 0
                remainder_dict[item_id][prediction_level] += remainder_value
    return remainder_dict


def update_sku_level_prediction_based_on_remainder(dict_of_predictions, remainder_dict, sku_id_set):
    """
    This function takes 2 dictionaries of the following structure:
    dict_of_predictions = {item_id: {prediction_level: {sku: base_stock_level}}}
    remainder_dict = {item_id: {prediction_level: remainder}}


    Args:
        dict_of_predictions: a dictionary of the following structure: {item_id: {prediction_level: {sku: base_stock_level}}}
        remainder_dict: a dictionary of the following structure: {item_id: {prediction_level: sum(remainder)}}
        sku_id_set: a set of sku ids that are tuned in advanced, the function will not tune these sku ids

    Returns:
        a dictionary of the following structure: {item_id: {prediction_level: {sku: base_stock_level}}}
    """
    for item_id, prediction_level_dict in dict_of_predictions.items():
        store = item_id.split(', ')[1]
        for prediction_level, sku_dict in prediction_level_dict.items():
            prediction_level_dict[prediction_level] = update_valid_sku_level_prediction_based_on_remainder(sku_dict, remainder_dict[item_id][prediction_level], store, sku_id_set)
    return dict_of_predictions


def get_valid_sku(skus_set, store, sku_store_filter):
    """
    this function take a set of skus (set of strs) and a store (str) and a sku_store_filter (set of strs, of the format: "sku, store")
    the function will return a set of skus that satisfy the following condition:
    the combination of the sku and the store is not in sku_store_filter.

    Args:
        skus_set: a set of skus (set of strs) - represents the skus that are considered for prediction
        store: a store (str) - represents the store that is considered for prediction
        sku_store_filter: a set of strs, of the format: "sku, store" - represents the skus that are not considered for prediction


    Returns:
        a set of skus that satisfy the following condition:
        the combination of the sku and the store is not in sku_store_filter.

    Example:
        skus_set = {'sku1', 'sku2', 'sku3'}
        store = 'store1'
        sku_store_filter = {'sku1, store1', 'sku2, store2'}
        return = {'sku3'}
    """
    valid_sku_stores = set(sku + ', ' + store for sku in skus_set) - sku_store_filter
    return set(sku_store.split(', ')[0] for sku_store in valid_sku_stores)


def update_valid_sku_level_prediction_based_on_remainder(sku_level_pred, remainder, valid_skus):
    """
    This function takes the dictionary of the following structure:
    sku_level_pred = {sku: base_stock_level}, and updates the base_stock_level for each sku in the valid_skus set
    based on the remainder in the following way:
    the remainder is spread evenly across the valid_skus in an iterative hierarchical manner.

    Args:
        sku_level_pred: a dictionary of the following structure: {sku: base_stock_level}
        remainder: a positive integer - represents the remainder that needs to be spread across the valid_skus
        valid_skus: a set of skus (set of strs) - represents the skus that are considered for prediction

    Returns:
        a dictionary of the following structure: {sku: base_stock_level}

    Notes:
        the remainder is a positive integer, and the base_stock_level is a positive integer.

    Examples:
        1.
        sku_level_pred = {'sku1': 6, 'sku2': 5, 'sku3': 5}
        remainder = 3
        valid_skus = {'sku1', 'sku2'}
        return = {'sku1': 7, 'sku2': 6, 'sku3': 5}
        2.
        sku_level_pred = {'sku1': 6, 'sku2': 5, 'sku3': 5}
        remainder = 1
        valid_skus = {'sku1', 'sku2'}
        return = {'sku1': 7, 'sku2': 5, 'sku3': 5}
        3.
        sku_level_pred = {'sku1': 5, 'sku2': 6, 'sku3': 5}
        remainder = 1
        valid_skus = {'sku1', 'sku2'}
        return = {'sku1': 5, 'sku2': 7, 'sku3': 5}

    """
    if remainder == 0:
        return sku_level_pred
    if len(valid_skus) == 0:
        return sku_level_pred
    if len(valid_skus) == 1:
        sku = valid_skus.pop()
        sku_level_pred[sku] += remainder
        return sku_level_pred

    remainder_per_sku = remainder // len(valid_skus)
    remainder = remainder % len(valid_skus)
    for sku in valid_skus:
        sku_level_pred[sku] += remainder_per_sku
    valid_skus = sort_by_dict_val(sku_level_pred, valid_skus & set(sku_level_pred.keys()))
    while remainder > 0:
        sku_level_pred[valid_skus.pop(0)] += 1
        remainder -= 1
    return sku_level_pred


def sort_by_dict_val(dict_of_values, valid_set):
    """
    This function takes dictionary of the following structure:
    dict_of_values = {key: value(int)}, and a set of keys (valid_set)
    the function will return a sorted list of keys based on the values in dict_of_values.

    Args:
        dict_of_values: a dictionary of the following structure: {key: value(int)}
        valid_set: a set of keys (valid_set)

    Returns:
        a sorted list of keys based on the values in dict_of_values.

    Examples:
        1.
        dict_of_values = {'sku1': 4, 'sku2': 6, 'sku3': 5}
        valid_set = {'sku1', 'sku2'}
        return = ['sku2', 'sku1']
    """
    return sorted(valid_set, key=lambda sku: dict_of_values[sku], reverse=True)


def main(prediction_dict, sku_sales_data, n=3, m=1, q=3):
    """
    This function takes a dictionary of the following structure:
    prediction_dict = {item_id: {prediction_level: {sku: base_stock_level}}}
    and tunes the base_stock_level for each sku in the following way:
    first calculate the remainder for each item_id, prediction_level pair and get the valid sku_id set.
    then, for each item_id, prediction_level pair, update the base_stock_level for each sku in the valid sku_id set
    based on the remainder in the following way:
    the remainder is spread evenly across the valid_skus in an iterative hierarchical manner.

    Args:
        prediction_dict: a dictionary of the following structure: {item_id: {prediction_level: {sku: base_stock_level}}}
        n: a positive integer - represents the number for threshold for the weak selling sku
        m: a positive integer - represents the time window for the weak selling sku
        q: a positive integer - represents the number of days to aggregate on when checking for weak selling sku

    Returns:
        a dictionary of the following structure: {item_id: {prediction_level: {sku: base_stock_level}}}
    """
    res_dict = get_remainder(sku_sales_data, n, m, q)
    prediction_dict, remainder_weak = tune_weak_selling_level_prediction(prediction_dict, res_dict['weak_selling_sku'])
    prediction_dict, remainder_slow = tune_slow_moving_level_prediction(prediction_dict, res_dict['slow_moving_sku'])
    prediction_dict, remainder_dead = tune_slow_moving_level_prediction(prediction_dict, res_dict['dead_sku'], threshold=1)
    remainder = remainder_sum([remainder_weak, remainder_slow, remainder_dead])
    valid_set = res_dict['sku_id_tuned']
    for item_id in prediction_dict:
        for prediction_level in prediction_dict[item_id]:
            try:
                prediction_dict[item_id][prediction_level] = update_valid_sku_level_prediction_based_on_remainder(
                    prediction_dict[item_id][prediction_level], remainder[item_id][prediction_level], valid_set)
            except:
                continue
    return prediction_dict
