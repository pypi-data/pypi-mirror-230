# -*- coding: utf-8 -*-
import pandas as pd
import pdb

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


class CustomizeFactory(EngineFactory):
    def allign_data(self, data, table_name, begin_date=None, end_date=None, codes=None):
        return self._fetch_engine.exportCfg.handle_allignment(table_name, begin_date, end_date, codes, data, self._fetch_engine.get_all_codes())

    def del_flag(self, data):
        if data is not None and 'flag' in data.columns:
            del data['flag']
        return data

    def custom(self, clause_list, table, columns=None, format_data=0):
        data = self._fetch_engine.custom(table=table,
                                         clause_list=clause_list,
                                         columns=columns)
        if format_data == 1 and 'trade_date' in data.columns and 'code' in data.columns:
            data['trade_date'] = pd.to_datetime(data['trade_date'])
            if is_ultron:
                dates = bizDatesList('china.sse', data.trade_date.min(),
                                 data.trade_date.max())
            else:    
                dates = []

            data.set_index('trade_date', inplace=True)
            codes = data['code'].unique()
            res = {}
            cols = [
                col for col in columns if col not in ['trade_date', 'code']
            ]
            for col in cols:
                piot_dt = data.copy().pivot(columns='code', values=col)
                if len(dates) > 0:
                    piot_dt = piot_dt.reindex(dates)
                piot_dt = piot_dt.reindex(columns=codes)
                res[col] = piot_dt
            return res
        return data if 'flag' not in data.columns else data.drop(['flag'],axis=1)

    def custom_by_map(self, mapping: dict, columns: list, codes=None, begin_date=None, end_date=None):
        data_dict = {}
        for col in columns:
            df = self._fetch_engine.custom_by_map(col, mapping, codes, begin_date, end_date)
            data_dict[col] = self.del_flag(df)
        return data_dict


def cusomize_api(name='ch', url=None):
    from jdwdata.DataAPI.ddb.fetch_engine import FetchEngine
    CustomizeAPI = CustomizeFactory(FetchEngine.create_engine(name), url=url)
    return CustomizeAPI