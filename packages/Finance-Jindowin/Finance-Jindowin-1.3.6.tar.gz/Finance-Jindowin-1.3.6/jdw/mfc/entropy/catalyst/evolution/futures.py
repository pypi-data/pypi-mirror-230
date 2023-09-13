# -*- coding: utf-8 -*-
from jdw.data.SurfaceAPI.futures.yields import FutYields
from jdw.data.SurfaceAPI.futures.factors import FutFactors
from jdw.data.SurfaceAPI.universe import FutUniverse
from jdw.data.SurfaceAPI.futures.classify import FutClassify
from jdw.data.SurfaceAPI.dummy import Dummy
from jdw.mfc.entropy.catalyst.evolution.base import Base


class FuturesEvolution(Base):

    def __init__(self,
                 thresh,
                 universe,
                 factor_columns,
                 industry_name,
                 industry_level,
                 is_weighted=False,
                 dummy_name=None,
                 is_loop=False,
                 offset=0,
                 horizon=0,
                 model_sets=None,
                 params_sets={},
                 factors_normal=True,
                 callback_save=None,
                 yield_name='returns'):
        super(FuturesEvolution, self).__init__(yields_class=FutYields,
                                               factors_class=FutFactors,
                                               universe_class=FutUniverse,
                                               industry_class=FutClassify,
                                               dummy_class=Dummy,
                                               is_weighted=is_weighted,
                                               thresh=thresh,
                                               offset=offset,
                                               horizon=horizon,
                                               universe=universe,
                                               dummy_name=dummy_name,
                                               is_loop=is_loop,
                                               factor_columns=factor_columns,
                                               industry_name=industry_name,
                                               industry_level=industry_level,
                                               model_sets=model_sets,
                                               params_sets=params_sets,
                                               factors_normal=factors_normal,
                                               callback_save=callback_save,
                                               yield_name=yield_name)

    def industry_fillna(self, industry_data, factors_data):
        factors_data = factors_data.merge(industry_data.drop(['trade_date'],
                                                             axis=1),
                                          on=['code'])
        factors_data = self.industry_median(factors_data)
        return factors_data