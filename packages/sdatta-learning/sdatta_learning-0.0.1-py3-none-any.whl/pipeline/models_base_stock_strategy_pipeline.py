import pandas as pd
from src.strategy_base_stock.model_simulator_base_stock.optimal_simulator import Simulator
from src.strategy_base_stock.model_simulator_base_stock.sku_level_logic_tune import main
import numpy as np


def models_base_stock_strategy_fit_pipeline(sales_data,
                                            all_ids_final_one_model,
                                        data_with_features,
                                        features_dict,
                                        split_train_test=0.8):
    dict_for_model_simulator_base_stock = {}
    for id in all_ids_final_one_model.keys():
        data_with_features_id = data_with_features[data_with_features['item, store'] == id]
        date_range = pd.to_datetime(data_with_features_id['date']).max() - pd.to_datetime(
            data_with_features_id['date']).min()
        train_duration = date_range * split_train_test
        split_date = (pd.to_datetime(data_with_features_id['date']).min() + train_duration).strftime(
            '%Y-%m-%d')
        train_data = data_with_features_id[data_with_features_id['date'] <= split_date]
        test_data = data_with_features_id[data_with_features_id['date'] > split_date]
        y_train_real = train_data['sales']
        y_test_real = test_data['sales']
        y_train_pred = all_ids_final_one_model[id]['final_model'].predict(
            train_data[features_dict[id]['selected_features']])
        y_test_pred = all_ids_final_one_model[id]['final_model'].predict(
            test_data[features_dict[id]['selected_features']])
        y_train_real = pd.Series(y_train_real, index=train_data.index)
        y_test_real = pd.Series(y_test_real, index=test_data.index)
        y_train_pred = pd.Series(np.ceil(y_train_pred), index=train_data.index)
        y_test_pred = pd.Series(np.ceil(y_test_pred), index=test_data.index)
        y_train_real.index.name = 'date'
        y_test_real.index.name = 'date'
        y_train_pred.index.name = 'date'
        y_test_pred.index.name = 'date'
        dict_for_model_simulator_base_stock[id] = {'y_train_real': y_train_real,
                                                   'y_test_real': y_test_real,
                                                   'y_train_pred': y_train_pred,
                                                   'y_test_pred': y_test_pred}
    simulator = Simulator(horizon_forwards=1, horizon_backwards=5)
    all_data = simulator.preprocess_data(sales_data)
    data_size_item_sku_store_ = simulator.load_data_size_item_sku_store(all_data)
    optimal_stock_levels_sku = simulator.main_simulation(data_size_item_sku_store_, all_data, dict_for_model_simulator_base_stock)
    all_data['sku, store'] = all_data['sku'].astype(str) + ', ' + all_data['store'].astype(str)
    final_dict = main(optimal_stock_levels_sku, all_data)
    return final_dict


def models_base_stock_strategy_predict_pipeline(all_predictions, optimal_stock_level_for_models_dict):
    for date in all_predictions:
        for item_store in all_predictions[date]:
            value = all_predictions[date][item_store]
            all_predictions[date][item_store] = int(np.ceil(value))
    final_sku_store_base_stock = {}
    for date in all_predictions:
        final_sku_store_base_stock[date] = {}
        for item_store in all_predictions[date]:
            pred_item_store = all_predictions[date][item_store]
            store = item_store.split(', ')[1]
            print(f"item_store: {item_store}")
            dict_to_add = optimal_stock_level_for_models_dict[item_store][pred_item_store]
            # add store to all keys
            dict_to_add = {f'{key}, {store}': value for key, value in dict_to_add.items()}
            final_sku_store_base_stock[date].update(dict_to_add)
    return final_sku_store_base_stock