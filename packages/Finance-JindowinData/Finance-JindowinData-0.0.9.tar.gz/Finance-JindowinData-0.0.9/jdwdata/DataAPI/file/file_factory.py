# -*- coding: utf-8 -*-
import pandas as pd
import os, yaml
from jdwdata.config.export_cfg import ExportCfg

is_ultron = True
try:
    from ultron.tradingday import *
except ImportError:
    is_ultron = False


class EngineFactory():

    def create_engine(self, engine_class, url):
        return engine_class(url=url)

    def __init__(self, engine_class, url=None):
        self._fetch_engine = self.create_engine(engine_class, url=url)
        self._export_cfg = ExportCfg()


class CustomizeFactory(EngineFactory):

    def tranpose_df(self, transepose_cols, transepose_indexs, col, col_data):
        if len(col_data.columns) > 2:
            col_data.reset_index(inplace=True)
            l = list(col_data.columns)
            for col_name in transepose_indexs:
                l.remove(col_name)
            df = pd.melt(col_data, id_vars=transepose_indexs, value_vars=l)
            df.rename(columns={
                'variable': transepose_cols[0],
                'value': col
            },
                      inplace=True)
            return df
        return col_data

    def reset_tranpose(self, table, df):
        transepose_indexs, transepose_cols = self._export_cfg.get_transpose_conf(
            table)
        if len(transepose_indexs) > 0 and len(transepose_cols) == 0:
            df.reset_index(inplace=True)
            return df
        return df

    def del_flag(self, data):
        if data is not None and 'flag' in data.columns:
            del data['flag']
        return data

    def custom(self, clause_list, table, columns, format_data=0):
        data = self._fetch_engine.custom(table=table,
                                         clause_list=clause_list,
                                         columns=columns)
        df = None
        if format_data == 0:
            transepose_indexs, transepose_cols = self._export_cfg.get_transpose_conf(
                table)
            for key in data.keys():
                col_data = data[key]
                if col_data is not None:
                    if df is None:
                        df = self.tranpose_df(transepose_cols,
                                              transepose_indexs, key, col_data)
                    else:
                        tmp = self.tranpose_df(transepose_cols,
                                               transepose_indexs, key,
                                               col_data)
                        df = pd.merge(df,
                                      tmp,
                                      how='left',
                                      on=transepose_cols + transepose_indexs)
            if len(transepose_indexs) > 0:
                if transepose_indexs[0] not in df.columns:
                    df.reset_index(inplace=True)
            return self.del_flag(df)
        return data

    def custom_by_map(self,
                      mapping: dict,
                      columns: list,
                      codes=None,
                      begin_date=None,
                      end_date=None):
        data_dict = {}
        for col in columns:
            df = self._fetch_engine.custom_by_map(col, mapping, codes,
                                                  begin_date, end_date)
            df = self.reset_tranpose(mapping[col]['table'], df)
            data_dict[col] = self.del_flag(df)
        return data_dict


def cusomize_api(name='fl', url=None):
    from jdwdata.DataAPI.file.fetch_engine import FetchEngine
    CustomizeAPI = CustomizeFactory(FetchEngine.create_engine(name), url=url)
    return CustomizeAPI