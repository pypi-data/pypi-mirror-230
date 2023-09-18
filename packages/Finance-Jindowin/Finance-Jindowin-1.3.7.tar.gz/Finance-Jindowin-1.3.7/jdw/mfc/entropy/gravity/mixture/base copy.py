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


class ModelTuple(object):

    def __init__(self, features, model_name, params, batch, freq, horizon,
                 offset):
        alpha_model = load_module(model_name)(features=features, **params)
        s = hashlib.md5(
            json.dumps({
                'name': model_name,
                'feature': alpha_model.formulas.names,
                'params': params
            }).encode(encoding="utf-8")).hexdigest()
        self.id = create_id(original=s, digit=10)
        self.alpha_model = alpha_model
        self.features = features
        self.model_name = model_name
        self.params = params
        self.batch = batch
        self.freq = freq
        self.horizon = horizon
        self.offset = offset
        self.train_models = []


class Base(object):

    def __init__(self,
                 factor_class,
                 universe_class,
                 yields_class,
                 industry_class,
                 model_name,
                 model_params,
                 model_sets,
                 batch=1,
                 freq=1,
                 horizon=1,
                 offset=1,
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
        self._model_name = model_name
        self._model_params = model_params
        self._batch = batch
        self._freq = freq
        self._horizon = horizon
        self._offset = offset
        self._universe = universe
        self._factors_normal = factors_normal
        self._yield_name = yield_name
        self._model_sets = self.initialize_model(model_sets)

    def initialize_model(self, model_sets):
        kd_logger.info("initialize models")
        return [
            ModelTuple(features=x['features'],
                       model_name=x['model_name'],
                       params=x['params'],
                       batch=x['batch'],
                       freq=x['freq'],
                       horizon=x['horizon'],
                       offset=x['offset']) for x in model_sets
        ]

    def max_params(self, name):
        return max([x.__getattribute__(name) for x in self._model_sets])

    def initialize_params(self):
        kd_logger.info("initialize params")
        max_horizon = self.max_params('horizon') + self._horizon
        max_offset = self.max_params('offset') + self._offset
        max_batch = self.max_params('batch') + self._batch
        max_freq = self.max_params('freq') + self._freq
        formulas = [x.alpha_model.formulas for x in self._model_sets]
        return max_offset, max_horizon, max_batch, max_freq, formulas

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

        dependency = list(
            itertools.chain.from_iterable([x.dependency for x in formulas]))

        factors_columns = list(
            itertools.chain.from_iterable([x.names for x in formulas]))

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
        res = []
        for exp in formulas:
            formula_data = exp.transform(
                'code', factors_data.set_index('trade_date')).reset_index()
            res.append(formula_data.set_index(['trade_date', 'code']))
        factors_data = pd.concat(res, axis=1).reset_index()
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

    def create_model(self, total_data, mid, alpha_model, batch, freq,
                     begin_date, end_date):
        models = {}
        date_label = pd.DatetimeIndex(total_data.trade_date).to_pydatetime()
        #dates = np.unique(date_label)
        dates = makeSchedule(begin_date,
                             end_date,
                             '{}b'.format(freq),
                             calendar='china.sse',
                             dateRule=BizDayConventions.Following,
                             dateGenerationRule=DateGeneration.Backward)
        for d in dates:
            start_date = advanceDateByCalendar('china.sse', d,
                                               "-{}b".format(freq),
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
                    -batch -
                    1] if batch <= len(ref_dates) - 1 else ref_dates[0]
            else:
                end = ref_dates[-1]
                start = ref_dates[-batch] if batch <= len(
                    ref_dates) else ref_dates[0]
            index = (date_label >= start) & (date_label <= end)
            base_model = copy.deepcopy(alpha_model)
            train_data = total_data.set_index(
                'trade_date').loc[index].reset_index().fillna(0)
            if train_data.empty:
                continue
            train_data = train_data.sort_values(by=['trade_date', 'code'])
            ne_x = train_data[alpha_model.formulas.names].values
            ne_y = train_data[['nxt1_ret']].values

            X = pd.DataFrame(ne_x,
                             columns=alpha_model.formulas.names).fillna(0)
            Y = ne_y
            kd_logger.info("start train {} model".format(d))
            base_model.fit(X, Y)
            models[d] = base_model
        return {'id': mid, 'models': models}

    def predict(self, mid, models, total_data, batch, freq, begin_date,
                end_date):
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
            start_date = advanceDateByCalendar('china.sse', d,
                                               "-{}b".format(batch + freq),
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
                    -batch -
                    1] if batch <= len(ref_dates) - 1 else ref_dates[0]
            else:
                end = ref_dates[-1]
                start = ref_dates[-batch] if batch <= len(
                    ref_dates) else ref_dates[0]

            index = (date_label >= start) & (date_label <= end)
            base_model = copy.deepcopy(alpha_model)
            train_data = total_data.set_index(
                'trade_date').loc[index].reset_index()
            train_data = train_data.sort_values(by=['trade_date', 'code'])
            ne_x = train_data[alpha_model.formulas.names].values

            codes = train_data.code
            X = pd.DataFrame(ne_x,
                             columns=alpha_model.formulas.names).fillna(0)
            y = pd.DataFrame(base_model.predict(X).flatten(),
                             index=codes,
                             columns=[mid])
            y['trade_date'] = d
            res.append(y.reset_index().set_index(['trade_date', 'code']))
        return pd.concat(res, axis=0)

    def generate_models(self, begin_date, end_date):
        max_offset, max_horizon, max_batch, max_freq, formulas = self.initialize_params(
        )
        start_date = advanceDateByCalendar(
            'china.sse', begin_date,
            "-{}b".format(max_horizon + max_offset + 1),
            BizDayConventions.Following)
        total_data = self.prepare_data(begin_date=start_date,
                                       end_date=end_date,
                                       formulas=formulas)
        for model_tuple in self._model_sets:
            models = self.create_model(
                mid=model_tuple.id,
                total_data=total_data[
                    ['trade_date', 'code', 'nxt1_ret'] +
                    model_tuple.alpha_model.formulas.names].copy(),
                alpha_model=model_tuple.alpha_model,
                freq=model_tuple.freq,
                batch=model_tuple.batch,
                begin_date=begin_date,
                end_date=end_date)
            model_tuple.train_models = models['models']
        print("generate models done")

        ### 生成因子对齐
        res = []
        for model_tuple in self._model_sets:
            new_factors = self.predict(
                mid=model_tuple.id,
                total_data=total_data[
                    ['trade_date', 'code'] +
                    model_tuple.alpha_model.formulas.names].copy(),
                models=model_tuple.train_models,
                freq=model_tuple.freq,
                batch=model_tuple.batch,
                begin_date=begin_date,
                end_date=end_date)
            new_factors.reset_index(inplace=True)
            new_factors.drop_duplicates(subset=['trade_date', 'code'],
                                        inplace=True)
            res.append(new_factors.set_index(['trade_date', 'code']))

        features_data = pd.concat(res, axis=1)
        ###初始化后置模型
        features = features_data.columns.tolist()
        features_data = features_data.reset_index().merge(
            total_data[['trade_date', 'code', 'nxt1_ret']])
        alapha_model = load_module(self._model_name)(features=features,
                                                     **self._model_params)
        model = self.create_model(total_data=features_data,
                                  mid='alpha',
                                  alpha_model=alapha_model,
                                  batch=self._batch,
                                  freq=self._freq,
                                  begin_date=begin_date,
                                  end_date=end_date)
