# -*- coding: utf-8 -*-


class Paramizer(object):

    @classmethod
    def LinearRegression(cls, **kwargs):
        return {
            'fit_intercept': [True],
            'normalize': [False, True],
            'positive': [False, True]
        }

    @classmethod
    def LassoRegression(cls, **kwargs):
        return {
            'alpha': [1.0],
            'fit_intercept': [True, False],
            'normalize': [True, False],
            'selection': ['cyclic', 'random'],
            'positive': [True, False],
            'max_iter': [i for i in range(80, 180, 10)]
        }

    @classmethod
    def BayesianRegression(cls, **ElasticNetRegressionkwargs):
        return {'n_iter': [i for i in range(250, 350, 10)]}

    @classmethod
    def ElasticNetRegression(cls, **kwargs):
        return {
            'l1_ratio': [(i / 100) for i in range(0, 100, 5)],
            'alpha': [(i / 100) for i in range(0, 9, 1)]
        }

    @classmethod
    def RidgeRegression(cls, **kwargs):
        return {
            #'l1_ratio': [0],
            'alpha': [(i / 100) for i in range(0, 100, 5)]
        }

    @classmethod
    def LogisticRegression(cls, **kwargs):
        return {
            'solver': ['saga'],
            'l1_ratio': [(i / 100) for i in range(0, 100, 5)],
            'penalty': ['elasticnet'],
            'C': [(i / 100) for i in range(1, 10000, 10)],
        }

    @classmethod
    def RandomForestRegressor(cls, **kwargs):
        return {
            'n_estimators': [i for i in range(10, 100, 10)],
            'max_depth': [i for i in range(3, 50, 1)],
            'min_samples_split': [i for i in range(20, 100, 1)]
        }

    @classmethod
    def NvSVRModel(cls, **kwargs):
        return {
            'kernel': ['linear'],
            'C': [(i / 100) for i in range(1, 10000, 100)],
            'gamma': [(i / 10) for i in range(1, 100, 1)],
        }

    @classmethod
    def XGBRegressor(cls, **kwargs):
        return {
            'max_depth': [i for i in range(2, 10, 1)],
            'n_estimators': [i for i in range(50, 150, 10)],
            'learning_rate': [(i / 100) for i in range(1, 10, 1)]
        }

    @classmethod
    def LGBMRegressor(cls, **kwargs):
        return {
            'max_depth': [i for i in range(2, 10, 1)],
            'n_estimators': [i for i in range(50, 150, 10)],
            'learning_rate': [(i / 100) for i in range(1, 10, 1)],
            'num_leaves': [i for i in range(20, 80, 1)],
            'min_data_in_leaf': [i for i in range(20, 100, 1)],
            'lambda_l2': [(i / 100) for i in range(1, 100, 1)]
        }

    @classmethod
    def ExtraTreesRegressor(cls, **kwargs):
        return {
            'n_estimators': [i for i in range(80, 180, 10)],
            'max_depth': [i for i in range(3, 5, 2)],
            'max_features': ['auto', 'sqrt', 'log2']
        }

    @classmethod
    def BaggingRegressor(cls, **kwargs):
        return {
            'n_estimators': [i for i in range(80, 180, 10)],
            'max_depth': [i for i in range(3, 5, 2)],
            'max_features': ['auto', 'sqrt', 'log2']
        }

    @classmethod
    def AdaBoostRegressor(cls, **kwargs):
        return {
            'n_estimators': [i for i in range(50, 150, 10)],
            'learning_rate': [(i / 10) for i in range(1, 10, 2)],
            'loss': ['linear', 'square', 'exponential']
        }

    @classmethod
    def DecisionTreeRegressor(cls, **kwargs):
        return {
            'criterion': ['mse', 'friedman_mse', 'mae', 'poisson'],
            'splitter': ['best', 'random']
        }

    @classmethod
    def GradientBoostingRegressor(cls, **kwargs):
        return {
            'n_estimators': [i for i in range(50, 150, 10)],
            'learning_rate': [(i / 10) for i in range(1, 10, 2)],
            'loss': ['ls', 'lad', 'huber', 'quantile'],
            'criterion': ['friedman_mse', 'mse', 'mae']
        }
