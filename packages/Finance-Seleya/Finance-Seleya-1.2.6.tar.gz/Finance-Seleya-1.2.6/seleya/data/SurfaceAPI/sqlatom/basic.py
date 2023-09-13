# -*- coding: utf-8 -*-
import pdb
import pandas as pd
from seleya.data.SurfaceAPI.sqlatom.engine import FetchKDEngine


class Basic(object):

    def __init__(self, table_name=None):
        self._engine = FetchKDEngine()
        self._table_name = table_name if table_name is not None else self._deafault_table_name
        self._table_model = self._engine.table_model(self._table_name)

    def _transform_list(self, params):
        if isinstance(params, str):
            return [params]
        elif isinstance(params, list):
            return params
        elif isinstance(params, int):
            return [params]
        else:
            raise TypeError('industry_code must be str or list')

    def customize(self, clause_list, columns=None):
        return self._engine.customize(table=self._table_model,
                                      clause_list=clause_list,
                                      columns=columns)
