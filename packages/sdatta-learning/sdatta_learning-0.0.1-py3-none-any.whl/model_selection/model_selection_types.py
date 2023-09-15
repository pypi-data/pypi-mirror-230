from datetime import datetime

class TimeWeightedModel:
    def __init__(self, models, weights):
        self.models = models
        self.weights = weights

    def predict(self, data):
        predictions = [model.predict(data) for model in self.models]
        return sum(w * p for w, p in zip(self.weights, predictions))


class MAEWeightedModel:
    def __init__(self, models, maes):
        self.models = models
        self.weights = self._compute_weights(maes)

    def _compute_weights(self, maes):
        # We invert the MAEs to get weights since lower MAE is better
        inv_maes = [1 / mae for mae in maes]
        total_inv_mae = sum(inv_maes)
        return [inv_mae / total_inv_mae for inv_mae in inv_maes]

    def predict(self, data):
        predictions = [model.predict(data) for model in self.models]
        return sum(w * p for w, p in zip(self.weights, predictions))


class MAETimeWeightedModel:
    def __init__(self, models, maes, end_dates):
        self.models = models
        # Convert string end_dates to datetime objects
        time_weights = self._compute_time_weights(end_dates)
        mae_weights = self._compute_mae_weights(maes)
        self.weights = [mw * tw for mw, tw in zip(mae_weights, time_weights)]

    def _compute_mae_weights(self, maes):
        inv_maes = [1 / mae for mae in maes]
        total_inv_mae = sum(inv_maes)
        return [inv_mae / total_inv_mae for inv_mae in inv_maes]

    def _compute_time_weights(self, end_dates):
        end_dates = [datetime.strptime(date, "%Y-%m-%d") for date in end_dates]
        max_date = max(end_dates)
        time_diffs = [(max_date - date).days for date in end_dates]
        inv_time_diffs = [1 / (diff + 1) for diff in time_diffs]  # adding 1 to avoid division by 0
        total_inv_time_diff = sum(inv_time_diffs)
        return [inv_time_diff / total_inv_time_diff for inv_time_diff in inv_time_diffs]

    def predict(self, data):
        predictions = [model.predict(data) for model in self.models]
        return sum(w * p for w, p in zip(self.weights, predictions))

class TopNMAEModel:
    def __init__(self, models, maes, n):
        self.models = models
        self.n = min(n, len(models))
        self.top_n_indices = self._get_top_n_indices(maes)

    def _get_top_n_indices(self, maes):
        # Get the indices of the models_base_stock_tasks with the lowest MAEs
        sorted_indices = sorted(range(len(maes)), key=lambda i: maes[i])
        return sorted_indices[:self.n]

    def predict(self, data):
        top_n_predictions = [self.models[i].predict(data) for i in self.top_n_indices]
        return sum(top_n_predictions) / self.n


class TopLastFoldModel:
    def __init__(self, models, end_dates, n):
        self.models = models
        self.end_dates = [datetime.strptime(date, "%Y-%m-%d") for date in end_dates]
        self.n = min(n, len(models))
        self.last_n_indices = self._get_last_n_indices()

    def _get_last_n_indices(self):
        # Get the indices of the models_base_stock_tasks with the most recent end_dates
        sorted_indices = sorted(range(len(self.end_dates)), key=lambda i: self.end_dates[i], reverse=True)
        return sorted_indices[:self.n]

    def predict(self, data):
        last_n_predictions = [self.models[i].predict(data) for i in self.last_n_indices]
        return sum(last_n_predictions) / self.n
