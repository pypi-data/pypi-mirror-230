# -*- coding: utf-8 -*-
import pandas as pd
from seleya.data.SurfaceAPI.sqlatom.basic import Basic


class GDReviewsBase(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'gd_reviews_base'
        super(GDReviewsBase, self).__init__(table_name=table_name)

    def fetch(self, begin_date, end_date, cids, columns=None):
        cids = self._transform_list(cids)
        clause_list = [
            self._table_model.cid.in_(cids),
            self._table_model.reviewDateTime.between(begin_date, end_date)
        ]
        return self.customize(clause_list=clause_list, columns=columns)
