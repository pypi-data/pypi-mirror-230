# -*- coding: utf-8 -*-
from jdw.data.SurfaceAPI.futures.yields import FutYields
from jdw.data.SurfaceAPI.futures.factors import FutFactors
from jdw.data.SurfaceAPI.universe import FutUniverse
from jdw.data.SurfaceAPI.futures.classify import FutClassify
from jdw.mfc.entropy.catalyst.mutation.base import Base


class FuturesMutation(Base):

    def __init__(self,
                 offset,
                 horizon,
                 factor_columns,
                 universe,
                 industry_name,
                 industry_level,
                 factors_normal=True,
                 operators=None,
                 yield_name='returns'):
        super(FuturesMutation, self).__init__(offset=offset,
                                              horizon=horizon,
                                              factor_columns=factor_columns,
                                              universe=universe,
                                              yields_class=FutYields,
                                              universe_class=FutUniverse,
                                              industry_class=FutClassify,
                                              factors_class=FutFactors,
                                              industry_name=industry_name,
                                              industry_level=industry_level,
                                              factors_normal=factors_normal,
                                              operators=operators,
                                              yield_name=yield_name)

    def industry_fillna(self, industry_data, factors_data):
        factors_data = factors_data.merge(industry_data.drop(['trade_date'],
                                                             axis=1),
                                          on=['code'])
        factors_data = self.industry_median(factors_data)
        return factors_data