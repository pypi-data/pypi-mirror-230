# -*- coding: utf-8 -*-
import pandas as pd
from jdw.kdutils.logger import kd_logger
from jdw.mfc.entropy.gravity.dendall.base import Base
from jdw.data.SurfaceAPI.stock.factors import StkFactors
from jdw.data.SurfaceAPI.universe import StkUniverse
from jdw.data.SurfaceAPI.stock.yields import StkYields
from jdw.data.SurfaceAPI.index_market import IndexMarket
from jdw.data.SurfaceAPI.stock.industry import Industry
from jdw.data.SurfaceAPI.index_component import IndexComponent
from jdw.data.SurfaceAPI.stock.risk_model import RiskModel


class StockDendall(Base):

    def __init__(self,
                 horizon=0,
                 offset=0,
                 risk_model='day',
                 industry_name='sw',
                 industry_level=1,
                 factor_columns=None,
                 alpha_model=None,
                 factors_data=None,
                 benchmark=None,
                 universe=None):
        super(StockDendall, self).__init__(factor_class=StkFactors,
                                           industry_class=Industry,
                                           universe_class=StkUniverse,
                                           index_yields_class=IndexMarket,
                                           yields_class=StkYields,
                                           horizon=horizon,
                                           offset=offset,
                                           industry_name=industry_name,
                                           industry_level=industry_level,
                                           factors_data=factors_data,
                                           factor_columns=factor_columns,
                                           alpha_model=alpha_model,
                                           benchmark=benchmark,
                                           universe=universe)
        self._risk_model = risk_model
        self._category = 'onlylong'
        self._map_universe = {
            'sh50': '000016',
            'zz500': '000985',
            'hs300': '000300',
            'zz800': '000906',
            'zz1000': '000852'
        }

    def merge(self, industry_data, component_data):
        industry_dummy = pd.get_dummies(
            industry_data.set_index(['trade_date',
                                     'code'])['industry_code']).reset_index()

        total_data = component_data.merge(industry_data,
                                          on=['trade_date', 'code']).merge(
                                              industry_dummy,
                                              on=['trade_date', 'code'])
        return total_data

    def create_component(self, begin_date, end_date, universe=None):
        kd_logger.info("start create component data")
        component_data = IndexComponent().query(
            benchmark=self._map_universe[universe],
            start_date=begin_date,
            end_date=end_date)
        return component_data

    def create_riskmodel(self, begin_date, end_date, universe=None):
        kd_logger.info("start create risk model data")
        risk_model = RiskModel(risk_model=self._risk_model)
        factor_model, risk_cov, risk_exp = risk_model.fetch_cov(
            universe=universe,
            start_date=begin_date,
            end_date=end_date,
            model_type='factor')
        return factor_model, risk_cov, risk_exp
