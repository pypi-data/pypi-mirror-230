# -*- coding: utf-8 -*-
import re, pdb
import dolphindb as ddb
import pandas as pd


class DDBEngine(object):

    def _parser(self, url):
        pattern = r"ddb://([^:]+):(.+?)@([^:]+):(\d+)"
        match = re.match(pattern, url)
        user = match.group(1)
        password = match.group(2)
        address = match.group(3)
        port = match.group(4)
        return user, password, address, int(port)

    def __init__(self, url):
        self._engine = ddb.session()
        user, password, address, port = self._parser(url)
        self._engine.connect(host=address,
                             port=port,
                             userid=user,
                             password=password)

    def ddb_engine(self):
        return self._engine


class FetchEngine(object):

    def __init__(self, name, url):
        self._name = name
        self._engine = DDBEngine(url=url)
        self._export_cfg = {}

    @classmethod
    def create_engine(cls, name):
        if name == 'ch':
            from .ch import ch_engine
            return ch_engine.__getattribute__('FetchCHEngine')
        else:
            ValueError("name:{0} is error".format(name))

    def to_ddb_table(self, table_name):
        strs = table_name.split('_')
        ddb_table = ''
        for ele in strs:
            ddb_table = ddb_table + ele[0].upper() + ele[1:]
        return ddb_table

    def get_table_schema(self, dbPath, tableName):
        sql = """schema(loadTable('{dbName}',`{table}))""".format(
            dbName=dbPath, table=tableName)
        data = self._engine.ddb_engine().run(sql)
        col_list = data['colDefs']['name'].to_list()
        return col_list

    def custom(self, table, clause_list, columns):
        return self.base(table_name=table,
                         clause_list=clause_list,
                         columns=columns)

    def base(self, table_name, columns=None, clause_list=None):
        db_name = self.to_ddb_table(table_name)
        dbPath = 'dfs://{0}'.format(db_name)
        if self._engine.ddb_engine().existsDatabase(
                dbPath) and self._engine.ddb_engine().existsTable(
                    dbPath, table_name):
            column_list = self.get_table_schema(dbPath, table_name)
            #cols = []
            if columns is not None:
                select_col = ''
                for col in columns:
                    if col in column_list:
                        select_col = select_col + col + ','
                    else:
                        print('{0} is not {1} column'.format(col, table_name))
                select_col = select_col[:-1]
            else:
                select_col = '*'

            sql = """select {select_col} from loadTable('{dbName}',`{table}) where 1==1""".format(
                dbName=dbPath, table=table_name, select_col=select_col)
            if clause_list is not None:
                for clause in clause_list:
                    sql = sql + ' and ' + clause
            data = self._engine.ddb_engine().run(sql)
        return data

    def handle_cfg_transpose(self, data, col, table):
        if table in self._export_cfg.keys() and len(data) > 0:
            table_cfg = self._export_cfg[table]
            if 'Columns' in table_cfg['Transpose'].keys():
                data = data.pivot(columns=table_cfg['Transpose']['Columns'],
                                  index=table_cfg['Transpose']['Index'],
                                  values=col).reset_index()
        return data

    def handle_cfg_select_cols(self, table, col):
        dbPath = 'dfs://' + self.to_ddb_table(table)
        if col == '':
            sql = """select * from loadTable('{dbName}',`{table}) where 1==1""".format(
                dbName=dbPath, table=table)
        else:
            if table in self._export_cfg.keys():
                table_cfg = self._export_cfg[table]
                select_cols = []
                select_cols.append(col)
                if 'Transpose' in table_cfg.keys():
                    if isinstance(table_cfg['Transpose']['Index'], list):
                        select_cols = select_cols + table_cfg['Transpose'][
                            'Index']
                    else:
                        select_cols.append(table_cfg['Transpose']['Index'])
                    if 'Columns' in table_cfg['Transpose'].keys():
                        select_cols.append(table_cfg['Transpose']['Columns'])
            else:

                col_list = self.get_table_schema(dbPath, table)
                select_cols = []
                if 'code' in col_list:
                    select_cols.append('code')
                if 'trade_date' in col_list:
                    select_cols.append('trade_date')
                elif 'publishDate' in col_list:
                    select_cols.append('publishDate')

            select_col_str = ''
            for col in select_cols:
                select_col_str = select_col_str + col + ','
            select_col_str = select_col_str[:-1]
            sql = """select {select_col_str} from loadTable('{dbName}',`{table}) where 1==1""".format(
                dbName=dbPath, table=table, select_col_str=select_col_str)

        return sql

    def handle_cfg_date_filter(self, sql, table, start_date, end_date):
        date_type = ''
        if table in self._export_cfg.keys():
            table_cfg = self._export_cfg[table]
            if 'IncUpdate' in table_cfg.keys():
                date_type = table_cfg['IncUpdate']
        else:
            dbPath = 'dfs://' + self.to_ddb_table(table)
            col_list = self.get_table_schema(dbPath, table)
            if 'trade_date' in col_list:
                date_type = 'trade_date'
            elif 'publishDate' in col_list:
                date_type = 'publishDate'

        if date_type != '':
            if start_date is not None:
                sql = sql + """ and date({date_type})>= {start_date}""".format(
                    date_type=date_type,
                    start_date=start_date.replace('-', '.'))

            if end_date is not None:
                sql = sql + """ and date({date_type})<= {end_date}""".format(
                    date_type=date_type, end_date=end_date.replace('-', '.'))
        return sql

    def handle_cfg_filter(self, sql, table):
        if table in self._export_cfg.keys():
            table_cfg = self._export_cfg[table]
            if 'Filter' in table_cfg.keys():
                for key in table_cfg['Filter']:
                    if isinstance(table_cfg['Filter'][key], str):
                        sql = sql + """ and {filter}= '{filter_value}'""".format(
                            filter=key, filter_value=table_cfg['Filter'][key])
                    else:
                        sql = sql + """ and {filter}= {filter_value}""".format(
                            filter=key, filter_value=table_cfg['Filter'][key])
        return sql

    def handle_codes_filter(self, sql, table, codes):
        if codes is None:
            return sql
        if isinstance(codes, str):
            if codes != '':
                codes = [codes]
            else:
                codes = []
        dbPath = 'dfs://' + self.to_ddb_table(table)
        col_list = self.get_table_schema(dbPath, table)
        if 'code' in col_list:
            codes_str = '('
            for code in codes:
                codes_str = codes_str + "'" + code + "',"
            codes_str = codes_str[:-1] + ')'
            sql = sql + """ and code in {codes_str}""".format(
                codes_str=codes_str)
        return sql