# -*- coding: utf-8 -*-
import yaml, os
from jdwdata.DataAPI.file.fetch_engine import FetchEngine
from jdwdata.DataAPI.file.file_factory import *
from jdwdata.DataAPI.ddb.utilities import to_format, convert_date
from jdwdata.config.export_cfg import ExportCfg
from jdwdata.config.mapping_cfg import MappingCfg


class FileCustomized(object):

    def __init__(self):
        self._engine = CustomizeFactory(FetchEngine.create_engine(name='fl'))
        self._export_cfg = ExportCfg()
        self._mapping_cfg = MappingCfg()

    def add_def_cols(self, columns, table_name):
        transepose_indexs, transepose_cols = self._export_cfg.get_transpose_conf(
            table_name)
        columns = columns + transepose_indexs + transepose_cols
        columns = list(set(columns))
        return columns

    def sequence(self,
                 table_name,
                 columns,
                 begin_date,
                 end_date,
                 format_data=0,
                 inc_update=None):
        tb_cfg = self._export_cfg.get_table_cfg(table_name)
        if tb_cfg is None and inc_update is None:
            raise ValueError("not inc_update")

        clause_list = []
        inc_update = tb_cfg['IncUpdate']
        if begin_date is not None:
            clause_list1 = to_format(inc_update, '>=',
                                     convert_date(begin_date))
            clause_list.append(clause_list1)
        if end_date is not None:
            clause_list2 = to_format(inc_update, '<=', convert_date(end_date))
            clause_list.append(clause_list2)
        clause_list = clause_list if len(clause_list) > 0 else None
        dt = self._engine.custom(table=table_name,
                                 columns=self.add_def_cols(
                                     columns, table_name),
                                 clause_list=clause_list,
                                 format_data=format_data)
        return dt

    def sequence_by_map(self,
                        mapping: dict,
                        columns: list,
                        codes=None,
                        begin_date=None,
                        end_date=None,
                        **kwargs):
        tmp_mapping = self._mapping_cfg.get_mapping_by_cols(columns, mapping)
        return self._engine.custom_by_map(tmp_mapping, columns, codes,
                                          begin_date, end_date)


def cusomize_sequence(table_name,
                      columns,
                      begin_date=None,
                      end_date=None,
                      format_data=0,
                      inc_update=None):
    return FileCustomized().sequence(table_name=table_name,
                                     columns=columns,
                                     begin_date=begin_date,
                                     end_date=end_date,
                                     format_data=format_data,
                                     inc_update=inc_update)


def cusomize_sequence_by_map(columns: list,
                             codes=None,
                             begin_date=None,
                             end_date=None,
                             mapping: dict = {},
                             **kwargs):
    return FileCustomized().sequence_by_map(mapping=mapping,
                                            columns=columns,
                                            codes=codes,
                                            begin_date=begin_date,
                                            end_date=end_date,
                                            kwargs=kwargs)
