# -*- coding: utf-8 -*-
from jdw.mfc.entropy.gravity.mixture.base import Base
from jdw.data.SurfaceAPI.futures.factors import FutFactors
from jdw.data.SurfaceAPI.universe import FutUniverse
from jdw.data.SurfaceAPI.futures.yields import FutYields
from jdw.data.SurfaceAPI.futures.classify import FutClassify


class FuturesMixture(Base):

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
                 industry_name='kh',
                 industry_level=1,
                 yield_name='returns',
                 universe=None):
        super(FuturesMixture, self).__init__(factor_class=FutFactors,
                                             universe_class=FutUniverse,
                                             yields_class=FutYields,
                                             industry_class=FutClassify,
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
