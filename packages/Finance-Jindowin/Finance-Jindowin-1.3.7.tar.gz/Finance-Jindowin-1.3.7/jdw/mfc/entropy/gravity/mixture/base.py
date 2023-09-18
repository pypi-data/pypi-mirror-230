# -*- coding: utf-8 -*-
import pdb, itertools, copy, hashlib, json
import pandas as pd
from ultron.tradingday import *
from collections import namedtuple
from ultron.optimize.model.modelbase import load_module
from ultron.factor.data.processing import factor_processing
from ultron.factor.data.winsorize import winsorize_normal
from ultron.factor.data.standardize import standardize
from jdw.mfc.entropy.gravity.mixture.models import IntegratedModel
from jdw.kdutils.logger import kd_logger
from jdw.kdutils.create_id import create_id

### modelsets: [
# alpha_model, features, params, batch, freq, horizon, offset]


class Base(object):

    def __init__(self,
                 factor_class,
                 universe_class,
                 yields_class,
                 industry_class,
                 model_name=None,
                 model_params=None,
                 model_sets=[],
                 batch=1,
                 freq=1,
                 horizon=1,
                 offset=1,
                 stacking=False,
                 factors_normal=True,
                 industry_name='sw',
                 industry_level=1,
                 yield_name='returns',
                 universe=None):
        self._factor_class = factor_class
        self._yields_class = yields_class
        self._industry_class = industry_class
        self._universe_class = universe_class
        self._industry_name = industry_name
        self._industry_level = industry_level
        self._universe = universe
        self._factors_normal = factors_normal
        self._yield_name = yield_name
        self._integrated_model = None
        if model_name is not None:
            self._integrated_model = IntegratedModel(model_name=model_name,
                                                     model_params=model_params,
                                                     model_sets=model_sets,
                                                     batch=batch,
                                                     freq=freq,
                                                     horizon=horizon,
                                                     offset=offset,
                                                     stacking=stacking)

    def initialize_params(self):
        kd_logger.info("initialize params")
        max_horizon = self._integrated_model.max_params(
            'horizon') + self._integrated_model._horizon
        max_offset = self._integrated_model.max_params(
            'offset') + self._integrated_model._offset
        max_batch = self._integrated_model.max_params(
            'batch') + self._integrated_model._batch
        max_freq = self._integrated_model.max_params(
            'freq') + self._integrated_model._freq
        return max_offset, max_horizon, max_batch, max_freq

    def fetch_yields(self, begin_date, end_date, universe=None):
        kd_logger.info("start create yields data")
        yields = self._yields_class()
        if self._yield_name == 'returns':
            closing_date = advanceDateByCalendar(
                'china.sse', end_date,
                "{}b".format(self._integrated_model._horizon +
                             self._integrated_model._offset + 1),
                BizDayConventions.Following)

            yields_data = yields.fetch_returns(
                universe=universe,
                start_date=begin_date,
                end_date=closing_date,
                horizon=self._integrated_model._horizon,
                offset=self._integrated_model._offset,
                benchmark=None)
        else:
            yields_data = yields.fetch_yileds(universe=universe,
                                              start_date=begin_date,
                                              end_date=end_date,
                                              name=self._yield_name)
        return yields_data

    def factors_data(self, begin_date, end_date, factor_name, universe=None):
        factors_data = self._factor_class().fetch(universe=universe,
                                                  start_date=begin_date,
                                                  end_date=end_date,
                                                  columns=factor_name)
        return factors_data

    def fetch_industry(self, begin_date, end_date, universe=None):
        kd_logger.info("start fetch industry data")
        industry = self._industry_class()
        industry_data = industry.fetch(universe=universe,
                                       start_date=begin_date,
                                       end_date=end_date,
                                       category=self._industry_name,
                                       level=self._industry_level)
        return industry_data

    def industry_fillna(self, industry_data, factors_data):
        return factors_data.fillna(0)

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
        standarad_cols = ['standard_' + col for col in self._features]
        kd_logger.info("start industry median data ...")

        for col in self._features:
            rts = _industry_median(factors_data, col)
            res.append(rts)

        factors_data = pd.concat(res, axis=1)

        factors_data = factors_data.fillna(0)
        factors_data = factors_data.reset_index().set_index(
            ['trade_date', 'code'])
        factors_data = factors_data.drop(
            self._features,
            axis=1).rename(columns=dict(zip(standarad_cols, self._features)))
        return factors_data.reset_index()

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

    def prepare_data(self, begin_date, end_date, formulas, is_train=True):
        if is_train:
            yields_data = self.fetch_yields(
                begin_date=begin_date,
                end_date=end_date,
                universe=self._universe_class(u_name=self._universe))

        dependency = self._integrated_model.dependency()

        factors_columns = self._integrated_model.features()

        factors_data = self.factors_data(
            begin_date=begin_date,
            end_date=end_date,
            factor_name=dependency,
            universe=self._universe_class(u_name=self._universe))

        industry_data = self.fetch_industry(
            begin_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))

        factors_data = self.industry_fillna(
            industry_data=industry_data, factors_data=factors_data).fillna(0)
        factors_data = factors_data.sort_values(by=['trade_date', 'code'])
        ### 因子换算
        factors_data = factors_data.sort_values(by=['trade_date', 'code'])
        '''
        res = []
        for exp in formulas:
            formula_data = exp.transform(
                'code', factors_data.set_index('trade_date')).reset_index()
            res.append(formula_data.set_index(['trade_date', 'code']))
        factors_data = pd.concat(res, axis=1).reset_index()
        '''
        factors_data = formulas.transform(
            'code', factors_data.set_index('trade_date')).reset_index()
        ### 行业中位数填充
        if self._factors_normal:
            if is_train:
                total_data = factors_data.merge(yields_data,
                                                on=['trade_date', 'code'])
                total_data = self.factors_normal(
                    total_data, factors_columns + ['nxt1_ret'])
            else:
                total_data = factors_data
                total_data = self.factors_normal(total_data, factors_columns)
        return total_data

    def dump_models(self):
        return self._integrated_model.dump_models()

    def load_models(self, desc):
        self._integrated_model = IntegratedModel.mixture_clf_load(desc)

    def generate_models(self, begin_date, end_date):
        max_offset, max_horizon, max_batch, max_freq = self.initialize_params()
        start_date = advanceDateByCalendar(
            'china.sse', begin_date,
            "-{}b".format(max_horizon + max_offset + 1),
            BizDayConventions.Following)
        formulas = self._integrated_model.formulas()
        total_data = self.prepare_data(begin_date=start_date,
                                       end_date=end_date,
                                       formulas=formulas)
        self._integrated_model.generate_models(total_data=total_data,
                                               begin_date=begin_date,
                                               end_date=end_date)

    def generate_predict(self, begin_date, end_date):
        max_offset, max_horizon, max_batch, max_freq = self.initialize_params()
        start_date = advanceDateByCalendar(
            'china.sse', begin_date, "-{}b".format(max_batch + max_offset + 1),
            BizDayConventions.Following)
        formulas = self._integrated_model.formulas()
        total_data = self.prepare_data(begin_date=start_date,
                                       end_date=end_date,
                                       formulas=formulas)

        return self._integrated_model.generate_predict(total_data=total_data,
                                                       begin_date=begin_date,
                                                       end_date=end_date)

    def run(self, begin_date, end_date):
        max_offset, max_horizon, max_batch, max_freq = self.initialize_params()
        start_date = advanceDateByCalendar(
            'china.sse', begin_date,
            "-{}b".format(max_horizon + max_offset + 1),
            BizDayConventions.Following)
        formulas = self._integrated_model.formulas()
        total_data = self.prepare_data(begin_date=start_date,
                                       end_date=end_date,
                                       formulas=formulas)
        self._integrated_model.generate_models(total_data=total_data,
                                               begin_date=begin_date,
                                               end_date=end_date)

        return self._integrated_model.generate_predict(total_data=total_data,
                                                       begin_date=begin_date,
                                                       end_date=end_date)