# -*- coding: utf-8 -*-
import pdb
import pandas as pd
from seleya.data.SurfaceAPI.sqlatom.basic import Basic


class SASBMapdom(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'sasb_mapdom'
        super(SASBMapdom, self).__init__(table_name=table_name)

    def fetch_sector(self,
              sector_code,
              columns=['column_name', 'trcode']):
        sector_code = self._transform_list(sector_code)
        flag = self._transform_list(1)
        clause_list = [
            self._table_model.sector.in_(sector_code),
            self._table_model.flag.in_(flag),
        ]
        return self.customize(clause_list=clause_list, columns=columns)
