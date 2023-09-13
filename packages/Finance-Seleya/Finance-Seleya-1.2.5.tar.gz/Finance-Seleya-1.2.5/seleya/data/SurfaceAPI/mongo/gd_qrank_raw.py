# -*- coding: utf-8 -*-
import pandas as pd
from seleya.data.SurfaceAPI.mongo.basic import Basic


class GDQrankRaw(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'gd_qrank_raw'
        super(GDQrankRaw, self).__init__(table_name=table_name)

    def fetch(self, columns=None, **kwargs):
        query = {}
        if 'codes' in kwargs:
            query['code'] = {'$in': kwargs['codes']}
        if 'begin_date' in kwargs and 'end_date' in kwargs:
            query['date'] = {
                '$gte': kwargs['begin_date'],
                '$lte': kwargs['end_date']
            }
        if 'industry_code' in kwargs:
            query['industry'] = kwargs['industry_code']

        return self.customize(query=query, columns=columns)

    def fetch_industy_range(self,
                            industry_code,
                            begin_date,
                            end_date,
                            columns=None):
        return self.fetch(industry_code=industry_code,
                          begin_date=begin_date,
                          end_date=end_date,
                          columns=columns)
