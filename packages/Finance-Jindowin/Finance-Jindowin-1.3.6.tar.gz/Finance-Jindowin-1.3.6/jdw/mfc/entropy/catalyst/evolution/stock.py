# -*- coding: utf-8 -*-
from jdw.data.SurfaceAPI.stock.yields import StkYields
from jdw.data.SurfaceAPI.stock.factors import StkFactors
from jdw.data.SurfaceAPI.universe import StkUniverse
from jdw.data.SurfaceAPI.stock.industry import Industry
from jdw.data.SurfaceAPI.dummy import Dummy
from jdw.mfc.entropy.catalyst.evolution.base import Base


class StockEvolution(Base):

    def __init__(self,
                 thresh,
                 universe,
                 factor_columns,
                 industry_name,
                 industry_level,
                 is_weighted=True,
                 dummy_name=None,
                 is_loop=False,
                 offset=0,
                 horizon=0,
                 model_sets=None,
                 params_sets={},
                 factors_normal=True,
                 callback_save=None,
                 yield_name='returns'):
        super(StockEvolution, self).__init__(yields_class=StkYields,
                                             factors_class=StkFactors,
                                             universe_class=StkUniverse,
                                             industry_class=Industry,
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
        factors_data = factors_data.merge(industry_data,
                                          on=['trade_date', 'code'])
        factors_data = self.industry_median(factors_data)
        return factors_data