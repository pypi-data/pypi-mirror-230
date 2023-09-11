# -*- coding: utf-8 -*-

import yaml
import os, traceback, six
from jdwdate.api import *
import pandas as pd
import datetime as dt
from jdwdata.kdutils.singleton import *


@six.add_metaclass(Singleton)
class ExportCfg(object):

    def __init__(self):
        self.export_cfg = {}
        if 'EXPORT_CFG_PATH' in os.environ.keys():
            with open(os.environ['EXPORT_CFG_PATH'], 'r',
                      encoding='utf8') as y:
                self.export_cfg = yaml.safe_load(y)
        self.index_codes = ['000905', '000016', '000852', '000300']

    def get_table_cfg(self, table):
        return self.export_cfg.get(table, None)

    def get_index_align_codes(self):
        return self.index_codes

    def get_transpose_conf(self, table_name):
        transepose_indexs = []
        transepose_cols = []
        if table_name in self.export_cfg.keys(
        ) and self.export_cfg[table_name] is not None:
            if 'Transpose' in self.export_cfg[table_name].keys(
            ) and self.export_cfg[table_name]['Transpose'] is not None:
                trans_index = self.export_cfg[table_name]['Transpose']['Index']
                if isinstance(trans_index, str):
                    transepose_indexs.append(trans_index)
                else:
                    transepose_indexs = trans_index

                tran_col = self.export_cfg[table_name]['Transpose'].get(
                    'Columns', None)
                if tran_col is not None:
                    if isinstance(tran_col, str):
                        transepose_cols.append(tran_col)
                    else:
                        transepose_cols = tran_col
        return transepose_indexs, transepose_cols

    def get_subfolder_conf(self, table_name):
        if table_name in self.export_cfg.keys(
        ) and self.export_cfg[table_name] is not None:
            if 'SubFolder' in self.export_cfg[table_name].keys(
            ) and self.export_cfg[table_name]['SubFolder'] is not None:
                return self.export_cfg[table_name]['SubFolder']
        return ''

    def make_filename(self, base_dir, table, col_name='', sub_folder=''):
        if sub_folder != '':
            dir_name = os.path.join(base_dir, self.export_cfg[table]['Path'].replace('\\','/'),
                                    sub_folder)
        else:
            dir_name = os.path.join(base_dir, self.export_cfg[table]['Path'].replace('\\','/'))

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        if col_name == '':
            name = table.replace('stk_', '')
            return os.path.join(dir_name, name + '.fea')

        return os.path.join(dir_name, col_name + '.fea')

    def handle_map_cond(self, data, table, conds):
        if conds is None:
            return data
        transepose_indexs, transepose_cols = self.get_transpose_conf(table)
        if len(transepose_indexs) > 0:
            if transepose_indexs[0] in data.columns:
                data.set_index(transepose_indexs, inplace=True)
        for key in conds.keys():
            value = conds[key]
            if key in transepose_cols:
                if isinstance(value, str):
                    data = data[[value]]
                elif isinstance(value, list):
                    data = data[value]
            elif key in data.columns:
                data = data[data[key] == value]
        return data

    def handle_codes(self, data, table, codes):
        if codes is None:
            return data
        transepose_indexs, transepose_cols = self.get_transpose_conf(table)
        if len(transepose_indexs) > 0:
            data.set_index(transepose_indexs, inplace=True)

        if 'code' not in data.columns:
            try:
                data = data[codes]
            except:
                print(traceback.format_exc())
        else:
            try:
                data = data[data['code'].isin(codes)]
            except:
                print(traceback.format_exc())

        if len(transepose_indexs) > 0:
            data.reset_index(inplace=True)

        return data

    def handle_date_filter(self, df, end_date, start_date, table_cfg):
        date_type = ''
        if 'IncUpdate' in table_cfg.keys():
            date_type = table_cfg['IncUpdate']
        if date_type != '':
            if start_date is not None:
                df = df[df[date_type] >= pd.to_datetime(start_date)]
            if end_date is not None:
                df = df[df[date_type] <= pd.to_datetime(end_date)]
        return df

    def handle_allignment(self,
                          table,
                          start_date,
                          end_date,
                          codes,
                          data,
                          all_codes=None):
        tranpose_index, trans_cols = self.get_transpose_conf(table)
        if tranpose_index is not None and len(tranpose_index) > 0 and len(
                data) > 0:
            if tranpose_index[0] in data.columns:
                data.set_index(tranpose_index, inplace=True)
            if len(tranpose_index) == 1 and (
                    'date' in tranpose_index[0].lower()
                    or 'time' in tranpose_index[0].lower()):
                if tranpose_index[0] in data.columns:
                    data.set_index(tranpose_index, inplace=True)
                if start_date is not None and end_date is not None:
                    trade_dates = bizDatesList('china.sse', start_date,
                                               end_date)
                    data = data.reindex(index=trade_dates,
                                        columns=data.columns)
                elif start_date is not None:
                    trade_dates = bizDatesList(
                        'china.sse', start_date,
                        dt.datetime.now().strftime('%Y-%m-%d'))
                    data = data.reindex(index=trade_dates, columns=codes)
            if len(trans_cols) == 1 and trans_cols[0] == 'code' and 'code' not in data.columns:
                if codes is None and all_codes is not None:
                    data = data.reindex(index=data.index, columns=all_codes)
                else:
                    data = data.reindex(index=data.index, columns=codes)
            elif len(trans_cols) == 1 and trans_cols[0] == 'indexCode' and 'indexCode' not in data.columns:
                if codes is None:
                    data = data.reindex(index=data.index,
                                        columns=self.index_codes)
                else:
                    data = data.reindex(index=data.index, columns=codes)
        return data

    ##################### from ddb engine######

    def get_slct_cols(self, table_name, col):
        if table_name in self.export_cfg.keys():
            table_cfg = self.export_cfg[table_name]
            select_cols = []
            select_cols.append(col)
            if 'Transpose' in table_cfg.keys():
                if isinstance(table_cfg['Transpose']['Index'], list):
                    select_cols = select_cols + table_cfg['Transpose']['Index']
                else:
                    select_cols.append(table_cfg['Transpose']['Index'])
                if 'Columns' in table_cfg['Transpose'].keys():
                    select_cols.append(table_cfg['Transpose']['Columns'])
            return select_cols
        return None

    def handle_transpose(self, data, col, table):
        table_cfg = self.get_table_cfg(table)
        if table_cfg is not None and len(data) > 0:
            if 'Columns' in table_cfg['Transpose'].keys():
                try:
                    data = data.pivot(
                        columns=table_cfg['Transpose']['Columns'],
                        index=table_cfg['Transpose']['Index'],
                        values=col)
                except:
                    print()
        return data
