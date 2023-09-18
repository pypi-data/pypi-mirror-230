# -*- coding: utf-8 -*-
from jdw.mfc.entropy.gravity.mixture.base import Base
from jdw.data.SurfaceAPI.stock.factors import StkFactors
from jdw.data.SurfaceAPI.universe import StkUniverse
from jdw.data.SurfaceAPI.stock.yields import StkYields
from jdw.data.SurfaceAPI.stock.industry import Industry


class StockMixture(Base):

    def __init__(self,
                 model_name=None,
                 model_params=None,
                 model_sets=[],
                 batch=1,
                 freq=1,
                 horizon=1,
                 offset=1,
                 stacking=False,
                 factors_normal=True,
                 industry_name='sw',
                 industry_level=1,
                 yield_name='returns',
                 universe=None):
        super(StockMixture, self).__init__(factor_class=StkFactors,
                                           universe_class=StkUniverse,
                                           yields_class=StkYields,
                                           industry_class=Industry,
                                           model_name=model_name,
                                           model_params=model_params,
                                           model_sets=model_sets,
                                           batch=batch,
                                           freq=freq,
                                           horizon=horizon,
                                           offset=offset,
                                           stacking=stacking,
                                           factors_normal=factors_normal,
                                           industry_name=industry_name,
                                           industry_level=industry_level,
                                           yield_name=yield_name,
                                           universe=universe)
