# -*- coding: utf-8 -*-
from jdw.data.DataAPI.ddb.fetch_engine import FetchEngine
# -*- coding: utf-8 -*-
import yaml, os
from jdw.data.DataAPI.ddb.ddb_factory import *
from jdw.data.DataAPI.ddb.utilities import to_format, convert_date


class Customized(object):

    def __init__(self):
        self._engine = CustomizeFactory(FetchEngine.create_engine(name='ch'))
        self._yaml = None
        yaml_path = None if 'CHYAML_PATH' not in os.environ else os.environ[
            'CHYAML_PATH']
        if yaml_path is not None:
            with open(yaml_path, 'r') as file:
                self._yaml = yaml.safe_load(file)

    def sequence(self,
                 table_name,
                 columns,
                 begin_date,
                 end_date,
                 format_data=0,
                 inc_update=None):
        if table_name not in self._yaml and inc_update is None:
            raise ValueError("not inc_update")

        clause_list = []
        inc_update = self._yaml[table_name]['IncUpdate']
        if begin_date is not None:
            clause_list1 = to_format(inc_update, '>=',
                                     convert_date(begin_date))
            clause_list.append(clause_list1)
        if end_date is not None:
            clause_list2 = to_format(inc_update, '<=', convert_date(end_date))
            clause_list.append(clause_list2)
        clause_list = clause_list if len(clause_list) > 0 else None
        dt = self._engine.custom(table=table_name,
                                 columns=columns,
                                 clause_list=clause_list,
                                 format_data=format_data)
        return dt


def cusomize_sequence(table_name,
                      columns=None,
                      begin_date=None,
                      end_date=None,
                      format_data=0,
                      inc_update=None):
    return Customized().sequence(table_name=table_name,
                                 columns=columns,
                                 begin_date=begin_date,
                                 end_date=end_date,
                                 format_data=format_data,
                                 inc_update=inc_update)
