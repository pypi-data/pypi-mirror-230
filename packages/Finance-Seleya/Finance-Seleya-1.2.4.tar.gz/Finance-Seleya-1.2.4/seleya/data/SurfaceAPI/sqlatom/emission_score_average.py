# -*- coding: utf-8 -*-
from seleya.data.SurfaceAPI.sqlatom.basic import Basic


class EmissionScoreAverage(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'emission_score_average'
        super(EmissionScoreAverage, self).__init__(table_name=table_name)

    def fetch(self, industry, columns=None):
        industry = self._transform_list(industry)
        clause_list = [self._table_model.industry.in_(industry)]
        return self.customize(clause_list=clause_list, columns=columns)