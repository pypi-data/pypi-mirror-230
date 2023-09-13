# -*- coding: utf-8 -*-
from sqlalchemy.exc import SQLAlchemyError
from pymongo.errors import PyMongoError


class MongoException(PyMongoError, Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)


class SQLException(SQLAlchemyError, Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return str(self.msg)
