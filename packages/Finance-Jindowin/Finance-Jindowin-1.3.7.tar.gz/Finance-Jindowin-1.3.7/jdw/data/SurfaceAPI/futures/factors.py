# -*- coding: utf-8 -*-
import pdb
import pandas as pd
import numpy as np
from sqlalchemy import select, and_, outerjoin, join
from jdw.data.SurfaceAPI.factors import Factors
from jdw.data.SurfaceAPI.universe import Universe


class FutFactors(Factors):

    def __init__(self) -> None:
        super(FutFactors, self).__init__(name='fut_factor')

    def derivo(self,
               name,
               start_date,
               end_date,
               universe,
               category,
               columns=None):
        factor_model = self._engine.table_model(category + '_{0}'.format(name))
        cols = [
            factor_model.trade_date, factor_model.code, factor_model.name,
            factor_model.value
        ]
        if isinstance(universe, Universe):
            cond = universe._query_statements(start_date, end_date)
            universe_model = universe._table_model
            cond1 = and_(factor_model.trade_date == universe_model.trade_date,
                         factor_model.code == universe_model.code,
                         factor_model.flag == 1, cond)

            if isinstance(columns, list):
                cond1 = cond1 & (factor_model.name.in_(columns))

            big_table = join(factor_model, universe_model, cond1)
            query = select(cols).select_from(big_table)\
            .order_by(factor_model.trade_date, factor_model.code)
        else:
            cond1 = and_(factor_model.trade_date.between(start_date, end_date),
                         factor_model.code.in_(universe))
            if isinstance(columns, list):
                cond1 = cond1 & (factor_model.name.in_(columns))
            query = select(cols).where(cond1).order_by(factor_model.trade_date,
                                                       factor_model.code)
        df = pd.read_sql(query, self._engine.client())
        if 'id' in df.columns:
            df.drop('id', axis=1, inplace=True)
        if 'flag' in df.columns:
            df.drop('flag', axis=1, inplace=True)
        if 'timestamp' in df.columns:
            df.drop('timestamp', axis=1, inplace=True)
        df.replace([-np.inf, np.inf], np.nan, inplace=True)
        return df

    def derive(self,
               start_date,
               end_date,
               universe,
               category,
               columns=None,
               format=0):
        #0 matrix  1 serise  2 DatFrame
        factors_data = self.derivo(name='derive',
                                   start_date=start_date,
                                   end_date=end_date,
                                   universe=universe,
                                   category=category,
                                   columns=columns)
        if format == 2:
            return factors_data.set_index(['trade_date', 'code', 'name'
                                           ])['value'].unstack().reset_index()
        elif format == 0:
            factors_data = factors_data.set_index(
                ['trade_date', 'code', 'name'])['value'].unstack().unstack()
        return factors_data

    def orthozd(self,
                start_date,
                end_date,
                universe,
                category,
                columns=None,
                format=0):
        #0 matrix  1 serise  2 DatFrame
        columns = [
            "{0}_ord_{1}".format(col, universe.u_name) for col in columns
        ] if isinstance(columns, list) else None
        factors_data = self.derivo(name='orthozd',
                                   start_date=start_date,
                                   end_date=end_date,
                                   universe=universe,
                                   category=category,
                                   columns=columns)
        if format == 2:
            return factors_data.set_index(['trade_date', 'code', 'name'
                                           ])['value'].unstack().reset_index()
        elif format == 0:
            factors_data = factors_data.set_index(
                ['trade_date', 'code', 'name'])['value'].unstack().unstack()
        return factors_data

    def orthozn(self,
                start_date,
                end_date,
                universe,
                category,
                columns=None,
                format=0):
        #0 matrix  1 serise  2 DatFrame
        columns = [
            "{0}_orn_{1}".format(col, universe.u_name) for col in columns
        ] if isinstance(columns, list) else None
        factors_data = self.derivo(name='orthozn',
                                   start_date=start_date,
                                   end_date=end_date,
                                   universe=universe,
                                   category=category,
                                   columns=columns)
        if format == 2:
            return factors_data.set_index(['trade_date', 'code', 'name'
                                           ])['value'].unstack().reset_index()
        elif format == 0:
            factors_data = factors_data.set_index(
                ['trade_date', 'code', 'name'])['value'].unstack().unstack()
        return factors_data