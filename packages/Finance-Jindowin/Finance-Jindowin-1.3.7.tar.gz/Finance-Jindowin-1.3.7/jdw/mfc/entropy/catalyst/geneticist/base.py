# -*- coding: utf-8 -*-
import time, pdb
import pandas as pd
from ultron.factor.genetic.geneticist.operators import custom_transformer
from ultron.factor.genetic.geneticist.engine import Engine
from ultron.factor.genetic.geneticist.genetic import Gentic
from ultron.factor.data.processing import factor_processing
from ultron.factor.data.winsorize import winsorize_normal
from ultron.factor.data.standardize import standardize
from ultron.factor.fitness.metrics import Metrics
from ultron.tradingday import *
from jdw.kdutils.logger import kd_logger


class Base(object):

    def __init__(self,
                 offset,
                 horizon,
                 factor_columns,
                 universe,
                 yields_class,
                 universe_class,
                 dummy_class,
                 industry_class,
                 factors_class,
                 industry_name,
                 industry_level,
                 dummy_name=None,
                 is_loop=False,
                 operators=None,
                 factors_normal=True,
                 callback_save=None,
                 yield_name='returns'):
        self._offset = offset
        self._horizon = horizon
        self._factor_columns = factor_columns
        self._universe = universe
        self._dummy_name = dummy_name
        self._yields_class = yields_class
        self._industry_class = industry_class
        self._industry_name = industry_name
        self._industry_level = industry_level
        self._factors_class = factors_class
        self._universe_class = universe_class
        self._dummy_class = dummy_class
        self._yield_name = yield_name
        self._operators = operators
        self._factors_normal = factors_normal
        self._callback_save = callback_save
        self._gentic_class = Engine if is_loop else Gentic
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

    def fetch_yields(self, begin_date, end_date, universe=None):
        kd_logger.info("start create yields data")
        yields = self._yields_class()
        if self._yield_name == 'returns':
            closing_date = advanceDateByCalendar(
                'china.sse', end_date,
                "{}b".format(self._offset + self._horizon + 1),
                BizDayConventions.Following)

            yields_data = yields.fetch_returns(
                universe=universe,
                start_date=begin_date,
                end_date=closing_date,
                horizon=0,  #评估metrics方法不适用累计收益##self._horizon,
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

    def factors_normal(self, factors_data):
        kd_logger.info("start factors normal")
        columns = self._factor_columns  # + ['nxt1_ret']
        new_factors = factor_processing(
            factors_data[columns].values,
            pre_process=[winsorize_normal, standardize],
            groups=factors_data['trade_date'].values)

        factors_data = pd.DataFrame(new_factors,
                                    columns=columns,
                                    index=factors_data.set_index(
                                        ['trade_date', 'code']).index)
        factors_data = factors_data.reset_index()
        factors_data = factors_data.sort_values(by=['trade_date', 'code'])
        return factors_data

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

        yileds_data = self.fetch_yields(
            begin_date=begin_date,
            end_date=end_date,
            universe=self._universe_class(u_name=self._universe))

        if self._factors_normal:  # 收益率 + 因子 做去极值，标准化
            factors_data = self.factors_normal(factors_data)
        total_data = factors_data.merge(yileds_data, on=['trade_date', 'code'])
        dummy_data = self.dummy_data(begin_date=begin_date, end_date=end_date)
        total_data = total_data.merge(dummy_data, on=[
            'trade_date', 'code'
        ]) if dummy_data is not None else total_data
        return total_data

    def save_model(self, gen, rootid, best_programs, custom_params):
        if self._callback_save is not None:
            self._callback_save(gen=gen,
                                rootid=rootid,
                                best_programs=best_programs,
                                custom_params=custom_params)
        else:
            for programs in best_programs:
                self._evolution_sets[programs._name] = programs

    def create_gentic(self, operators_sets, configure):
        gentic = self._gentic_class(
            population_size=configure['population_size'],
            tournament_size=configure['tournament_size'],
            init_depth=(1, configure['init_depth']),
            generations=configure['generations'],
            n_jobs=configure['n_jobs'],
            stopping_criteria=configure['stopping_criteria'],
            p_crossover=configure['crossover'],
            p_point_mutation=configure['point_mutation'],
            p_subtree_mutation=configure['subtree_mutation'],
            p_hoist_mutation=configure['hoist_mutation'],
            p_point_replace=configure['point_replace'],
            rootid=configure['rootid'],
            factor_sets=self._factor_columns,
            standard_score=configure['standard_score'],
            operators_set=operators_sets,
            backup_cycle=1,
            convergence=configure['convergence'],
            fitness=None,
            save_model=self.save_model,
            custom_params=configure['custom_params'])
        return gentic

    def create_configure(self, configure):

        def init_config(name, value, configure):
            configure[name] = configure[name] if name in configure else value

        init_config('population_size', 100, configure)  # 初始化种群数
        init_config('tournament_size', 20, configure)  # 每一代优秀种群数
        init_config('init_depth', 4, configure)  # 每个种群
        init_config('generations', 30, configure)  # 繁衍代数据
        init_config('n_jobs', 4, configure)  # 并发数
        init_config('stopping_criteria', 100, configure)  # 停止繁衍值即目标值大于预设值停止繁衍
        init_config('standard_score', 10, configure)  # 每一代保留优秀种群的预设值
        init_config('crossover', 0.4, configure)  # 交叉率
        init_config('point_mutation', 0.3, configure)  # 点变异率
        init_config('subtree_mutation', 0.1, configure)  # 树变异率
        init_config('hoist_mutation', 0.1, configure)  # 突变异率
        init_config('point_replace', 0.1, configure)  # 点交换率
        init_config('rootid', str(int(time.time())), configure)  # 节点
        init_config('convergence', 0.002, configure)  # 每一代收敛预设停止值

    def calculate_result(self, total_data, configure, custom_params=None):
        operators_sets = custom_transformer(self._operators)
        self.create_configure(configure)
        kwargs = custom_params if isinstance(custom_params, dict) else {}
        kwargs['horizon'] = self._horizon
        kwargs['offset'] = self._offset
        kwargs['universe'] = self._universe
        kwargs['hold'] = self._horizon
        kwargs['evaluate'] = configure['evaluate']
        kwargs['method'] = configure['method']
        kwargs['tournament_size'] = configure['tournament_size']
        kwargs['standard_score'] = configure['standard_score']
        kwargs['rootid'] = configure['rootid']
        configure['custom_params'] = kwargs
        gentic = self.create_gentic(operators_sets, configure)
        gentic.train(total_data=total_data)
        return self._evolution_sets if self._callback_save is None else None

    def run(self, begin_date, end_date, configure, custom_params=None):
        total_data = self.prepare_data(begin_date=begin_date,
                                       end_date=end_date)
        return self.calculate_result(total_data=total_data,
                                     configure=configure,
                                     custom_params=custom_params)
