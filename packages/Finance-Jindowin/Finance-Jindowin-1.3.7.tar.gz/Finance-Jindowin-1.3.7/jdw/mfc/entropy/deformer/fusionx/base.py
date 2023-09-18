# -*- coding: utf-8 -*-
import copy, os, hashlib, json, datetime, pdb
import pandas as pd
from ultron.tradingday import *
from ultron.strategy.deformer import FusionX
from ultron.kdutils.file import dump_pickle, load_pickle
from ultron.kdutils.create_id import create_id
from ultron.factor.data.transformer import Transformer


class Base(object):

    def __init__(self,
                 batch,
                 freq,
                 offset,
                 horizon,
                 id=None,
                 directory=None,
                 is_full=False):
        self.batch = batch
        self.freq = freq
        self.horizon = horizon
        self.offset = offset
        self.directory = directory if directory is not None else os.path.join(
            os.getcwd(), "fusionx")
        self.id = id
        self.is_full = is_full

    def _create_id(self, name, features, **kwargs):
        if self.id is None:
            params = copy.deepcopy(kwargs)
            params['batch'] = self.batch
            params['freq'] = self.freq
            params['name'] = name
            params['features'] = Transformer(features).names
            s = hashlib.md5(
                json.dumps(params).encode(encoding="utf-8")).hexdigest()
            self.id = "{0}".format(create_id(original=s, digit=10))
        return self.id

    def create_directory(self, name, features, **kwargs):
        if self.id is None:
            self.id = self._create_id(name, features, **kwargs)
        self.directory = os.path.join(self.directory, self.id)

    def set_model(self, model):
        self.base_model = model
        self.id = self.base_model.id
        self.create_directory(model.name, model.features, **model.kwargs)

    def create_model(self, name, features, universe, paramo=None, **kwargs):
        self.base_model = FusionX(name,
                                  features=features,
                                  universe=universe,
                                  paramo=paramo,
                                  **kwargs)
        self.id = self.base_model.id
        self.create_directory(name, features, **kwargs)

    def local_directory(self, models, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

        for trade_date, model in models.items():
            filename = os.path.join(
                self.directory,
                "{0}.h5".format(trade_date.strftime('%Y-%m-%d')))
            dump_pickle(model.save(), filename)

    def create_data(self,
                    total_data,
                    name=None,
                    returns=None,
                    begin_date=None,
                    end_date=None,
                    **kwargs):
        models = {}
        self.create_directory(name, features=None, **kwargs)
        ### 加载模型
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                filename = os.path.join(root, file)
                date = file.split(".")[0]
                desc = load_pickle(filename)
                models[datetime.datetime.strptime(
                    date, '%Y-%m-%d')] = FusionX.load(desc)
        alpha_model = next(iter(models.values()))
        if self.is_full and alpha_model.category == 'combine':
            return self.forecast(total_data=total_data,
                                 returns=returns,
                                 models=models)
        else:
            return self.forecast(
                total_data=total_data, returns=returns, models=models
            ) if self.batch == 0 and self.freq == 0 else self.predict(
                total_data=total_data,
                returns=returns,
                models=models,
                begin_date=begin_date,
                end_date=end_date)

    def forecast(self, total_data, returns, models):
        total_data['trade_date'] = pd.to_datetime(total_data['trade_date'])
        train_data = total_data.sort_values(by=['trade_date', 'code'])
        alpha_model = next(iter(models.values()))
        base_model = copy.deepcopy(alpha_model)

        train_data = train_data.sort_values(by=['trade_date', 'code'])
        train_data = base_model.formulas.transform(
            'code',
            train_data.set_index('trade_date')).reset_index().sort_values(
                by=['trade_date', 'code'])
        ne_x = train_data[base_model.formulas.dependency].values

        X = pd.DataFrame(ne_x,
                         columns=base_model.formulas.dependency,
                         index=train_data.set_index(
                             ['trade_date',
                              'code']).index).fillna(0).reset_index()

        y = base_model.predict(
            X, returns
        ) if alpha_model.category == 'combine' else base_model.predict(X)
        return y.set_index(['trade_date', 'code'
                            ]) if alpha_model.category == 'combine' else y

    def predict(self, total_data, returns, models, begin_date, end_date):
        total_data['trade_date'] = pd.to_datetime(total_data['trade_date'])
        begin_date = total_data['trade_date'].dt.strftime(
            '%Y-%m-%d').min() if begin_date is None else begin_date
        end_date = total_data['trade_date'].dt.strftime(
            '%Y-%m-%d').max() if end_date is None else end_date
        last_date = total_data['trade_date'].dt.strftime('%Y-%m-%d').max()
        date_label = pd.DatetimeIndex(total_data.trade_date).to_pydatetime()
        dates = makeSchedule(begin_date,
                             end_date,
                             '1b',
                             calendar='china.sse',
                             dateRule=BizDayConventions.Following,
                             dateGenerationRule=DateGeneration.Backward)
        keys = models.keys()
        res = []
        for d in dates:
            sub_list = list(filter(lambda x: x <= d, keys))
            if len(sub_list) == 0:
                continue
            alpha_model = models[sub_list[0]]
            start_date = advanceDateByCalendar(
                'china.sse', d, "-{}b".format(self.batch + self.freq),
                BizDayConventions.Following)
            ref_dates = makeSchedule(
                start_date,
                d,
                '1b',
                calendar='china.sse',
                dateRule=BizDayConventions.Following,
                dateGenerationRule=DateGeneration.Backward)
            '''
            if ref_dates[-1] == d:
                end = ref_dates[-2]
                start = ref_dates[
                    -self.batch -
                    1] if self.batch <= len(ref_dates) - 1 else ref_dates[0]
            else:
                end = ref_dates[-1]
                start = ref_dates[-self.batch] if self.batch <= len(
                    ref_dates) else ref_dates[0]
            '''
            if last_date < d.strftime('%Y-%m-%d'):
                break
            end = ref_dates[-1]
            start = ref_dates[
                -self.batch -
                1] if self.batch <= len(ref_dates) - 1 else ref_dates[0]

            index = (date_label >= start) & (date_label <= end)
            base_model = copy.deepcopy(alpha_model)
            train_data = total_data.set_index(
                'trade_date').loc[index].reset_index()
            if train_data.empty:
                continue
            train_data = train_data.sort_values(by=['trade_date', 'code'])
            #train_data = base_model.formulas.transform(
            #    'code',
            #    train_data.set_index('trade_date')).reset_index().sort_values(
            #        by=['trade_date', 'code'])
            ne_x = train_data[base_model.formulas.dependency].values

            X = pd.DataFrame(ne_x,
                             columns=base_model.formulas.dependency,
                             index=train_data.set_index(
                                 ['trade_date', 'code']).index).reset_index()
            if returns is None:
                y = base_model.predict(X)
            else:
                y = base_model.predict(X, returns)
            # 获取最新一期
            #y = y.reset_index().sort_values(
            #    by=['trade_date', 'code']).drop_duplicates(subset=['code'],
            #                                               keep='last')
            y = y.loc[d].reset_index()
            y['trade_date'] = d
            res.append(y.set_index(['trade_date', 'code']))
        return pd.concat(res, axis=0)

    def train(self,
              total_data,
              begin_date,
              end_date,
              is_save=1):  # 0 不保存   1. 保存本地  2.保存OSS
        models = self.educate(
            total_data=total_data
        ) if self.batch == 0 and self.freq == 0 else self.fit(
            total_data=total_data, begin_date=begin_date, end_date=end_date)
        if is_save == 1:
            self.local_directory(models, self.directory)

    def educate(self, total_data, begin_date=None, end_date=None):
        total_data['trade_date'] = pd.to_datetime(total_data['trade_date'])
        begin_date = total_data['trade_date'].dt.strftime(
            '%Y-%m-%d').min() if begin_date is None else begin_date
        end_date = total_data['trade_date'].dt.strftime(
            '%Y-%m-%d').max() if end_date is None else end_date
        models = {}
        base_model = copy.deepcopy(self.base_model)
        train_data = total_data.fillna(0)
        if train_data.empty:
            return models
        train_data = train_data.sort_values(by=['trade_date', 'code'])
        ne_y = train_data[['nxt1_ret']].values

        ne_x = train_data[base_model.formulas.dependency].values

        X = pd.DataFrame(ne_x,
                         columns=base_model.formulas.dependency,
                         index=train_data.set_index(['trade_date', 'code'
                                                     ]).index).reset_index()
        Y = ne_y
        base_model.fit(X, Y)
        d = advanceDateByCalendar('china.sse', end_date, "1b",
                                  BizDayConventions.Following)
        models[d] = base_model
        return models

    def fit(self, total_data, begin_date=None, end_date=None):
        ## 切割交易日
        total_data['trade_date'] = pd.to_datetime(total_data['trade_date'])
        begin_date = total_data['trade_date'].dt.strftime(
            '%Y-%m-%d').min() if begin_date is None else begin_date
        end_date = total_data['trade_date'].dt.strftime(
            '%Y-%m-%d').max() if end_date is None else end_date
        models = {}
        date_label = pd.DatetimeIndex(total_data.trade_date).to_pydatetime()
        dates = makeSchedule(begin_date,
                             end_date,
                             '{}b'.format(self.freq),
                             calendar='china.sse',
                             dateRule=BizDayConventions.Following,
                             dateGenerationRule=DateGeneration.Backward)

        for d in dates:
            start_date = advanceDateByCalendar(
                'china.sse', d, "-{}b".format(self.freq + self.batch +
                                              self.offset + self.horizon),
                BizDayConventions.Following)
            ref_dates = makeSchedule(
                start_date,
                d,
                '1b',
                calendar='china.sse',
                dateRule=BizDayConventions.Following,
                dateGenerationRule=DateGeneration.Backward)
            '''
            if ref_dates[-1] == d:
                end = ref_dates[-1]
                start = ref_dates[
                    -self.batch -
                    1] if self.batch <= len(ref_dates) - 1 else ref_dates[0]
            else:
                end = ref_dates[-1]
                start = ref_dates[-self.batch] if self.batch <= len(
                    ref_dates) else ref_dates[0]
            '''
            pos = self.offset + self.horizon
            end = ref_dates[-pos]
            start = ref_dates[-(pos + self.batch) + 1]
            index = (date_label >= start) & (date_label <= end)
            base_model = copy.deepcopy(self.base_model)
            train_data = total_data.set_index(
                'trade_date').loc[index].reset_index().fillna(0)
            if train_data.empty:
                continue
            train_data = train_data.sort_values(by=['trade_date', 'code'])

            ne_y = train_data[['nxt1_ret']].values
            #train_data = base_model.formulas.transform(
            #    'code',
            #    train_data.set_index('trade_date')).reset_index().sort_values(
            #        by=['trade_date', 'code'])
            ne_x = train_data[base_model.formulas.dependency].values

            X = pd.DataFrame(ne_x,
                             columns=base_model.formulas.dependency,
                             index=train_data.set_index(
                                 ['trade_date',
                                  'code']).index).fillna(0).reset_index()
            Y = ne_y
            if 'sample_weight' in train_data.columns:
                sample_weight = train_data['sample_weight']
                base_model.fit(X, Y, sample_weight=sample_weight)
            else:
                base_model.fit(X, Y)
            models[d] = base_model
        return models