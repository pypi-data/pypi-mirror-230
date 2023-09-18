# -*- coding: utf-8 -*-
import pdb
import pandas as pd
from sqlalchemy import select, and_, join
from jdw.data.SurfaceAPI.engine import FetchKDEngine
from jdw.data.SurfaceAPI.utilities import create_stats, shift_stats
from jdw.data.SurfaceAPI.universe import Universe


class Yields(object):

    def __init__(self, table_name=None):
        self._engine = FetchKDEngine()
        self._table_name = table_name if table_name is not None else 'stk_derived_yields'
        self._table_model = self._engine.table_model(self._table_name)

    def _fetch_returns(self,
                       universe,
                       name,
                       table_model,
                       start_date,
                       end_date,
                       horizon,
                       offset,
                       is_log=True,
                       benchmark=None):

        codes = universe.query(start_date,
                               end_date).code.unique().tolist() if isinstance(
                                   universe, Universe) else universe
        t1 = select([
            table_model.trade_date,
            table_model.code.label("code"),
            table_model.__dict__[name].label("chgPct")
        ]).where(
            and_(table_model.trade_date.between(start_date, end_date),
                 table_model.code.in_(codes),
                 table_model.flag == 1)).order_by(table_model.trade_date,
                                                  table_model.code)
        df1 = pd.read_sql(t1, self._engine.client()).dropna()
        df1 = create_stats(df=df1.copy(),
                           horizon=horizon,
                           offset=offset,
                           no_code=False,
                           is_log=is_log)

        if isinstance(universe, Universe):
            df2 = universe.query(start_date, end_date)
            df2["trade_date"] = pd.to_datetime(df2["trade_date"])
            df = pd.merge(df1, df2, on=["trade_date", "code"])
        else:
            df = df1.copy()
        df = df.set_index("trade_date")

        return df.reset_index().sort_values(['trade_date', 'code'])

    def fetch_yileds(self, universe, start_date, end_date, name, offset=None):
        universe_model = universe._table_model if isinstance(
            universe, Universe) else None

        cols = [
            self._table_model.trade_date, self._table_model.code,
            self._table_model.__dict__[name].label('nxt1_ret')
        ]
        if isinstance(universe, Universe):
            cond = universe._query_statements(start_date, end_date)
            big_table = join(
                self._table_model, universe_model,
                and_(self._table_model.trade_date == universe_model.trade_date,
                     self._table_model.flag == 1,
                     self._table_model.code == universe_model.code, cond))
            query = select(cols).select_from(big_table)
        else:
            clause_list = and_(
                self._table_model.flag == 1,
                self._table_model.code.in_(universe),
                self._table_model.trade_date.between(start_date, end_date))

            query = select(cols).where(clause_list)
        yields_data = pd.read_sql(query, self._engine.client())
        if offset is not None:
            yields_data = shift_stats(df=yields_data,
                                      name='nxt1_ret',
                                      offset=offset)
        return yields_data

    def codes_fetch(self, codes, start_date, end_date, name):
        cols = [
            self._table_model.trade_date, self._table_model.code,
            self._table_model.__dict__[name].label('nxt1_ret')
        ]
        clause_list = and_(
            self._table_model.flag == 1, self._table_model.code.in_(codes),
            self._table_model.trade_date.between(start_date, end_date))

        query = select(cols).where(clause_list)
        return pd.read_sql(query, self._engine.client())

    def universe_fetch(self,
                       universe,
                       start_date,
                       end_date,
                       name,
                       horizon=0,
                       offset=0):
        universe_model = universe._table_model
        cols = [
            self._table_model.trade_date, self._table_model.code,
            self._table_model.__dict__[name].label('nxt1_ret')
        ]

        cond = universe._query_statements(start_date, end_date)
        big_table = join(
            self._table_model, universe_model,
            and_(self._table_model.trade_date == universe_model.trade_date,
                 self._table_model.flag == 1,
                 self._table_model.code == universe_model.code, cond))
        query = select(cols).select_from(big_table)
        df = pd.read_sql(query, self._engine.client())
        return df
