# -*- coding: utf-8 -*-
import copy, hashlib, json, pdb, itertools
import pandas as pd
from ultron.tradingday import *
from ultron.sentry.Analysis.SecurityValueHolders import SecurityValueHolder
from ultron.optimize.model.treemodel import StackingRegressor
from ultron.optimize.model.modelbase import load_module
from ultron.factor.utilities import encode, decode
from ultron.factor.data.transformer import Transformer
from jdw.kdutils.create_id import create_id
from jdw.kdutils.logger import kd_logger


class ModelTuple(object):

    def __init__(self, features, model_name, params, batch, freq, horizon,
                 offset):
        alpha_model = load_module(model_name)(features=features, **params)
        s = hashlib.md5(
            json.dumps({
                'name': model_name,
                'feature': alpha_model.formulas.names,
                'params': params,
                'batch': batch,
                'freq': freq,
                'horizon': horizon,
                'offset': offset
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


class IntegratedModel(object):

    @classmethod
    def mixture_clf_dump(cls, total_data, begin_date, end_date, model_name,
                         model_params, model_sets, batch, freq, horizon,
                         offset, stacking):
        integrated_model = cls(model_name=model_name,
                               model_params=model_params,
                               model_sets=model_sets,
                               batch=batch,
                               freq=freq,
                               horizon=horizon,
                               offset=offset,
                               stacking=stacking)
        integrated_model.generate_models(total_data=total_data,
                                         begin_date=begin_date,
                                         end_date=end_date)
        return integrated_model.save_models()

    @classmethod
    def mixture_clf_load(cls, desc):
        model_desc = decode(desc)
        base_model = decode(model_desc['base_model'])
        model_sets = model_desc['model_sets']
        sets = []
        for model in model_sets:
            sets.append(decode(model))
        stacking = model_desc['stacking']
        integrated_model = cls(model_name=base_model['name'],
                               model_params=base_model['params'],
                               model_sets=model_sets,
                               batch=base_model['batch'],
                               freq=base_model['freq'],
                               horizon=base_model['horizon'],
                               offset=base_model['offset'],
                               stacking=stacking,
                               alpha_models={
                                   'models': base_model['models'],
                                   'id': base_model['id']
                               })
        return integrated_model

    def __init__(self,
                 model_name,
                 model_params,
                 model_sets,
                 batch=1,
                 freq=1,
                 horizon=1,
                 offset=1,
                 stacking=False,
                 alpha_models=None):
        self._model_name = model_name
        self._model_params = model_params
        self._batch = batch
        self._freq = freq
        self._horizon = horizon
        self._offset = offset
        self._model_sets = self.initialize_models(model_sets)
        self._stacking = stacking
        self._alpha_models = alpha_models

    def initialize_models(self, model_sets):
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

    def formulas(self):
        features = [x.features for x in self._model_sets]
        features = list(itertools.chain.from_iterable(features))
        formulas = []
        names = []
        for f in features:
            if isinstance(f, str) and f not in names:
                formulas.append(f)
                names.append(f)
            elif isinstance(f, SecurityValueHolder):
                formulas.append(f)
        return Transformer(formulas)

    def features(self):
        return list(
            set(
                list(
                    itertools.chain.from_iterable([
                        x.alpha_model.formulas.names for x in self._model_sets
                    ]))))

    def dependency(self):
        return list(
            set(
                list(
                    itertools.chain.from_iterable([
                        x.alpha_model.formulas.dependency
                        for x in self._model_sets
                    ]))))

    def max_params(self, name):
        return max([x.__getattribute__(name) for x in self._model_sets])

    def create_model(self, total_data, name, mid, alpha_model, batch, freq,
                     begin_date, end_date):
        models = {}
        date_label = pd.DatetimeIndex(total_data.trade_date).to_pydatetime()
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
            kd_logger.info("start train {0} {1}:{2} model".format(
                d, name, mid))
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

            #codes = train_data.code
            index = train_data.set_index(['trade_date', 'code']).index
            X = pd.DataFrame(ne_x,
                             columns=alpha_model.formulas.names).fillna(0)
            y = pd.DataFrame(base_model.predict(X).flatten(),
                             index=index,
                             columns=[mid])
            # 获取最新一期
            y = y.reset_index().sort_values(
                by=['trade_date', 'code']).drop_duplicates(subset=['code'],
                                                           keep='last')
            y['trade_date'] = d
            res.append(y.set_index(['trade_date', 'code']))
        return pd.concat(res, axis=0)

    def train_models(self, total_data, begin_date, end_date):
        kd_logger.info("train models")
        for model_tuple in self._model_sets:
            models = self.create_model(
                mid=model_tuple.id,
                name=model_tuple.model_name,
                total_data=total_data[
                    ['trade_date', 'code', 'nxt1_ret'] +
                    model_tuple.alpha_model.formulas.names].copy(),
                alpha_model=model_tuple.alpha_model,
                freq=model_tuple.freq,
                batch=model_tuple.batch,
                begin_date=begin_date,
                end_date=end_date)
            model_tuple.train_models = models['models']

    def train_model(self, factors_data, begin_date, end_date, features):
        kd_logger.info("train model")
        alpha_model = load_module(self._model_name)(features=features,
                                                    **self._model_params)
        s = hashlib.md5(
            json.dumps({
                'name': self._model_name,
                'feature': alpha_model.formulas.names,
                'params': self._model_params
            }).encode(encoding="utf-8")).hexdigest()
        mid = create_id(original=s, digit=10)
        self._alpha_models = self.create_model(total_data=factors_data,
                                               name=self._model_name,
                                               mid=mid,
                                               alpha_model=alpha_model,
                                               batch=self._batch,
                                               freq=self._freq,
                                               begin_date=begin_date,
                                               end_date=end_date)

    def create_factors(self, total_data, begin_date, end_date):
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
            res.append(new_factors)
        factors_data = pd.concat(res, axis=1)
        return factors_data

    def stacking_models(self, total_data, begin_date, end_date):
        features = self.features()
        alpha_model = load_module(self._model_name)(features=features,
                                                    **self._model_params)
        regressors = [x.alpha_model.device for x in self._model_sets]
        model = StackingRegressor(features=features,
                                  regressors=regressors,
                                  meta_regressor=alpha_model.device)
        s = hashlib.md5(
            json.dumps({
                'name': self._model_name,
                'feature': alpha_model.formulas.names,
                'params': self._model_params
            }).encode(encoding="utf-8")).hexdigest()
        mid = create_id(original=s, digit=10)

        self._alpha_models = self.create_model(total_data=total_data,
                                               name=self._model_name,
                                               mid=mid,
                                               alpha_model=model,
                                               batch=self._batch,
                                               freq=self._freq,
                                               begin_date=begin_date,
                                               end_date=end_date)

    def dump_models(self):
        res = []
        if not self._stacking:
            for model in self._model_sets:
                rs = {'model': encode(model), 'id': model.id}
                res.append(rs)
        desc = {
            'model_sets':
            res,
            'base_model':
            encode({
                'name': self._model_name,
                'params': self._model_params,
                'batch': self._batch,
                'freq': self._freq,
                'horizon': self._horizon,
                'offset': self._offset,
                'models': self._alpha_models['models'],
                'id': self._alpha_models['id']
            }),
            'stacking':
            self._stacking,
            'version':
            1.0
        }
        return encode(desc)

    def generate_models(self, total_data, begin_date, end_date):
        kd_logger.info("generate models")
        if not self._stacking:
            self.train_models(total_data=total_data,
                              begin_date=begin_date,
                              end_date=end_date)
            factors_data = self.create_factors(total_data=total_data,
                                               begin_date=begin_date,
                                               end_date=end_date)
            features = factors_data.columns.tolist()
            factors_data = factors_data.reset_index().merge(
                total_data[['trade_date', 'code', 'nxt1_ret']])

            self.train_model(factors_data=factors_data,
                             begin_date=begin_date,
                             end_date=end_date,
                             features=features)
        else:
            self.stacking_models(total_data=total_data,
                                 begin_date=begin_date,
                                 end_date=end_date)

    def generate_predict(self, total_data, begin_date, end_date):
        kd_logger.info("generate predict")
        if not self._stacking:
            factors_data = self.create_factors(total_data=total_data,
                                               begin_date=begin_date,
                                               end_date=end_date)
            new_factors = self.predict(mid=self._alpha_models['id'],
                                       total_data=factors_data.reset_index(),
                                       models=self._alpha_models['models'],
                                       freq=self._freq,
                                       batch=self._batch,
                                       begin_date=begin_date,
                                       end_date=end_date)
        else:
            new_factors = self.predict(mid=self._alpha_models['id'],
                                       total_data=total_data,
                                       models=self._alpha_models['models'],
                                       freq=self._freq,
                                       batch=self._batch,
                                       begin_date=begin_date,
                                       end_date=end_date)

        return new_factors