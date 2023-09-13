# -*- coding: utf-8 -*-
import pdb
import pandas as pd
from ultron.tradingday import *
from ultron.factor.data.transformer import Transformer
from ultron.strategy.optimize import Optimize
from jdw.kdutils.logger import kd_logger
from jdw.mfc.entropy.gravity.dendall.params import create_params


class Base(object):

    def __init__(self,
                 industry_class,
                 universe_class,
                 yields_class,
                 index_yields_class,
                 factor_class,
                 horizon=0,
                 offset=0,
                 industry_name='sw',
                 industry_level=1,
                 yield_name='returns',
                 alpha_model=None,
                 factor_columns=None,
                 factors_data=None,
                 benchmark=None,
                 universe=None):
        self._index_yields_class = index_yields_class
        self._yields_class = yields_class
        self._industry_class = industry_class
        self._universe_class = universe_class
        self._factor_class = factor_class
        self._benchmark = benchmark
        self._universe = universe
        self._industry_name = industry_name
        self._industry_level = industry_level
        self._horizon = horizon
        self._offset = offset
        self._yield_name = yield_name
        ### 1.加载指定数据库数据, 1) 指定因子列(包括公式化) 2)单模型特征加载  3)集成模型加载
        ### 2.外部输入数据 factors_data和factor_columns
        self._alpha_model = alpha_model
        self._factors_data = factors_data
        self._transformer = Transformer(
            factor_columns) if alpha_model is None else alpha_model[list(
                alpha_model.keys())[0]].formulas

    def index_yields(self, begin_date, end_date):
        closing_date = advanceDateByCalendar(
            'china.sse', end_date,
            "{}b".format(self._offset + self._horizon + 1),
            BizDayConventions.Following)
        index_return = self._index_yields_class().yields(
            start_date=begin_date,
            end_date=closing_date,
            offset=self._offset,
            horizon=self._horizon,
            index_code=self._benchmark)
        index_return.rename(columns={'nxt1_ret': 'returns'}, inplace=True)
        return index_return

    def fetch_yields(self, begin_date, end_date, universe=None):
        kd_logger.info("start create yields data")
        yields = self._yields_class()
        if self._yield_name == 'returns':
            closing_date = advanceDateByCalendar(
                'china.sse', end_date,
                "{}b".format(self._horizon + self._offset + 1),
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

    def factors_data(self, begin_date, end_date, factor_name, universe=None):
        factors_data = self._factor_class().fetch(universe=universe,
                                                  start_date=begin_date,
                                                  end_date=end_date,
                                                  columns=factor_name)
        return factors_data

    def create_component(self, begin_date, end_date, universe=None):
        return None

    def create_riskmodel(self, begin_date, end_date, universe=None):
        return None

    def merge(self, industry_data, component_data):
        return None

    def fetch_data(self, begin_date, end_date):
        factor_model, _, risk_exp = self.create_riskmodel(
            begin_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))
        component_data = self.create_component(begin_date=begin_date,
                                               end_date=end_date,
                                               universe=self._universe)

        industry_data = self.fetch_industry(
            begin_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))

        yields_data = self.fetch_yields(
            begin_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))
        total_data = self.merge(industry_data=industry_data,
                                component_data=component_data)
        if risk_exp is not None:
            total_data = total_data.merge(risk_exp, on=['trade_date', 'code'])
        self._industry_data = industry_data
        return factor_model, total_data, yields_data

    def _inner_factors(self, begin_date, end_date):
        factors_data = self.factors_data(
            begin_date=begin_date,
            end_date=end_date,
            factor_name=self._transformer.dependency,
            universe=self._universe_class(u_name=self._universe))
        if self._industry_data is None:
            self._industry_data = self.fetch_industry(
                begin_date=begin_date,
                end_date=end_date,
                universe=self._universe_class(u_name=self._universe))
        factors_data = self.industry_fillna(
            industry_data=self._industry_data,
            factors_data=factors_data).fillna(0)
        factors_data = factors_data.sort_values(by=['trade_date', 'code'])
        factors_data = self._transformer.transform(
            'code', factors_data.set_index('trade_date')).reset_index()
        return factors_data

    def create_configure(self, configure):
        return create_params(**configure)

    def create_factors(self, begin_date, end_date):
        if self._factors_data is None:
            self._factors_data = self._inner_factors(begin_date, end_date)
        return self._factors_data
        '''
        yields_data = self._yields_class().fetch_returns(
            universe=self._universe_class(u_name=self._universe),
            start_date=begin_date,
            end_date=end_date,
            horizon=self._horizon,
            offset=self._offset,
            benchmark=None)
        rank = yields_data.set_index(['trade_date',
                                      'code'])['nxt1_ret'].unstack().rank(
                                          axis=1,
                                          method='dense').rank(axis=1,
                                                               method='dense')
        score = (rank - 0.5).div(rank.max(axis=1), axis='rows') - 0.5
        score = score.stack().reset_index()
        score = score.rename(columns={0: 'factor'})
        return yields_data.rename(columns={'nxt1_ret': 'factor'})
        '''

    def prepare_data(self, begin_date, end_date):
        kd_logger.info("start service")
        #factors_data = self.create_factors(begin_date, end_date)
        index_return = None
        if self._benchmark is not None:
            index_return = self.index_yields(begin_date=begin_date,
                                             end_date=end_date)
        factor_model, total_data, yields_data = self.fetch_data(
            begin_date, end_date)
        total_data = total_data.merge(yields_data,
                                      on=['trade_date', 'code'],
                                      how='left')
        return index_return, factor_model, total_data,

    def calculate_result(self,
                         total_data,
                         factor_model,
                         begin_date,
                         end_date,
                         configure,
                         index_returns=None):
        params = self.create_configure(configure)
        optimize = Optimize(alpha_model=None,
                            category=self._category,
                            features=self._transformer.names,
                            begin_date=begin_date,
                            end_date=end_date,
                            risk_model=factor_model,
                            index_returns=index_returns,
                            total_data=total_data)
        return optimize.run(
            params) if self.index_yields else optimize.rebalance_positions(
                params)

    def run(self, begin_date, end_date, configure):
        index_returns, factor_model, total_data = self.prepare_data(
            begin_date=begin_date, end_date=end_date)
        factors = self.create_factors(begin_date, end_date)
        total_data = total_data.merge(factors, on=['trade_date', 'code'])
        metrics, returns, positions = self.calculate_result(
            total_data=total_data,
            factor_model=factor_model,
            begin_date=begin_date,
            end_date=end_date,
            configure=configure,
            index_returns=index_returns)
        return metrics, returns, positions
