# -*- coding: utf-8 -*-
import json, pdb, time
import pandas as pd
import numpy as np
from jdw.kdutils.logger import kd_logger
from jdw.mfc.entropy.catalyst.evolution.paramizer import Paramizer
from ultron.tradingday import *
from ultron.factor.data.transformer import Transformer
from ultron.factor.data.processing import factor_processing
from ultron.factor.data.winsorize import winsorize_normal
from ultron.factor.data.standardize import standardize
from ultron.optimize.model.loader import load_model
from ultron.factor.fitness.metrics import Metrics
from ultron.optimize.geneticist.genetic import Gentic
from ultron.optimize.geneticist.engine import Engine
from ultron.factor.dimension.corrcoef import FCorrType
from ultron.factor.dimension import DimensionCorrcoef
from ultron.ump.similar.corrcoef import ECoreCorrType

default_models = [
    'RandomForestRegressor', 'LGBMRegressor', 'XGBRegressor', 'SGDRegression',
    'RidgeRegression', 'ExtraTreesRegressor', 'AdaBoostRegressor',
    'GradientBoostingRegressor'
]

GREATER_MAPPING = {
    'score': True,
    'forward_score': True,
    'evs': False,
    'mae': False,
    'mse': False,
    'r2_score': True
}


class Base(object):

    def __init__(self,
                 yields_class,
                 factors_class,
                 universe_class,
                 dummy_class,
                 industry_class,
                 thresh,
                 universe,
                 factor_columns,
                 industry_name,
                 industry_level,
                 is_weighted=True,
                 dummy_name=None,
                 offset=0,
                 horizon=0,
                 factors_normal=True,
                 callback_save=None,
                 is_loop=False,
                 model_sets=None,
                 params_sets=None,
                 yield_name='returns'):
        self._yields_class = yields_class
        self._factors_class = factors_class
        self._universe_class = universe_class
        self._industry_class = industry_class
        #self._factor_columns = factor_columns
        self._factors_normal = factors_normal
        self._is_weighted = is_weighted
        self._offset = offset
        self._horizon = horizon
        self._universe = universe
        self._thresh = thresh
        self._yield_name = yield_name
        self._industry_name = industry_name
        self._industry_level = industry_level
        self._callback_save = callback_save
        self._dummy_class = dummy_class
        self._dummy_name = dummy_name
        self._results = None
        self._total_data = None
        self._best_programs = None
        self._gentic_class = Engine if is_loop else Gentic
        self._model_sets = default_models if model_sets is None else model_sets
        self._params_sets = params_sets
        self._transformer = Transformer(factor_columns)

    def industry_fillna(self, industry_data, factors_data):
        return factors_data

    def fetch_returns(self, begin_date, end_date, universe=None):
        yields = self._yields_class()
        yields_data = yields.fetch_yileds(universe=universe,
                                          start_date=begin_date,
                                          end_date=end_date,
                                          offset=self._offset,
                                          name='ret')
        return yields_data

    def fetch_yields(self, begin_date, end_date, universe=None):
        kd_logger.info("start create yields data")
        yields = self._yields_class()
        if self._yield_name == 'returns':
            closing_date = advanceDateByCalendar(
                'china.sse', end_date,
                "{}b".format(self._offset + self._horizon + 1),
                BizDayConventions.Following)

            yields_data = yields.fetch_returns(universe=universe,
                                               start_date=begin_date,
                                               end_date=closing_date,
                                               horizon=self._horizon,
                                               offset=self._offset,
                                               benchmark=None)
        else:
            yields_data = yields.fetch_yileds(universe=universe,
                                              start_date=begin_date,
                                              end_date=end_date,
                                              name=self._yield_name)
        return yields_data

    def factors_data(self, begin_date, end_date, factor_name, universe=None):
        factors_data = self._factors_class().fetch(
            universe=universe,
            start_date=begin_date,
            end_date=end_date,
            columns=self._transformer.dependency)
        return factors_data

    def industry_median(self, factors_data):

        def _industry_median(standard_data, factor_name):
            median_values = standard_data[[
                'trade_date', 'industry_code', 'code', factor_name
            ]].groupby(['trade_date', 'industry_code']).median()[factor_name]

            median_values.name = factor_name + '_median'
            factor_data = standard_data[[
                'trade_date', 'industry_code', 'code', factor_name
            ]].merge(median_values.reset_index(),
                     on=['trade_date', 'industry_code'],
                     how='left')
            factor_data['standard_' +
                        factor_name] = factor_data[factor_name].mask(
                            pd.isnull(factor_data[factor_name]),
                            factor_data[factor_name + '_median'])
            return factor_data.drop(
                [factor_name + '_median'],
                axis=1).set_index(['trade_date', 'code', 'industry_code'])

        res = []
        standarad_cols = [
            'standard_' + col for col in self._transformer.dependency
        ]
        kd_logger.info("start industry median data ...")

        for col in self._transformer.dependency:
            rts = _industry_median(factors_data, col)
            res.append(rts)

        factors_data = pd.concat(res, axis=1)

        factors_data = factors_data.fillna(0)
        factors_data = factors_data.reset_index().set_index(
            ['trade_date', 'code'])
        factors_data = factors_data.drop(
            self._transformer.dependency, axis=1).rename(columns=dict(
                zip(standarad_cols, self._transformer.dependency)))
        return factors_data.reset_index()

    def create_configure(self, configure):

        def init_config(name, value, configure):
            configure[name] = configure[name] if name in configure else value

        init_config('population_size', 50, configure)
        init_config('tournament_size', 10, configure)
        init_config('generations', 10, configure)
        init_config('n_jobs', 4, configure)
        init_config('stopping_criteria', 0.1, configure)
        init_config('standard_score', 5, configure)
        init_config('crossover', 0.2, configure)
        init_config('point_mutation', 0.45, configure)
        init_config('subtree_mutation', 0.15, configure)
        init_config('hoist_mutation', 0.2, configure)
        init_config('point_replace', 0.05, configure)
        init_config('rootid', str(int(time.time())), configure)
        init_config('convergence', 0.002, configure)
        init_config('mode', 'score', configure)
        init_config('n_splits', 5, configure)
        init_config('slicing', 0.2, configure)
        init_config('greater_is_better', GREATER_MAPPING[configure['mode']],
                    configure)

        return configure

    def corrcoef(self, factors_data, yields_data, factors_columns):
        kd_logger.info("start corrcoef")
        total_data = factors_data.merge(yields_data, on=['trade_date', 'code'])
        total_data = total_data.sort_values(by=['trade_date', 'code'])
        engine = DimensionCorrcoef(features=factors_columns,
                                   thresh=self._thresh,
                                   method=FCorrType.F_TS_CORR)
        dimension_data = engine.run(
            factors_data=factors_data,
            similar_type=ECoreCorrType.E_CORE_TYPE_SPERM)
        dimension_data = dimension_data.replace([np.inf, -np.inf], np.nan)
        return dimension_data.merge(yields_data, on=['trade_date', 'code'])

    def fetch_industry(self, begin_date, end_date, universe=None):
        kd_logger.info("start fetch industry data")
        industry = self._industry_class()
        industry_data = industry.fetch(universe=universe,
                                       start_date=begin_date,
                                       end_date=end_date,
                                       category=self._industry_name,
                                       level=self._industry_level)
        return industry_data

    def create_program(self, best_programs):
        result = [p.output() for p in best_programs]
        result = pd.DataFrame(result)
        result['desc'] = result['desc'].apply(lambda x: json.dumps(x))
        result.sort_values(by='fitness', ascending=False, inplace=True)
        return result.drop(['update_time'], axis=1)

    def create_metrics(self, best_programs):

        def _transform_metrics(retain_data, name):
            res = []
            for c in ['short', 'long', 'both']:
                metrics_data = retain_data.__getattribute__(
                    '{0}_evaluate'.format(c))._asdict()
                metrics_data = pd.DataFrame([metrics_data]).drop(['category'],
                                                                 axis=1)
                new_name = zip(
                    metrics_data.columns,
                    ["{0}_{1}".format(c, col) for col in metrics_data.columns])
                metrics_data.rename(columns=dict(new_name), inplace=True)
                res.append(metrics_data)
            result = pd.concat(res, axis=1)
            result['direction'] = retain_data.direction
            result['name'] = name
            return result.set_index('name')

        def _metrics(program, data, name):
            new_model = load_model(program._desc)
            X = data[new_model.features]
            Y = data['nxt1_ret']
            y_predict = new_model.predict(X)
            y_predict = pd.Series(y_predict, index=X.index)
            yield_score = Y.unstack()
            factors_socre = y_predict.unstack()
            ms = Metrics(returns=yield_score,
                         factors=factors_socre,
                         hold=self._horizon + 1,
                         show_log=False)
            retain_data = ms.fit_metrics()
            retain_data = _transform_metrics(retain_data, program._name)
            columns = [
                col for col in retain_data.columns if col not in ['direction']
            ]
            new_name = zip(columns,
                           ['{0}_{1}'.format(name, col) for col in columns])
            return retain_data.rename(columns=dict(new_name))

        train_results = [
            _metrics(best_program, self._train_data, 'train')
            for best_program in best_programs
        ]
        train_metrics = pd.concat(train_results, axis=0).reset_index()

        test_results = [
            _metrics(best_program, self._test_data, 'test')
            for best_program in best_programs
        ]
        test_metrics = pd.concat(test_results, axis=0).reset_index()
        return train_metrics.merge(test_metrics,
                                   on=['name'],
                                   suffixes=('', '_w')).drop(['direction_w'],
                                                             axis=1)

    def save_model(self, gen, rootid, best_programs,
                   custom_params):  ## 每一代优秀模型回调
        if self._callback_save is not None:
            self._callback_save(gen=gen,
                                rootid=rootid,
                                best_programs=best_programs,
                                custom_params=custom_params)
        else:
            result = self.create_program(best_programs=best_programs)
            score = self.create_metrics(best_programs=best_programs)
            result = result.merge(score, on=['name'])
            if self._best_programs is None:
                self._best_programs = result
            else:
                self._best_programs = pd.concat([self._best_programs, result],
                                                axis=0)
                self._best_programs = self._best_programs.drop_duplicates(
                    subset=['name'])

    def best_programs(self):
        return self._best_programs.reset_index(
            drop=True).sort_values(by=['fitness']) if isinstance(
                self._best_programs, pd.DataFrame) is not None else None

    def calculate_result(self, dimension_data, configure, custom_params=None):

        def change_params(model, custom_sets):
            if model in custom_sets:
                return custom_sets[model]
            else:
                return Paramizer().__getattribute__(model)()

        self.create_configure(configure)
        kwargs = custom_params if isinstance(custom_params, dict) else {}
        kwargs['mode'] = configure['mode']
        kwargs['horizon'] = self._horizon
        kwargs['offset'] = self._offset
        kwargs['universe'] = self._universe

        configure['custom_params'] = kwargs
        params_sets = [
            change_params(model, self._params_sets)
            for model in self._model_sets
        ]
        params_sets = dict(zip(self._model_sets, params_sets))

        #params_sets = dict(
        #    zip(self._model_sets,
        #        [Paramizer().__getattribute__(m)() for m in self._model_sets]))

        columns = [
            col for col in dimension_data.columns.tolist()
            if col not in ['trade_date', 'code', 'nxt1_ret', 'nxt1_ret_w']
        ]

        ### 数据切分
        dimension_data = dimension_data.sort_values(
            by=['trade_date', 'code']).reset_index(drop=True)

        ### 加权计算
        if self._is_weighted:
            dimension_data.sort_values(by=['trade_date', 'nxt1_ret_w'],
                                       ascending=True,
                                       inplace=True)
            weighted = dimension_data.set_index(['code']).groupby(
                ['trade_date']).apply(lambda x: x['nxt1_ret_w'].rank() / x[
                    'nxt1_ret_w'].rank().sum())
            weighted.name = 'sample_weight'
            dimension_data = dimension_data.merge(weighted,
                                                  on=['trade_date', 'code'])
        pos = int(len(dimension_data) * (1 - configure['slicing']))
        train_data = dimension_data.iloc[:pos]
        test_data = dimension_data.iloc[pos:]

        cols = columns + [
            'sample_weight'
        ] if self._is_weighted else columns  # 主要携带的weight 但不作为特征
        X = train_data[['trade_date', 'code'] + cols].set_index(
            ['trade_date', 'code']).fillna(0)
        Y = train_data[['trade_date', 'code',
                        'nxt1_ret']].set_index(['trade_date',
                                                'code']).fillna(0)

        self._train_data = train_data.drop(
            ['nxt1_ret'], axis=1).rename(columns={
                'nxt1_ret_w': 'nxt1_ret'
            }).set_index(['trade_date', 'code']).fillna(0)

        self._test_data = test_data.drop(
            ['nxt1_ret'], axis=1).rename(columns={
                'nxt1_ret_w': 'nxt1_ret'
            }).set_index(['trade_date', 'code']).fillna(0)

        gentic = self._gentic_class(
            model_sets=self._model_sets,
            params_sets=params_sets,
            rootid=configure['rootid'],
            generations=configure['generations'],
            n_jobs=configure['n_jobs'],
            stopping_criteria=configure['stopping_criteria'],
            convergence=configure['convergence'],
            population_size=configure['population_size'],
            tournament_size=configure['tournament_size'],
            p_point_mutation=configure['point_mutation'],
            p_crossover=configure['crossover'],
            standard_score=configure['standard_score'],
            greater_is_better=configure['greater_is_better'],
            custom_params=configure['custom_params'],
            save_model=self.save_model)

        gentic.train(columns,
                     X=X,
                     Y=Y,
                     mode=configure['mode'],
                     n_splits=configure['n_splits'])

    def factors_normal(self, factors_data, factors_columns):
        kd_logger.info("start factors normal")
        new_factors = factor_processing(
            factors_data[factors_columns].values,
            pre_process=[winsorize_normal, standardize],
            groups=factors_data['trade_date'].values)

        factors_data = pd.DataFrame(new_factors,
                                    columns=factors_columns,
                                    index=factors_data.set_index(
                                        ['trade_date', 'code']).index)
        factors_data = factors_data.reset_index()
        factors_data = factors_data.sort_values(by=['trade_date', 'code'])
        return factors_data

    def dummy_data(self, begin_date, end_date):
        kd_logger.info("start fetch dummy data")
        if self._dummy_name is None:
            return None
        closing_date = advanceDateByCalendar('china.sse', end_date,
                                             "{}b".format(self._offset + 1),
                                             BizDayConventions.Following)
        dummy_data = self._dummy_class().fetch(
            name=self._dummy_name,
            start_date=begin_date,
            end_date=closing_date,
            universe=self._universe_class(u_name=self._universe))
        dummy_data['pos'] = 1
        dummy_data.set_index(['trade_date', 'code'], inplace=True)
        dummy_data = dummy_data.unstack().shift(-(self._offset + 1)).stack()
        dummy_data = dummy_data.reset_index().drop(['pos'], axis=1)
        return dummy_data

    def prepare_data(self, begin_date=None, end_date=None):
        yields_data = self.fetch_yields(
            begin_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))

        factors_data = self.factors_data(
            begin_date=begin_date,
            end_date=end_date,
            factor_name=self._transformer.dependency,
            universe=self._universe_class(u_name=self._universe))

        industry_data = self.fetch_industry(
            begin_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))

        factors_data = self.industry_fillna(industry_data=industry_data,
                                            factors_data=factors_data)
        factors_data = factors_data.sort_values(by=['trade_date', 'code'])
        factors_data = self._transformer.transform(
            'code', factors_data.set_index('trade_date')).reset_index()

        #returns_data = yields_data.copy()
        ## 提取非累积收益 偏移
        returns_data = self.fetch_returns(
            begin_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))

        if self._factors_normal:
            total_data = factors_data.merge(yields_data,
                                            on=['trade_date', 'code'])
            total_data = self.factors_normal(
                total_data, self._transformer.names + ['nxt1_ret'])
            factors_data = total_data[['trade_date', 'code'] +
                                      self._transformer.names]

            yields_data = total_data[['trade_date', 'code', 'nxt1_ret']]

        dimension_data = self.corrcoef(factors_data=factors_data,
                                       yields_data=yields_data,
                                       factors_columns=self._transformer.names)
        dummy_data = self.dummy_data(begin_date=begin_date, end_date=end_date)

        dimension_data = dimension_data.merge(
            dummy_data, on=['trade_date', 'code'
                            ]) if dummy_data is not None else dimension_data

        return dimension_data.merge(returns_data,
                                    on=['trade_date', 'code'],
                                    suffixes=('', '_w'))

    def run(self, begin_date, end_date, configure, custom_params=None):
        kd_logger.info("start service")
        dimension_data = self.prepare_data(begin_date=begin_date,
                                           end_date=end_date)

        self.calculate_result(dimension_data=dimension_data,
                              configure=configure,
                              custom_params=custom_params)
