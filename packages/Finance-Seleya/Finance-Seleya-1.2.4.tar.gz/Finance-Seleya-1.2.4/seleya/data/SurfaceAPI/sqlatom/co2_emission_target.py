# -*- coding: utf-8 -*-
import pandas as pd
from seleya.data.SurfaceAPI.sqlatom.basic import Basic


class CO2EmissionTarget(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'co2_emission_target'
        super(CO2EmissionTarget, self).__init__(table_name=table_name)

    def fetch(self, codes, begin_date, end_date, columns):
        codes = self._transform_list(codes)
        clause_list = [
            self._table_model.code.in_(codes),
            self._table_model.date.between(begin_date, end_date)
        ]
        return self.customize(clause_list=clause_list, columns=columns)
