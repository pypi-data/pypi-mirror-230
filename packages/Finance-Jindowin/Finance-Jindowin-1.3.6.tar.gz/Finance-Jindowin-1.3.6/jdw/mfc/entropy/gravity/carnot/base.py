# -*- coding: utf-8 -*-
import hashlib, copy, json, pdb
import numpy as np
import pandas as pd
from ultron.tradingday import *
from ultron.optimize.model.modelbase import load_module
from ultron.factor.data.transformer import Transformer
from ultron.factor.data.processing import factor_processing
from ultron.factor.data.winsorize import winsorize_normal
from ultron.factor.data.standardize import standardize
from jdw.kdutils.logger import kd_logger
from jdw.kdutils.create_id import create_id
"""
每周一(freq)拉取过去400(batch)天的数据进行训练，
周二~周五用过去400天（batch)天，预测未来5(horizon）天的收益率. 
周四-下周二（offset=1）交易
"""


class Base(object):

    def __init__(self,
                 factor_class,
                 universe_class,
                 yields_class,
                 industry_class,
                 model_name,
                 model_params,
                 features,
                 batch=1,
                 freq=1,
                 horizon=1,
                 offset=1,
                 factors_normal=True,
                 industry_name='sw',
                 industry_level=1,
                 yield_name='returns',
                 factor_name=None,
                 universe=None):
        self._factor_class = factor_class
        self._yields_class = yields_class
        self._industry_class = industry_class
        self._universe_class = universe_class
        self._industry_name = industry_name
        self._industry_level = industry_level
        self._model_name = model_name
        self._model_params = model_params
        self._batch = batch
        self._freq = freq
        self._horizon = horizon
        self._offset = offset
        self._universe = universe
        self._factors_normal = factors_normal
        self._yield_name = yield_name
        self._factor_name = self._factor_name(
        ) if factor_name is None else factor_name
        self._alpha_model = load_module(model_name)(features=features,
                                                    **model_params)

    def _factor_name(self):
        s = hashlib.md5(
            json.dumps(
                self._model_params).encode(encoding="utf-8")).hexdigest()
        return "{0}_{1}".format(self._model_name,
                                create_id(original=s, digit=10))

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

    def prepare_data(self, begin_date=None, end_date=None, is_train=True):
        if is_train:
            yields_data = self.fetch_yields(
                begin_date=begin_date,
                end_date=end_date,
                universe=self._universe_class(u_name=self._universe))

        factors_data = self.factors_data(
            begin_date=begin_date,
            end_date=end_date,
            factor_name=self._alpha_model.formulas.dependency,
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
        factors_data = self._alpha_model.formulas.transform(
            'code', factors_data.set_index('trade_date')).reset_index()
        if self._factors_normal:
            if is_train:
                total_data = factors_data.merge(yields_data,
                                                on=['trade_date', 'code'])
                total_data = self.factors_normal(
                    total_data, self._alpha_model.features + ['nxt1_ret'])
            else:
                total_data = factors_data
                total_data = self.factors_normal(total_data,
                                                 self._alpha_model.features)

        return total_data

    def create_models(self, total_data, begin_date, end_date):
        models = {}
        date_label = pd.DatetimeIndex(total_data.trade_date).to_pydatetime()
        #dates = np.unique(date_label)
        dates = makeSchedule(begin_date,
                             end_date,
                             '{}b'.format(self._freq),
                             calendar='china.sse',
                             dateRule=BizDayConventions.Following,
                             dateGenerationRule=DateGeneration.Backward)
        for d in dates:
            start_date = advanceDateByCalendar('china.sse', d,
                                               "-{}b".format(self._freq),
                                               BizDayConventions.Following)
            ref_dates = makeSchedule(
                start_date,
                d,
                '1b',
                calendar='china.sse',
                dateRule=BizDayConventions.Following,
                dateGenerationRule=DateGeneration.Backward)

            if ref_dates[-1] == d:
                end = ref_dates[-2]
                start = ref_dates[
                    -self._batch -
                    1] if self._batch <= len(ref_dates) - 1 else ref_dates[0]
            else:
                end = ref_dates[-1]
                start = ref_dates[-self._batch] if self._batch <= len(
                    ref_dates) else ref_dates[0]
            index = (date_label >= start) & (date_label <= end)
            base_model = copy.deepcopy(self._alpha_model)
            train_data = total_data.set_index(
                'trade_date').loc[index].reset_index().fillna(0)
            train_data = train_data.sort_values(by=['trade_date', 'code'])
            ne_x = train_data[self._alpha_model.formulas.names].values
            ne_y = train_data[['nxt1_ret']].values

            X = pd.DataFrame(
                ne_x, columns=self._alpha_model.formulas.names).fillna(0)
            Y = ne_y
            kd_logger.info("start train {} model".format(d))
            base_model.fit(X, Y)
            models[d] = base_model
        return models

    def predict(self, models, total_data, begin_date, end_date):
        res = []
        date_label = pd.DatetimeIndex(total_data.trade_date).to_pydatetime()
        dates = makeSchedule(begin_date,
                             end_date,
                             '1b',
                             calendar='china.sse',
                             dateRule=BizDayConventions.Following,
                             dateGenerationRule=DateGeneration.Backward)
        keys = models.keys()
        for d in dates:
            sub_list = list(filter(lambda x: x <= d, keys))
            if len(sub_list) == 0:
                continue
            #if d not in models.keys():
            #    continue
            alpha_model = models[sub_list[0]]
            start_date = advanceDateByCalendar(
                'china.sse', d, "-{}b".format(self._batch + self._freq),
                BizDayConventions.Following)
            ref_dates = makeSchedule(
                start_date,
                d,
                '1b',
                calendar='china.sse',
                dateRule=BizDayConventions.Following,
                dateGenerationRule=DateGeneration.Backward)

            if ref_dates[-1] == d:
                end = ref_dates[-2]
                start = ref_dates[
                    -self._batch -
                    1] if self._batch <= len(ref_dates) - 1 else ref_dates[0]
            else:
                end = ref_dates[-1]
                start = ref_dates[-self._batch] if self._batch <= len(
                    ref_dates) else ref_dates[0]

            index = (date_label >= start) & (date_label <= end)
            base_model = copy.deepcopy(alpha_model)
            train_data = total_data.set_index(
                'trade_date').loc[index].reset_index()
            train_data = train_data.sort_values(by=['trade_date', 'code'])
            ne_x = train_data[self._alpha_model.formulas.names].values

            #codes = train_data.code
            kd_logger.info("start predict {} model".format(d))
            index = train_data.set_index(['trade_date', 'code']).index
            X = pd.DataFrame(
                ne_x, columns=self._alpha_model.formulas.names).fillna(0)
            y = pd.DataFrame(base_model.predict(X).flatten(),
                             index=index,
                             columns=[self._factor_name])
            # 获取最新一期
            y = y.reset_index().sort_values(
                by=['trade_date', 'code']).drop_duplicates(subset=['code'],
                                                           keep='last')
            y['trade_date'] = d
            res.append(y.set_index(['trade_date', 'code']))
        return pd.concat(res, axis=0)

    def generate_models(self, begin_date, end_date):
        start_date = advanceDateByCalendar(
            'china.sse', begin_date,
            "-{}b".format(self._batch + self._freq + 1),
            BizDayConventions.Following)
        total_data = self.prepare_data(begin_date=start_date,
                                       end_date=end_date,
                                       is_train=True)
        models = self.create_models(total_data=total_data,
                                    begin_date=begin_date,
                                    end_date=end_date)
        return models

    def create_factors(self, models, begin_date, end_date):
        start_date = advanceDateByCalendar(
            'china.sse', begin_date,
            "-{}b".format(self._batch + self._freq + 1),
            BizDayConventions.Following)
        total_data = self.prepare_data(begin_date=start_date,
                                       end_date=end_date,
                                       is_train=False)
        factors_data = self.predict(models=models,
                                    total_data=total_data,
                                    begin_date=begin_date,
                                    end_date=end_date)
        return factors_data

    def run(self, begin_date, end_date):
        start_date = advanceDateByCalendar(
            'china.sse', begin_date,
            "-{}b".format(self._batch + self._freq + 1),
            BizDayConventions.Following)
        total_data = self.prepare_data(begin_date=start_date,
                                       end_date=end_date)
        models = self.create_models(total_data=total_data,
                                    begin_date=begin_date,
                                    end_date=end_date)

        factors_data = self.predict(models=models,
                                    total_data=total_data,
                                    begin_date=begin_date,
                                    end_date=end_date)
        return factors_data