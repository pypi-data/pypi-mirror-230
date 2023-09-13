# -*- coding: utf-8 -*-
from jdw.mfc.entropy.gravity.carnot.base import Base
from jdw.data.SurfaceAPI.stock.factors import StkFactors
from jdw.data.SurfaceAPI.universe import StkUniverse
from jdw.data.SurfaceAPI.stock.yields import StkYields
from jdw.data.SurfaceAPI.stock.industry import Industry


class StockCarnot(Base):

    def __init__(self,
                 model_name,
                 model_params,
                 features,
                 factors_normal=True,
                 horizon=1,
                 batch=1,
                 freq=1,
                 offset=0,
                 factor_name=None,
                 industry_name='sw',
                 industry_level=1,
                 yield_name='ret',
                 universe=None):
        super(StockCarnot, self).__init__(factor_class=StkFactors,
                                          universe_class=StkUniverse,
                                          yields_class=StkYields,
                                          industry_class=Industry,
                                          model_name=model_name,
                                          model_params=model_params,
                                          features=features,
                                          factors_normal=factors_normal,
                                          batch=batch,
                                          freq=freq,
                                          offset=offset,
                                          horizon=horizon,
                                          factor_name=factor_name,
                                          industry_name=industry_name,
                                          industry_level=industry_level,
                                          yield_name=yield_name,
                                          universe=universe)
