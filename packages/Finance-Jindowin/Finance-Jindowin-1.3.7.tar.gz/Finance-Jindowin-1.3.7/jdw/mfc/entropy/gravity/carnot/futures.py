# -*- coding: utf-8 -*-
from jdw.mfc.entropy.gravity.carnot.base import Base
from jdw.data.SurfaceAPI.futures.factors import FutFactors
from jdw.data.SurfaceAPI.universe import FutUniverse
from jdw.data.SurfaceAPI.futures.yields import FutYields
from jdw.data.SurfaceAPI.futures.classify import FutClassify


class FuturesCarnot(Base):

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
                 industry_name='kh',
                 industry_level=1,
                 yield_name='ret',
                 universe=None):
        super(FuturesCarnot, self).__init__(factor_class=FutFactors,
                                            universe_class=FutUniverse,
                                            yields_class=FutYields,
                                            industry_class=FutClassify,
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
