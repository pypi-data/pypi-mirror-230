# -*- coding: utf-8 -*-
import pdb
import pandas as pd
from seleya.data.SurfaceAPI.sqlatom.basic import Basic


class Industry(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'industry'
        super(Industry, self).__init__(table_name=table_name)

    def fetch_sector(self,
                     sector_code,
                     industry='SICS',
                     is_primary=1,
                     columns=None):
        sector_code = self._transform_list(sector_code)
        industry = self._transform_list(industry)
        is_primary = self._transform_list(is_primary)
        clause_list = [
            self._table_model.sector_id.in_(sector_code),
            self._table_model.industry.in_(industry),
            self._table_model.is_primary.in_(is_primary),
        ]
        return self.customize(clause_list=clause_list, columns=columns)

    def unique_industry(self, industry='SICS', is_primary=1):
        industry = self._transform_list(industry)
        is_primary = self._transform_list(is_primary)
        clause_list = [
            self._table_model.is_primary.in_(is_primary),
            self._table_model.industry.in_(industry)
        ]
        return self.customize(clause_list=clause_list,
                              columns=['industry_id1'])

    def extract(self, codes, industry='SICS', is_primary=1, columns=None):
        codes = self._transform_list(codes)
        industry = self._transform_list(industry)
        is_primary = self._transform_list(is_primary)
        clause_list = [
            self._table_model.code.in_(codes),
            self._table_model.industry.in_(industry),
            self._table_model.is_primary.in_(is_primary),
        ]
        return self.customize(clause_list=clause_list, columns=columns)

    def fetch(self,
              industry_code,
              industry='SICS',
              is_primary=1,
              columns=None):
        industry_code = self._transform_list(industry_code)
        industry = self._transform_list(industry)
        is_primary = self._transform_list(is_primary)
        clause_list = [
            self._table_model.industry_id1.in_(industry_code),
            self._table_model.industry.in_(industry),
            self._table_model.is_primary.in_(is_primary),
        ]
        return self.customize(clause_list=clause_list, columns=columns)
