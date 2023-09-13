# -*- coding: utf-8 -*-
from seleya.data.DataAPI.mongo.mongodb import MongoDBManager


class FetchEngine(object):

    def __init__(self, uri):
        self._engine = MongoDBManager(uri)
        self._collection = uri.split('/')[-1]

    def mg_engine(self):
        return self._engine

    def mg_collection(self):
        return self._collection