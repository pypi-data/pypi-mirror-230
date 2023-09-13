# -*- coding: utf-8 -*-
from seleya.data.SurfaceAPI.sqlatom.basic import Basic


class CompanyEmissionTemperature(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'company_emission_temperature'
        super(CompanyEmissionTemperature, self).__init__(table_name=table_name)

    def fetch(self, codes, columns=None):
        codes = self._transform_list(codes)
        clause_list = [self._table_model.code.in_(codes)]
        return self.customize(clause_list=clause_list, columns=columns)