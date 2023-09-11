from jdwdata.RetrievalAPI.ddb_customized import cusomize_sequence as get_ddb_data
from jdwdata.RetrievalAPI.ddb_customized import cusomize_sequence_by_map as get_ddb_data_by_map
from jdwdata.RetrievalAPI.file_customized import cusomize_sequence as get_file_data
from jdwdata.RetrievalAPI.file_customized import cusomize_sequence_by_map as get_file_data_by_map
from jdwdata.RetrievalAPI.ddb_customized import get_factors, get_factor_info


def get_data(table_name,
             columns=None,
             begin_date=None,
             end_date=None,
             format_data=0,
             inc_update=None,
             method='ddb'):
    if method == 'ddb':
        return get_ddb_data(table_name=table_name,
                            columns=columns,
                            begin_date=begin_date,
                            end_date=end_date,
                            format_data=format_data,
                            inc_update=inc_update)
    elif method == 'file':
        return get_file_data(table_name=table_name,
                             columns=columns,
                             begin_date=begin_date,
                             end_date=end_date,
                             format_data=format_data,
                             inc_update=inc_update)
    else:
        raise ValueError("method is error")


def get_data_by_map(columns: list,
                    codes=None,
                    begin_date=None,
                    end_date=None,
                    mapping: dict = {},
                    method='ddb',
                    **kwargs):
    if method == 'ddb':
        return get_ddb_data_by_map(columns=columns,
                                   codes=codes,
                                   begin_date=begin_date,
                                   end_date=end_date,
                                   mapping=mapping,
                                   **kwargs)
    elif method == 'file':
        return get_file_data_by_map(columns=columns,
                                    codes=codes,
                                    begin_date=begin_date,
                                    end_date=end_date,
                                    mapping=mapping,
                                    **kwargs)
    else:
        raise ValueError("method is error")

