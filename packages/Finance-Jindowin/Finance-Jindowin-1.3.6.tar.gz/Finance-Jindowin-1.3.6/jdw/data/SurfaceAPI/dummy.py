# -*- coding: utf-8 -*-
import pdb
import pandas as pd
from sqlalchemy import select, and_, join
from jdw.data.SurfaceAPI.engine import FetchKDEngine
from jdw.data.SurfaceAPI.universe import Universe


class Dummy(object):

    def __init__(self, table_name=None):
        self._engine = FetchKDEngine()
        self._table_name = table_name if table_name is not None else 'stk_derived_dummy'
        self._table_model = self._engine.table_model(self._table_name)

    def fetch(self, universe, name, start_date, end_date):
        if isinstance(universe, Universe):
            cond = universe._query_statements(start_date, end_date)
            universe_model = universe._table_model
            big_table = join(
                self._table_model, universe_model,
                and_(self._table_model.trade_date == universe_model.trade_date,
                     self._table_model.code == universe_model.code,
                     self._table_model.__dict__[name] == 1,
                     self._table_model.flag == 1, cond))

            query = select([self._table_model.trade_date,
                        self._table_model.code]).select_from(big_table)\
            .order_by(self._table_model.trade_date, self._table_model.code)
        else:
            query = select([
                self._table_model.trade_date,
                self._table_model.code,
            ]).where(
                and_(
                    self._table_model.trade_date.between(start_date, end_date),
                    self._table_model.__dict__[name] == 1,
                    self._table_model.code.in_(universe))).order_by(
                        self._table_model.trade_date, self._table_model.code)
        return pd.read_sql(query, self._engine.client()).dropna()
