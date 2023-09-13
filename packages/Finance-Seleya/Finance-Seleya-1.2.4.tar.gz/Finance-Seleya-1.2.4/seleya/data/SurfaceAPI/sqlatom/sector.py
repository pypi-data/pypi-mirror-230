# -*- coding: utf-8 -*-
import pdb
import pandas as pd
from seleya.data.SurfaceAPI.sqlatom.basic import Basic


class Sector(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'industry'
        super(Sector, self).__init__(table_name=table_name)

    def fetch(self, sector_code, industry='SICS', is_primary=1, columns=None):
        sector_code = self._transform_list(sector_code)
        industry = self._transform_list(industry)
        is_primary = self._transform_list(is_primary)
        flag = self._transform_list(1)
        clause_list = [
            self._table_model.sector_id.in_(sector_code),
            self._table_model.industry.in_(industry),
            self._table_model.is_primary.in_(is_primary)
        ]
        return self.customize(clause_list=clause_list, columns=columns)
