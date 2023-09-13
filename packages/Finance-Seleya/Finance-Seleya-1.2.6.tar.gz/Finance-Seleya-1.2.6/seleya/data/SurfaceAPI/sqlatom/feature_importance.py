# -*- coding: utf-8 -*-
from seleya.data.SurfaceAPI.sqlatom.basic import Basic


class FeatureImportance(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'feature_importance'
        super(FeatureImportance, self).__init__(table_name=table_name)

    def fetch_factor(self, columns=None):
        clause_list = [self._table_model.is_contro == False]
        return self.customize(clause_list=clause_list, columns=columns)

    def fetch_factor_range(self, region, sector_id, columns=None):
        region = self._transform_list(region)
        sector_id = self._transform_list(sector_id)
        clause_list = [
            self._table_model.region.in_(region),
            self._table_model.sector_id.in_(sector_id)
        ]
        return self.customize(clause_list=clause_list, columns=columns)
