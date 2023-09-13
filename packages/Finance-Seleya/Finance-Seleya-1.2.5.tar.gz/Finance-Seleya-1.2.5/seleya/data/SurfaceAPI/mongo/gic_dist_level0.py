# -*- coding: utf-8 -*-
import pandas as pd
from seleya.data.SurfaceAPI.mongo.basic import Basic


class GicDistLevel0(Basic):

    def __init__(self, table_name=None):
        self._deafault_table_name = 'gic_dist_level0'
        super(GicDistLevel0, self).__init__(table_name=table_name)

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

        if 'type' in kwargs:
            query['type'] = {'$in': kwargs['type']}

        if 'name' in kwargs:
            query['name'] = {'$in': kwargs['name']}
        return self.customize(query=query, columns=columns)