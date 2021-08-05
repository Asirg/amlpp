from lightgbm import LGBMRegressor

from typing import List, Callable

import pandas as pd
import os

class Optimizer(object):
    def __init__(self, X_train:pd.DataFrame, Y_train:pd.DataFrame, 
                       X_test:pd.DataFrame, Y_test:pd.DataFrame,
                       rating_func:Callable,
                       quantity_trials:int,
                       params:List[str] = {}
                       ):

        self.X_train, self.Y_train = X_train, Y_train
        self.X_test, self.Y_test = X_test, Y_test
        self.rating_func = rating_func

        self.iter = 0
        self.quantity_trials = quantity_trials

        self.add_params = params

class SklearnOptimizer(Optimizer):
    def __init__(self, X_train:pd.DataFrame, Y_train:pd.DataFrame, 
                       X_test:pd.DataFrame, Y_test:pd.DataFrame,
                       rating_func:Callable, quantity_trials:int,
                       model:dict, model_params:Callable, params:List[str] = {}):

        super().__init__(X_train, Y_train, X_test, Y_test, 
                        rating_func, quantity_trials, params)
        self.model = model
        self.model_params = model_params

    def __call__(self, trial):
        model = self.model(**self.model_params(trial, {})).fit(self.X_train, self.Y_train)
        self.iter += 1
        progress_bar(self.iter, self.quantity_trials)
        return self.rating_func(self.Y_test, model.predict(self.X_test))

class LGBMOptimizer(Optimizer):
    def __init__(self, X_train:pd.DataFrame, Y_train:pd.DataFrame, 
                       X_test:pd.DataFrame, Y_test:pd.DataFrame,
                       rating_func:Callable, quantity_trials:int,
                       model:dict, model_params:Callable, params:List[str] = {}):

        super().__init__(X_train, Y_train, X_test, Y_test, 
                        rating_func, quantity_trials, params)
        self.model = model
        self.model_params = model_params

    def __call__(self, trial):
        model = LGBMRegressor(**self.model_params(trial))
        model.fit(self.X_train, self.Y_train, eval_set = [(self.X_test, self.Y_test)], verbose = False, 
                **self.add_params, early_stopping_rounds = 300)
        self.iter += 1
        progress_bar(self.iter, self.quantity_trials)
        return self.rating_func(self.Y_test, model.predict(self.X_test))

def progress_bar(iter:int, quantity:int):
    progress = round(iter/quantity*100, 2)
    if progress % 20 == 0:
        print(f"[{iter}/{quantity} - {progress}%]")