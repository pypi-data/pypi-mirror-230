from src.sdatta_learning.feature_selection.logger import create_logger
from configs import global_static_config as static_config
def feature_selection_pipeline(feature_selection_process, data):

    dict_features = {}
    list_of_new_ids = []
    print(" ids:")
    i = 1
    logger = create_logger(feature_selection_process.log_location)
    for id in data['item, store'].unique():

        id_data = data[data['item, store'] == id]
        if len(set(id_data['sales'])) > 1:
            dict_features[id] = {}
            model = feature_selection_process.tree_model
            selected_features = feature_selection_process.run_pipline_feature_selection(id_data, id, model, logger=logger)
            selected_features += [static_config.store_str, static_config.item_str, static_config.date_str]
            dict_features[id]["selected_features"] = selected_features
            # TODO: fix the linear feature selection ValueError: seasonal_periods must be larger than 1.
            # best_method, best_weight, best_window = feature_selection_process.run_pipline_linear_feature(id_data, selected_features, model)
            # dict_features[id]["best_method"] = best_method
            print(i, "/", len(data[static_config.item_store_str].unique()), " id: ", id, " selected features: ", selected_features)

            logger.info("final feature selection pipeline for id: %s, features: %s", id, dict_features[id])
        else:
            list_of_new_ids.append(id)
            logger.info("id: %s has only one value unique in train sales or train in empty df", id)
            print(i, "/", len(data[static_config.item_store_str].unique()), " id: ", id, " not enough data")
        i += 1
    return dict_features, list_of_new_ids