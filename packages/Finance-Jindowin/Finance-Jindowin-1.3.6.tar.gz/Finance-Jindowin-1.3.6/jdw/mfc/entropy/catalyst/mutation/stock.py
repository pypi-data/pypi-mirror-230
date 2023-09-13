# -*- coding: utf-8 -*-
from jdw.data.SurfaceAPI.stock.yields import StkYields
from jdw.data.SurfaceAPI.stock.factors import StkFactors
from jdw.data.SurfaceAPI.universe import StkUniverse
from jdw.data.SurfaceAPI.stock.industry import Industry
from jdw.mfc.entropy.catalyst.mutation.base import Base


class StockMutation(Base):

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
        super(StockMutation, self).__init__(offset=offset,
                                            horizon=horizon,
                                            factor_columns=factor_columns,
                                            universe=universe,
                                            yields_class=StkYields,
                                            universe_class=StkUniverse,
                                            industry_class=Industry,
                                            factors_class=StkFactors,
                                            industry_name=industry_name,
                                            industry_level=industry_level,
                                            factors_normal=factors_normal,
                                            operators=operators,
                                            yield_name=yield_name)

    def industry_fillna(self, industry_data, factors_data):
        factors_data = factors_data.merge(industry_data,
                                          on=['trade_date', 'code'])
        factors_data = self.industry_median(factors_data)
        return factors_data
