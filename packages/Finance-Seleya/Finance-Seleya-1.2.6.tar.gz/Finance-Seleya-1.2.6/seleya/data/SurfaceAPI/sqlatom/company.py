# -*- coding: utf-8 -*-
from seleya.data.SurfaceAPI.sqlatom.basic import Basic


class Company(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'company'
        super(Company, self).__init__(table_name=table_name)

    def fetch(self, codes, columns=None):
        codes = self._transform_list(codes)
        clause_list = [
            self._table_model.code.in_(codes),
            self._table_model.is_primary == 1
        ]
        return self.customize(clause_list=clause_list, columns=columns)