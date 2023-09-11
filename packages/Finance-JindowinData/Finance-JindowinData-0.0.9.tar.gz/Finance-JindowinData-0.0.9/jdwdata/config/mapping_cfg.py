# -*- coding: utf-8 -*-

import yaml
import os, six
from jdwdata.kdutils.singleton import *


@six.add_metaclass(Singleton)
class MappingCfg(object):

    def __init__(self):
        self.mapping_cfg = {}
        if 'MAPPING_CFG_PATH' in os.environ.keys():
            with open(os.environ['MAPPING_CFG_PATH'], 'r',
                      encoding='utf8') as y:
                self.mapping_cfg = yaml.safe_load(y)
    def gen_wide_table_map(self,tb, col, strs, dep_tbalis_cfg):
        tmp_map = {}
        tmp_map['table'] = dep_tbalis_cfg[tb]
        # tmp_map['column'] = strs[1]
        if len(strs) >= 3:
            if 'pnq' in strs[-1]:
                try:
                    tmp_map['cond'] = {'PNQ': int(strs[-1].replace('pnq', ''))}
                except:
                    pass
            if 'cond' in tmp_map and 'PNQ' in tmp_map['cond']:
                tmp_map['column'] = col.replace(strs[0] + "_", '').replace("_" + strs[-1], '')
            else:
                tmp_map['column'] = col.replace(strs[0] + "_", '')
        else:
            tmp_map['column'] = col.replace(strs[0] + "_", '')
        return tmp_map

    def gen_dep_table_map(self, tb, col, strs, tbalis_cfg):
        tmp_map = {}
        tmp_map['table'] = tbalis_cfg[tb]
        tmp_map['cond'] = {'name': col.replace(strs[0] + "_", '')}
        tmp_map['column'] = 'value'
        return tmp_map

    def get_mapping_by_cols(self, cols, mapping):
        tbalis_cfg = self.mapping_cfg['table_alias'].copy()
        dep_tbalis_cfg = self.mapping_cfg['table_alias_dep'].copy()
        colalis_cfg = self.mapping_cfg['column_alias'].copy()

        if isinstance(mapping, dict) and len(mapping) > 0:
            colalis_cfg.update(mapping)
        data_dict = {}
        for col in cols:
            if col in colalis_cfg:
                data_dict[col] = colalis_cfg[col]
            else:
                strs = col.split('_')
                if len(strs) == 1:
                    raise ValueError(
                        " no table configured in table_alias, column alias:" +
                        col)
                tb = strs[0]
                if tb in tbalis_cfg:
                    data_dict[col] = self.gen_wide_table_map(tb, col,strs, tbalis_cfg)
                elif tb in dep_tbalis_cfg:
                    data_dict[col] = self.gen_dep_table_map(tb, col,strs, dep_tbalis_cfg)
                else:
                    raise ValueError(tb + " not in table_alias, column alias:" + col)

        return data_dict

    def get_factor_table(self,freq):
        table = 'stk_xyfactor_daily'
        if freq.startswith('D') or freq.startswith('M'):
            table = self.mapping_cfg['factor_freq_map'].get('D','stk_xyfactor_daily')

        if freq.startswith('min'):
            table = self.mapping_cfg['factor_freq_map'].get('min','stk_xyfactor_min')

        return table

    def get_table_by_alias(self,alias):
        tbalis_cfg = self.mapping_cfg['table_alias'].copy()
        return tbalis_cfg.get(alias, None)


