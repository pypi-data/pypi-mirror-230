# -*- coding: utf-8 -*-
import re, pdb
import pandas as pd
import os, traceback
import yaml
from jdwdata.config.export_cfg import ExportCfg
from jdwdata.DataAPI.ddb.utilities import *


class FileEngine(object):

    def __init__(self, url):
        self._file_url = url

    def file_engine(self):
        return self

    def get_base_url(self):
        return self._file_url


class FetchEngine(object):

    def __init__(self, name, url):
        self._name = name
        self._engine = FileEngine(url=url)
        self.base_dir = self._engine.get_base_url()
        self.exportCfg = ExportCfg()

    @classmethod
    def create_engine(cls, name):
        if name == 'fl':
            from .fl import fl_engine
            return fl_engine.__getattribute__('FetchFLEngine')
        else:
            ValueError("name:{0} is error".format(name))

    def extract_date_clause(self, clause, trans_indexs, begin_date, end_date):
        if '>=' in clause:
            begin_date = self.get_clause_date(clause, '>=', trans_indexs)
        elif '>' in clause:
            begin_date = self.get_clause_date(clause, '>', trans_indexs)
        elif '<=' in clause:
            end_date = self.get_clause_date(clause, '<=', trans_indexs)
        elif '<' in clause:
            end_date = self.get_clause_date(clause, '<', trans_indexs)
        elif '=' in clause:
            begin_date = self.get_clause_date(clause, '<', trans_indexs)
            end_date = begin_date
        elif '==' in clause:
            begin_date = self.get_clause_date(clause, '<', trans_indexs)
            end_date = begin_date

        return begin_date, end_date

    def extract_subfolder_clause(self, clause, subfolder):
        if '=' in clause:
            tmpstrs = clause.split('=')
            col = tmpstrs[0].replace(' ', '')
            if col == subfolder:
                sub_folder_name = col + '_' + tmpstrs[1].replace(' ', '')
                return sub_folder_name
        return subfolder

    def extract_subfolder_cond(self, cond, subfolder):
        if isinstance(cond, dict) and subfolder in cond.keys():
            sub_folder_name = subfolder + '_' + str(cond[subfolder]).replace(
                ' ', '')
            return sub_folder_name
        return subfolder

    def get_template(self):
        df = pd.read_feather(os.path.join(self.base_dir, 'template.fea'))
        return df

    def get_all_codes(self):
        df = pd.read_feather(os.path.join(self.base_dir, 'template.fea'))
        all_codes = list(df.columns)
        all_codes.remove('index')
        return all_codes

    def get_clause_date(self, caluse, symbol, trans_indexs):
        if symbol in caluse:
            tmpstrs = caluse.split(symbol)
            col = tmpstrs[0].replace(' ', '')
            if (isinstance(trans_indexs, list)
                    and col in trans_indexs) or (isinstance(trans_indexs, str)
                                                 and col == trans_indexs):
                return deconvert_date(tmpstrs[1].replace(' ', ''))
        else:
            return None

    def custom_by_map(self,
                      factor_name,
                      mapping,
                      codes=None,
                      start_date=None,
                      end_date=None):
        params = mapping[factor_name]
        table_name = params['table']
        col = params.get('column', '')
        cond = params.get('cond', None)

        table_cfg = self.exportCfg.get_table_cfg(table_name)
        if table_cfg is None:
            print(table_name + ' not configured!')
            return
        elif table_cfg.get('IsWideTable',1) == 0:
            col = cond.get('name','')
        elif 'Path' not in table_cfg.keys():
            print(table_name + ' no fea file!')
            return
        if 'SubFolder' in table_cfg.keys():
            file = self.exportCfg.make_filename(
                self.base_dir, table_name, col,
                self.extract_subfolder_cond(cond, table_cfg['SubFolder']))
        else:
            file = self.exportCfg.make_filename(self.base_dir, table_name, col)
        df = pd.read_feather(file)
        df = self.exportCfg.handle_date_filter(df, end_date, start_date,
                                               table_cfg)
        df = self.exportCfg.handle_allignment(table_name, start_date, end_date,
                                              codes, df, self.get_all_codes())
        df = self.exportCfg.handle_map_cond(df, table_name, cond)
        df = self.exportCfg.handle_codes(df, table_name, codes)
        if 'flag' in df.columns:
            del df['flag']
        return df

    def custom(self, table, clause_list, columns):
        begin_date = None
        end_date = None
        data = {}
        trans_indexs, trans_cols = self.exportCfg.get_transpose_conf(table)
        sub_folder = self.exportCfg.get_subfolder_conf(table)
        sub_folder_name = sub_folder
        if clause_list is not None:
            if isinstance(clause_list, list):
                for clause in clause_list:
                    if 'date' in clause.lower() or 'time' in clause.lower():
                        begin_date, end_date = self.extract_date_clause(
                            clause, trans_indexs, begin_date, end_date)
                    elif sub_folder in clause:
                        sub_folder_name = self.extract_subfolder_clause(
                            clause, sub_folder)
            elif isinstance(clause_list, str):
                if 'date' in clause_list.lower(
                ) or 'time' in clause_list.lower():
                    begin_date, end_date = self.extract_date_clause(
                        clause_list, trans_indexs, begin_date, end_date)
                elif sub_folder in clause_list:
                    sub_folder_name = self.extract_subfolder_clause(
                        clause_list, sub_folder)
        for col in columns:
            if col in trans_indexs:
                continue
            if col in trans_cols:
                continue
            df = self.get_file(table,
                               col,
                               start_date=begin_date,
                               end_date=end_date,
                               sub_folder=sub_folder_name)
            data[col] = df
        return data

    def get_file(self,
                 table_name,
                 col,
                 start_date=None,
                 end_date=None,
                 sub_folder=''):
        table_cfg = self.exportCfg.get_table_cfg(table_name)
        if table_cfg is None:
            print(table_name + ' not configured!')
            return
        elif 'Path' not in table_cfg.keys():
            print(table_name + ' no fea file!')
            return

        if table_cfg is not None and 'SubFolder' in table_cfg.keys():
            file = self.exportCfg.make_filename(self.base_dir, table_name, col,
                                                sub_folder)
        else:
            file = self.exportCfg.make_filename(self.base_dir, table_name, col)
        df = pd.read_feather(file)
        df = self.exportCfg.handle_date_filter(df, end_date, start_date,
                                               table_cfg)
        df = self.exportCfg.handle_allignment(table_name, start_date, end_date,
                                              None, df, self.get_all_codes())
        if 'flag' in df.columns:
            del df['flag']
        return df
