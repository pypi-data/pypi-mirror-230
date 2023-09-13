# -*- coding: utf-8 -*-
import pdb
import pandas as pd
from seleya.data.SurfaceAPI.mongo.engine import FetchKDEngine


class Basic(object):

    def __init__(self, table_name):
        self._engine = FetchKDEngine()
        self._table_name = table_name if table_name is not None else self._deafault_table_name

    def customize(self, query, columns=None):
        results = self._engine.customize(table_name=self._table_name,
                                         query=query,
                                         columns=columns)
        results = pd.DataFrame(results)
        return self._engine._filter_columns(results)
