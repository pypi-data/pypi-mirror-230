from catboost import CatBoostRegressor


def predict_all_future_dates(dict_of_final_models, X, dict_of_features, columns_to_drop):
    all_future_dates_final_predictions = {}
    for date in X['date'].dt.strftime('%Y-%m-%d').unique():
        relevant_date_X = X[X['date'] == date]
        all_future_dates_final_predictions[date] = predict_all_ids(dict_of_final_models, relevant_date_X, dict_of_features,
                                                                   columns_to_drop)
    return all_future_dates_final_predictions


def predict_all_ids(dict_of_final_models, X_for_pred, dict_of_features, columns_to_drop):
    all_ids_final_predictions = {}
    print(" ids:")
    for id in X_for_pred["item, store"].unique():
        features_list = dict_of_features[id]['selected_features']
        features_list_new = [x for x in features_list if x not in columns_to_drop]
        X_for_pred_for_id = X_for_pred[X_for_pred["item, store"] == id]
        prediction = dict_of_final_models[id]['final_model'].predict(X_for_pred_for_id[features_list_new])[0]
        all_ids_final_predictions[id] = prediction
        print(id, "prediction:", prediction)
    return all_ids_final_predictions