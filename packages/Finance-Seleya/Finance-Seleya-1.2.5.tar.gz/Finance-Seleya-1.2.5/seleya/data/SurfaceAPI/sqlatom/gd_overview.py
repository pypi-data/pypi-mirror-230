# -*- coding: utf-8 -*-
import pandas as pd
from seleya.data.SurfaceAPI.sqlatom.basic import Basic


class GDOveriew(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'gd_overview'
        super(GDOveriew, self).__init__(table_name=table_name)

    def fetch(self, codes, columns=None):
        codes = self._transform_list(codes)
        clause_list = [self._table_model.code.in_(codes)]
        return self.customize(clause_list=clause_list, columns=columns)
