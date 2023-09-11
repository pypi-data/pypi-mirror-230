import numpy as np
import matplotlib.pyplot as plt
from hbmo.metrics import rmse, mae, mse

class HBMO:
    def __init__(self, n_param, calc_function, high = None, low = None, metric = 'rmse', init_pop = 1000, s_min_queen = 1, s_max_queen = 1e6, s_alpha = 0.981, n_workers = 10, seed = None):
        self.n_param = n_param
        self.calc_function = calc_function
        if seed:
            np.random.seed(seed)
        metrics = [rmse, mse, mae]
        metrics_name = ['rmse', 'mse', 'mae']
        assert metric in metrics_name, 'metric must be one of the following values: "rmse", "mse", "mae"'
        self.metric = metrics[metrics_name.index(metric)]
        self.high = np.ones((n_param,), dtype = np.float32) if not high else np.array(high, dtype = np.float32)
        self.low = np.ones((n_param,), dtype = np.float32) * -1 if not low else np.array(low, dtype = np.float32)
        assert len(self.high) == n_param and len(self.low) == n_param, 'length of high and low must be equal to n_param'
        self.init_pop = init_pop
        self.s_min_queen = s_min_queen
        self.s_max_queen = s_max_queen
        self.s_alpha = s_alpha
        self.n_workers = n_workers
        self.n_drone = init_pop // 2
        self.n_sperm = self.n_drone * 3
        self.errors = []
    
    def _fit(self, data, targets, iterations):
        population = np.random.rand(self.init_pop, self.n_param) * (self.high - self.low) + self.low
        pop_rmse = np.stack(list(map(lambda x:self.metric(targets, self.calc_function(x, data)), population)))
        population_r = np.concatenate((population, pop_rmse[:, None]), axis = 1)
        population_r = np.array(sorted(population_r, key = lambda x:x[-1]))
        member_best = population_r[0]
        queen_param = member_best[None, :-1]
        queen_rmse = population_r[0,-1]
        drone_pop = population_r[1:self.n_drone + 1]
        errors = []
        #r2_scores = []
        for i in range(iterations):
            queen_speed = np.random.rand() * (self.s_max_queen - self.s_min_queen) + self.s_min_queen
            sperm_mat = [member_best]
            while queen_speed > self.s_min_queen and len(sperm_mat) < self.n_sperm:
                selected_drone_ind = int(np.random.rand() * drone_pop.shape[0])
                selected_drone = drone_pop[selected_drone_ind]
                selected_drone_rmse = selected_drone[-1]
                prob = np.exp(-np.abs(queen_rmse - selected_drone_rmse) / queen_speed)
                if prob > np.random.rand():
                    sperm_mat.append(selected_drone)
                queen_speed = self.s_alpha * queen_speed
            sperm_mat = np.stack(sperm_mat)
            brood = member_best[:-1] + np.random.rand(sperm_mat.shape[0], sperm_mat.shape[1] - 1) * (sperm_mat[:, :-1] - member_best[:-1])
            brood_prediction = []
            for j in range(len(brood)):
                worker_brood = member_best[:-1] + np.random.rand(self.n_workers, self.n_param) * (brood[j] - member_best[:-1])
                worker_brood = np.concatenate((worker_brood, brood[None, j]), axis = 0)
                worker_brood_pred = np.stack(list(map(lambda x:self.calc_function(x, data), worker_brood)))
                worker_brood_rmse = self.metric(targets, worker_brood_pred)
                best_ind = np.argmin(worker_brood_rmse)
                brood[j] = worker_brood[best_ind]
                brood_prediction.append(worker_brood_pred[best_ind])
            brood_prediction = np.stack(brood_prediction)
            brood_rmse = self.metric(targets, brood_prediction)
            brood_r = np.concatenate((brood, brood_rmse[:, None]), axis = 1)
            brood_r = np.array(sorted(brood_r, key = lambda x:x[-1]))
            member_best = brood_r[0]
            errors.append(member_best[-1])
            queen_param = member_best[None, :-1]
            drone_pop = brood_r[1:]
        self.queen = queen_param
        self.errors = errors
    
    def fit(self, data, targets, iterations = 20):
        self._fit(data, targets, iterations)
    
    def predict(self, data):
        return np.stack(list(map(lambda x:self.calc_function(x, data), self.queen)))[0]
    
    def plot_progress(self):
        plt.plot(self.errors)

class MHBMO:
    def __init__(self, n_param, calc_function, high = None, low = None, metric = 'rmse', init_pop = 1000, s_min_queen = 1, s_max_queen = 1e6, s_alpha = 0.981, n_workers = 10, seed = None):
        self.n_param = n_param
        self.calc_function = calc_function
        if seed:
            np.random.seed(seed)
        metrics = [rmse, mse, mae]
        metrics_name = ['rmse', 'mse', 'mae']
        assert metric in metrics_name, 'metric must be one of the following values: "rmse", "mse", "mae"'
        self.metric = metrics[metrics_name.index(metric)]
        self.high = np.ones((n_param,), dtype = np.float32) if not high else np.array(high, dtype = np.float32)
        self.low = np.ones((n_param,), dtype = np.float32) * -1 if not low else np.array(low, dtype = np.float32)
        assert len(self.high) == n_param and len(self.low) == n_param, 'length of high and low must be equal to n_param'
        self.init_pop = init_pop
        self.s_min_queen = s_min_queen
        self.s_max_queen = s_max_queen
        self.s_alpha = s_alpha
        self.n_workers = n_workers
        self.n_drone = init_pop // 2
        self.n_sperm = self.n_drone * 3
        self.errors = []
    
    def _fit(self, data, targets, iterations):
        population = np.random.rand(self.init_pop, self.n_param) * (self.high - self.low) + self.low
        pop_rmse = np.stack(list(map(lambda x:self.metric(targets, self.calc_function(x, data)), population)))
        population_r = np.concatenate((population, pop_rmse[:, None]), axis = 1)
        population_r = np.array(sorted(population_r, key = lambda x:x[-1]))
        member_best = population_r[0]
        queen_param = member_best[None, :-1]
        queen_rmse = population_r[0,-1]
        drone_pop = population_r[1:self.n_drone + 1]
        errors = []
        #r2_scores = []
        for i in range(iterations):
            queen_speed = np.random.rand() * (self.s_max_queen - self.s_min_queen) + self.s_min_queen
            sperm_mat = []
            while queen_speed > self.s_min_queen and len(sperm_mat) < self.n_sperm:
                selected_drone_ind = int(np.random.rand() * drone_pop.shape[0])
                selected_drone = drone_pop[selected_drone_ind]
                selected_drone_rmse = selected_drone[-1]
                prob = np.exp(-np.abs(queen_rmse - selected_drone_rmse) / queen_speed)
                if prob > np.random.rand():
                    sperm_mat.append(selected_drone)
                queen_speed = self.s_alpha * queen_speed
            sperm_mat = np.stack(sperm_mat)
            brood = member_best[:-1] + np.random.rand(sperm_mat.shape[0], sperm_mat.shape[1] - 1) * (sperm_mat[:, :-1] - member_best[:-1])
            sp1, sp2, sp3 = brood[np.random.choice(range(len(brood)), 3, replace = False)]
            im1 = sp1 + np.random.rand(*sp1.shape) * (sp2 - sp3)
            im2 = member_best[:-1] + np.random.rand(*sp1.shape) * (sp2 - sp3)
            gamma1, gamma2, gamma3 = np.random.rand(3, sp1.shape[0])
            br1 = np.where(gamma1 <= gamma2, im1, sp1)
            br2 = np.where(gamma3 <= gamma2, im2, member_best[:-1])
            br_param = np.stack([br1, br2, member_best[:-1]])
            br_best = br_param[np.argmin(self.metric(targets, np.stack(list(map(lambda x:self.calc_function(x, data), br_param)))))]
            brood = np.concatenate([brood, br_best[None, ...]], axis = 0)
            brood_prediction = []
            for j in range(len(brood)):
                worker_brood = member_best[:-1] + np.random.rand(self.n_workers, self.n_param) * (brood[j] - member_best[:-1])
                worker_brood = np.concatenate((worker_brood, brood[None, j]), axis = 0)
                worker_brood_pred = np.stack(list(map(lambda x:self.calc_function(x, data), worker_brood)))
                worker_brood_rmse = self.metric(targets, worker_brood_pred)
                best_ind = np.argmin(worker_brood_rmse)
                brood[j] = worker_brood[best_ind]
                brood_prediction.append(worker_brood_pred[best_ind])
            brood_prediction = np.stack(brood_prediction)
            brood_rmse = self.metric(targets, brood_prediction)
            brood_r = np.concatenate((brood, brood_rmse[:, None]), axis = 1)
            brood_r = np.array(sorted(brood_r, key = lambda x:x[-1]))
            member_best = brood_r[0]
            errors.append(member_best[-1])
            queen_param = member_best[None, :-1]
            drone_pop = brood_r[1:]
        self.queen = queen_param
        self.errors = errors
    
    def fit(self, data, targets, iterations = 20):
        self._fit(data, targets, iterations)
    
    def predict(self, data):
        return np.stack(list(map(lambda x:self.calc_function(x, data), self.queen)))[0]
    
    def plot_progress(self):
        plt.plot(self.errors)