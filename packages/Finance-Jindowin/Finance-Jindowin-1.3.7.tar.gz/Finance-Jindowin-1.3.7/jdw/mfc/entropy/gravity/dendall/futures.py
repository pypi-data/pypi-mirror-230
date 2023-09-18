# -*- coding: utf-8 -*-
import copy, pdb
import numpy as np
import pandas as pd
from ultron.tradingday import *
from ultron.factor.covariance.cov_engine import CovEngine

from ultron.optimize.riskmodel import FullRiskModel
from jdw.kdutils.logger import kd_logger
from jdw.mfc.entropy.gravity.dendall.base import Base
from jdw.data.SurfaceAPI.universe import FutUniverse
from jdw.data.SurfaceAPI.futures.yields import FutYields
from jdw.data.SurfaceAPI.futures.factors import FutFactors
from jdw.data.SurfaceAPI.index_market import IndexMarket
from jdw.data.SurfaceAPI.futures.classify import FutClassify


class FuturesDendall(Base):

    def __init__(self,
                 horizon=0,
                 offset=0,
                 cov_window=20,
                 cov_model='unshrunk',
                 industry_name='kh',
                 industry_level=1,
                 alpha_model=None,
                 factor_columns=None,
                 factors_data=None,
                 benchmark=None,
                 universe=None):
        super(FuturesDendall, self).__init__(factor_class=FutFactors,
                                             industry_class=FutClassify,
                                             universe_class=FutUniverse,
                                             index_yields_class=IndexMarket,
                                             yields_class=FutYields,
                                             horizon=horizon,
                                             offset=offset,
                                             industry_name=industry_name,
                                             industry_level=industry_level,
                                             factors_data=factors_data,
                                             factor_columns=factor_columns,
                                             alpha_model=alpha_model,
                                             benchmark=benchmark,
                                             universe=universe)
        self._cov_window = cov_window
        self._cov_model = cov_model
        self._category = 'longshort'

    def merge(self, industry_data, component_data):
        industry_dummy = pd.get_dummies(
            industry_data.set_index(['trade_date',
                                     'code'])['industry_code']).reset_index()

        total_data = component_data.merge(
            industry_data.drop(['trade_date'], axis=1),
            on=['code']).merge(industry_dummy.drop(['trade_date'], axis=1),
                               on=['code'])
        return total_data

    def create_riskmodel(self, begin_date, end_date, universe=None):
        models = {}
        start_date = advanceDateByCalendar('china.sse', begin_date,
                                           "-{}b".format(self._cov_window),
                                           BizDayConventions.Following)
        yields_data = FutYields().fetch_yileds(universe=universe,
                                               start_date=start_date,
                                               end_date=end_date,
                                               name='ret')
        yields_data = yields_data.set_index(['trade_date', 'code']).unstack()
        dates = makeSchedule(begin_date, end_date, '1b', calendar='china.sse')
        for ref_date in dates:
            ref_begin_date = advanceDateByCalendar(
                'china.sse', ref_date, '-{0}b'.format(self._cov_window))
            ref_end_date = advanceDateByCalendar('china.sse', ref_date, '-0b')
            rtb = yields_data.loc[ref_begin_date:ref_end_date].fillna(0)
            cov = CovEngine.calc_cov(name=self._cov_model,
                                     ret_tb=rtb,
                                     window=self._cov_window)
            model = FullRiskModel(cov)
            models[ref_date] = model
        return models, None, None

    def create_component(self, begin_date, end_date, universe=None):
        universe_data = FutUniverse(u_name=universe).query(
            start_date=begin_date, end_date=end_date)
        universe_data['weight'] = 0.0
        return universe_data
