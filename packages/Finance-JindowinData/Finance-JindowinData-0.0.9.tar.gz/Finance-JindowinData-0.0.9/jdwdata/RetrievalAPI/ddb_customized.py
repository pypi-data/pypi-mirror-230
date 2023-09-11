# -*- coding: utf-8 -*-
import yaml, os
from jdwdata.DataAPI.ddb.fetch_engine import FetchEngine
from jdwdata.DataAPI.ddb.ddb_factory import *
from jdwdata.DataAPI.ddb.utilities import to_format, convert_date
from jdwdata.config.export_cfg import ExportCfg
from jdwdata.config.mapping_cfg import MappingCfg


class DDBCustomized(object):

    def __init__(self):
        self._engine = CustomizeFactory(FetchEngine.create_engine(name='ch'))
        self._export_cfg = ExportCfg()
        self._mapping_cfg = MappingCfg()

    def allign_data(self,
                    data,
                    table_name,
                    begin_date=None,
                    end_date=None,
                    codes=None):
        if codes is None:
            data = self._engine.allign_data(data=data,
                                        table_name=table_name,
                                        begin_date=begin_date,
                                        end_date=end_date,
                                        codes=None)
        return data

    def add_def_cols(self, columns, table_name):
        transepose_indexs, transepose_cols = self._export_cfg.get_transpose_conf(
            table_name)
        columns = transepose_indexs + transepose_cols + columns
        cols = []
        for col in columns:
            if col not in cols:
                cols.append(col)
        return cols

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

        if format_data == 0:
            transepose_indexs, transepose_cols = self._export_cfg.get_transpose_conf(
                table_name)
            if len(transepose_indexs) > 0:
                if transepose_indexs[0] not in dt.columns:
                    dt.reset_index(inplace=True)

        if format_data == 1:
            for key in dt.keys():
                dt[key] = self.allign_data(dt[key], table_name, begin_date,
                                           end_date)
        return dt

    def sequence_by_map(self,
                        mapping: dict,
                        columns: list,
                        codes=None,
                        begin_date=None,
                        end_date=None):
        tmp_mapping = self._mapping_cfg.get_mapping_by_cols(columns, mapping)
        dt = self._engine.custom_by_map(mapping=tmp_mapping,
                                        columns=columns,
                                        codes=codes,
                                        begin_date=begin_date,
                                        end_date=end_date)

        for col in columns:
            transepose_indexs, transepose_cols = self._export_cfg.get_transpose_conf(
                tmp_mapping[col]['table'])
            if len(transepose_indexs) > 0 and len(transepose_cols) > 0:
                tmp = dt[col]
                if tmp is not None and transepose_indexs[0] in tmp.columns:
                    tmp.set_index(transepose_indexs + transepose_cols,
                                  inplace=True)
                    dt[col] = tmp
            elif len(transepose_indexs) > 0 and len(transepose_cols) == 0:
                tmp = dt[col]
                if tmp is not None and transepose_indexs[0] not in tmp.columns:
                    tmp.reset_index(inplace=True)
                    dt[col] = tmp
        return dt

    def sequence_factor_data(self,
                             begin_date=None,
                             end_date=None,
                             ids=None,
                             freq='D',
                             format_data=0,
                             **kwargs):
        table = self._mapping_cfg.get_factor_table(freq)
        columns = []
        mapping = {}
        if isinstance(ids,list):
            for i in ids:
                mapping[i] = {'table': table,
                                'column': 'value',
                                'cond': {'id': i}
                                }
                columns.append(i)
        else:
            mapping[ids] = {'table': table,
                            'column': 'value',
                            'cond': {'id': ids}
                            }

            columns.append(ids)
        data = self.sequence_by_map(columns=columns,
                                   codes=None,
                                   begin_date=begin_date,
                                   end_date=end_date,
                                   mapping=mapping)

        rtn = None
        if data is not None:
            for id in data.keys():
                df = data[id]
                if df is not None:
                    if freq not in ['D', 'min']:
                        df = df.resample(freq).last()
                        data[id] = df
                    if format_data == 0:
                        l = list(df.columns)
                        df.reset_index(inplace=True)
                        df = pd.melt(data[id], id_vars='trade_date', value_vars=l, value_name=id)
                        if rtn is None:
                            rtn = df
                        else:
                            rtn = pd.merge(rtn,df,how='left',on=['trade_date','code'])
        if format_data == 0:
            return rtn
        return data

    def sequence_factor_info(self,
                        category=None,
                        freq=None,
                        begin_date=None,
                        universe=None,
                        **kwargs):
        table = self._mapping_cfg.get_table_by_alias('factorinfo')
        if table is None:
            ValueError("factorinfo not in table_alias!")

        mapping = {'factor_info': {'table': table,
                                   'cond': {'status': 1}
                                   }
                   }
        if category is not None:
            mapping['factor_info']['cond']['category'] = category
        if freq is not None:
            mapping['factor_info']['cond']['freq'] = freq
        if universe is not None:
            mapping['factor_info']['cond']['universe'] = universe

        if begin_date is None:
            import datetime as dt
            begin_date = dt.datetime.now().strftime('%Y-%m-%d')

        factor_info = self.sequence_by_map(columns=['factor_info'],
                                          codes=None,
                                          begin_date='1990-01-01',
                                          end_date=begin_date,
                                          mapping=mapping)
        return factor_info.get('factor_info', None)


def cusomize_sequence(table_name,
                      columns=None,
                      begin_date=None,
                      end_date=None,
                      format_data=0,
                      inc_update=None):
    return DDBCustomized().sequence(table_name=table_name,
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
    return DDBCustomized().sequence_by_map(mapping=mapping,
                                           columns=columns,
                                           codes=codes,
                                           begin_date=begin_date,
                                           end_date=end_date)

def get_factors(begin_date=None,
                end_date=None,
                ids=None,
                freq='D',
                format_data=0,
                **kwargs):
    return DDBCustomized().sequence_factor_data(begin_date=begin_date,
                                    end_date=end_date,
                                    ids=ids,
                                    freq=freq,
                                    format_data=format_data,
                                    kwargs=kwargs)
def get_factor_info(category=None,
                freq=None,
                begin_date=None,
                universe=None,
                **kwargs):
    return DDBCustomized().sequence_factor_info(category=category,
                                           freq=freq,
                                           begin_date=begin_date,
                                           universe=universe,
                                           kwargs=kwargs)