# -*- coding: utf-8 -*-
import six, os, itertools, pdb
from seleya.utilities.exceptions import MongoException
from seleya.utilities.kd_logger import kd_logger
from seleya.utilities.singleton import Singleton
from seleya.data.DataAPI.mongo.fetch_engine import FetchEngine


@six.add_metaclass(Singleton)
class FetchKDEngine(FetchEngine):

    def __init__(self, name=None, uri=None):
        if uri is None and name is None:
            super(FetchKDEngine, self).__init__(os.environ['SYL_MG'])
        else:
            super(FetchKDEngine, self).__init__(uri)

    def customize(self, table_name, query, columns=None):
        indices = self.show_indexs(table_name)
        for clause in query.keys():
            if clause not in indices:
                raise MongoException("{0} not indices".format(clause))

        cols = columns if columns is None else dict(
            zip(columns, [1 for i in range(0, len(columns))]))
        return self._engine[self._collection][table_name].find(query, cols)

    def show_indexs(self, table_name):
        list_indices = self._engine[
            self._collection][table_name].list_indexes()
        indices = [
            index['key'].__dict__['_SON__keys'] for index in list_indices
            if 'key' in index
        ]
        return list(set(itertools.chain.from_iterable(indices)))

    def automap(self, table_name):
        return [
            col for col in self._engine[self._collection]
            [table_name].find_one().keys()
            if col not in ['timestamp', 'flag', '_id', 'code']
        ]

    def _filter_columns(self, result):
        if result is not None and not result.empty:
            result = result.drop(['_id'],
                                 axis=1) if '_id' in result.columns else result
            result = result.drop(
                ['flag'], axis=1) if 'flag' in result.columns else result
            result = result.drop(
                ['timestamp'],
                axis=1) if 'timestamp' in result.columns else result
        return result