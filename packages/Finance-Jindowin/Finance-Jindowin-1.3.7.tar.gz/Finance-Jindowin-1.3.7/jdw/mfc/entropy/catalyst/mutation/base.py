# -*- coding: utf-8 -*-
import pdb
import pandas as pd
from ultron.factor.genetic.geneticist.operators import custom_transformer
from ultron.factor.genetic.geneticist.genetic import Gentic
from ultron.factor.data.processing import factor_processing
from ultron.factor.data.winsorize import winsorize_normal
from ultron.factor.data.standardize import standardize
from ultron.tradingday import *
from jdw.kdutils.logger import kd_logger


class Base(object):

    def __init__(self,
                 offset,
                 horizon,
                 factor_columns,
                 universe,
                 dummy_name,
                 yields_class,
                 universe_class,
                 dummy_class,
                 industry_class,
                 factors_class,
                 industry_name,
                 industry_level,
                 factors_normal=True,
                 operators=None,
                 yield_name='returns'):
        self._offset = offset
        self._horizon = horizon
        self._factor_columns = factor_columns
        self._universe = universe
        self._yields_class = yields_class
        self._industry_class = industry_class
        self._industry_name = industry_name
        self._industry_level = industry_level
        self._factors_class = factors_class
        self._universe_class = universe_class
        self._factors_normal = factors_normal
        self._yield_name = yield_name
        self._dummy_class = dummy_class
        self._dummy_name = dummy_name
        default_operators = [
            'CSMean', 'CSRank', 'CSQuantiles', 'SIGN', 'AVG', 'EMA', 'MACD',
            'RSI', 'MA', 'MADecay', 'MMAX', 'MARGMAX', 'MMIN', 'MARGMIN',
            'MRANK', 'MQUANTILE', 'MSUM', 'MVARIANCE', 'MSTD', 'SQRT', 'DIFF',
            'EXP', 'LOG', 'ABS', 'SHIFT', 'DELTA'
        ]
        self._operators = default_operators if operators is None else operators
        self._evolution_sets = {}

    def industry_fillna(self, industry_data, factors_data):
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
        standarad_cols = ['standard_' + col for col in self._factor_columns]
        kd_logger.info("start industry median data ...")

        for col in self._factor_columns:
            rts = _industry_median(factors_data, col)
            res.append(rts)

        factors_data = pd.concat(res, axis=1)

        factors_data = factors_data.fillna(0)
        factors_data = factors_data.reset_index().set_index(
            ['trade_date', 'code'])
        factors_data = factors_data.drop(self._factor_columns, axis=1).rename(
            columns=dict(zip(standarad_cols, self._factor_columns)))
        return factors_data.reset_index()

    def factors_data(self, begin_date, end_date, factor_name, universe=None):
        factors_data = self._factors_class().fetch(universe=universe,
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

    def factors_normal(self, factors_data):
        kd_logger.info("start factors normal")
        colmuns = factors_data.columns + ['nxt1_ret']
        new_factors = factor_processing(
            factors_data[colmuns].values,
            pre_process=[winsorize_normal, standardize],
            groups=factors_data['trade_date'].values)

        factors_data = pd.DataFrame(new_factors,
                                    columns=colmuns,
                                    index=factors_data.set_index(
                                        ['trade_date', 'code']).index)
        factors_data = factors_data.reset_index()
        factors_data = factors_data.sort_values(by=['trade_date', 'code'])
        return factors_data

    def save_model(self, gen, rootid, best_programs, custom_params):
        for programs in best_programs:
            self._evolution_sets[programs._name] = programs

    def dummy_data(self, begin_date, end_date):
        kd_logger.info("start fetch dummy data")
        if self._dummy_name is None:
            return None
        dummy_data = self._dummy_class().fetch(
            name=self._dummy_name,
            start_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))
        return dummy_data

    def prepare_data(self, begin_date=None, end_date=None):
        factors_data = self.factors_data(
            begin_date=begin_date,
            end_date=end_date,
            factor_name=self._factor_columns,
            universe=self._universe_class(u_name=self._universe))

        industry_data = self.fetch_industry(
            begin_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))

        ## 中位数填充
        factors_data = self.industry_fillna(industry_data=industry_data,
                                            factors_data=factors_data)
        factors_data = factors_data.sort_values(by=['trade_date', 'code'])

        if self._winsorize_normal:
            factors_data = self.winsorize_normal(factors_data)

        yileds_data = self.fetch_yields(
            begin_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))

        total_data = factors_data.merge(yileds_data, on=['trade_date', 'code'])

        dummy_data = self.dummy_data(begin_date=begin_date, end_date=end_date)

        total_data = total_data.merge(dummy_data, on=[
            'trade_date', 'code'
        ]) if dummy_data is not None else total_data
        return total_data

    def create_gentic(self, operators_sets, population_size, init_depth,
                      generations, custom_params, n_jobs, factor_columns):
        gentic = Gentic(population_size=population_size,
                        tournament_size=20,
                        init_depth=(1, init_depth),
                        generations=generations,
                        n_jobs=n_jobs,
                        stopping_criteria=10,
                        p_crossover=0.0,
                        p_point_mutation=0.5,
                        p_subtree_mutation=0.2,
                        p_hoist_mutation=0.2,
                        p_point_replace=0.0,
                        factor_sets=factor_columns,
                        standard_score=5,
                        operators_set=operators_sets,
                        backup_cycle=1,
                        convergence=0.2,
                        fitness=None,
                        save_model=self.save_model,
                        custom_params=custom_params)
        return gentic

    def calculate_result(self,
                         total_data,
                         init_depth,
                         evaluate='long_evaluate',
                         method='fitness',
                         generations=5,
                         n_jobs=1):
        operators_sets = custom_transformer(self._operators)
        population_size = len(operators_sets) * 3
        custom_params = {
            'evaluate': evaluate,
            'method': method,
            'universe': self._universe
        }
        for name in self._factor_columns:
            gentic = self.create_gentic(operators_sets=operators_sets,
                                        population_size=population_size,
                                        init_depth=init_depth,
                                        generations=generations,
                                        custom_params=custom_params,
                                        n_jobs=n_jobs,
                                        factor_columns=[name, name])
            gentic.train(total_data=total_data[
                ['trade_date', 'code', name, 'nxt1_ret']])
        return self._evolution_sets

    def run(self,
            begin_date,
            end_date,
            init_depth,
            evaluate='long_evaluate',
            method='fitness',
            generations=5,
            n_jobs=1):
        total_data = self.prepare_data(begin_date=begin_date,
                                       end_date=end_date)
        return self.calculate_result(total_data=total_data,
                                     init_depth=init_depth,
                                     evaluate=evaluate,
                                     method=method,
                                     generations=generations,
                                     n_jobs=n_jobs)
