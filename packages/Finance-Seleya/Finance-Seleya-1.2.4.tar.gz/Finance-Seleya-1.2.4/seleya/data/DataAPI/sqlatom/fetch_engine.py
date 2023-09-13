import importlib, pdb, itertools
import pandas as pd
import sqlalchemy.orm as orm
from sqlalchemy import create_engine, select, and_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.engine import reflection
from seleya.utilities.exceptions import SQLException


class SQLEngine(object):

    def __init__(self, url):
        self._engine = create_engine(url, echo=False)
        self._session = self.create_session()

    def create_session(self):
        db_session = orm.sessionmaker(bind=self._engine)
        return db_session()

    def __del__(self):
        if self._session:
            self._session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            self._session.close()

    def sql_engine(self):
        return self._engine


class FetchEngine(object):

    def __init__(self, name, url):
        self._name = name
        self._engine = SQLEngine(url)
        self._base = automap_base()
        self._base.prepare(self._engine.sql_engine(), reflect=True)
        self._insp = reflection.Inspector.from_engine(
            self._engine.sql_engine())

    @classmethod
    def create_engine(cls, name):
        if name == 'sly':
            from .sly import sly_engine
            return sly_engine.__getattribute__('FetchSLYEngine')

    def name(self, name):
        return None if name not in self._base.classes else self._base.classes[
            name]

    def show_indexs(self, name):
        indexs = [ins['column_names'] for ins in self._insp.get_indexes(name)]
        return list(set(itertools.chain.from_iterable(indexs)))

    def custom(self, query):
        return pd.read_sql(query, con=self._engine.sql_engine())

    def customize(self, table, clause_list, columns, show_id=False):
        condition = clause_list
        if columns is not None:
            cols = [
                table.__dict__[col] for col in columns if col in table.__dict__
            ]
        else:
            cols = [table]
        query = select(cols).where(condition)
        result = pd.read_sql(query, self._engine.sql_engine())
        if 'flag' in result.columns:
            result = result.drop(['flag'], axis=1)
        if 'timestamp' in result.columns:
            result = result.drop(['timestamp'], axis=1)
        if 'id' in result.columns and not show_id:
            result = result.drop(['id'], axis=1)
        return result

    def join(self, big_table, clause_list, columns):
        condition = clause_list
        cols = columns
        query = select(cols).select_from(big_table).where(condition)
        result = pd.read_sql(query, self._engine.sql_engine())
        if 'flag' in result.columns:
            result = result.drop(['flag'], axis=1)
        if 'timestamp' in result.columns:
            result = result.drop(['timestamp'], axis=1)
        if 'id' in result.columns:
            result = result.drop(['id'], axis=1)
        return result

    def base(self,
             table,
             begin_date,
             end_date,
             codes,
             time_name='trade_date',
             key=None,
             columns=None,
             freq=None,
             dates=None,
             clause_list=None,
             limit=None,
             pos=None):
        if dates is not None:
            clause_list = and_(
                table.trade_date.in_(dates), table.__dict__[key].in_(
                    codes)) if clause_list is None else clause_list
        else:
            clause_list = and_(
                table.trade_date >= begin_date, table.trade_date <= end_date,
                table.__dict__[key].in_(
                    codes)) if clause_list is None else clause_list

        ## 索引校验
        condition = and_(table.__dict__['flag'] == 1,
                         table.__dict__['flag'].isnot(None))
        indices = self.show_indexs(table.__name__)
        for clause in clause_list:
            if clause.left.name in indices:
                #condition.append(clause)
                condition = condition & clause
            else:
                raise SQLException("table:{0} {1} not indices".format(
                    table.__name__, clause.left.name))

        cols = [table.__dict__[time_name]]
        if key is not None:
            cols.append(table.__dict__[key])
        if columns is not None:
            for col in columns:
                cols.append(table.__dict__[col])
        else:
            cols = [table]
        if dates is not None:
            query = select(cols).where(condition)
        else:
            query = select(cols).where(condition)
        query = query if (limit is None or pos is None) else query.limit(
            limit).offset(pos).order_by(table.id)
        result = pd.read_sql(query, self._engine.sql_engine())
        return result

    def base_notime(self,
                    table,
                    codes=None,
                    key=None,
                    columns=None,
                    freq=None,
                    clause_list=None):
        if codes is not None:
            clause_list = and_(table.__dict__[key].in_(codes),
                               table.__dict__['flag']
                               == 1) if clause_list is None else clause_list
        elif codes is None and clause_list is not None:
            clause_list = clause_list
        ## 索引校验
        indices = self.show_indexs(table.__name__)
        condition = and_(table.__dict__['flag'] == 1,
                         table.__dict__['flag'].isnot(None))
        for clause in clause_list:
            if clause.left.name in indices:
                #condition.append(clause)
                condition = condition & clause
            else:
                raise SQLException("table:{0} {1} not indices".format(
                    table.__name__, clause.left.name))
        cols = []
        if columns is not None:
            if codes is not None:
                cols.append(table.__dict__[key])
            for col in columns:
                cols.append(table.__dict__[col])
        else:
            cols = [table]
        query = select(cols).where(condition) if key is not None else select(
            cols)
        result = pd.read_sql(query, self._engine.sql_engine())
        return result

    def base_multiple(self,
                      table,
                      clause_list=None,
                      columns=None,
                      limit=None,
                      pos=None):
        #condition = clause_list
        condition = and_(table.__dict__['flag'] == 1,
                         table.__dict__['flag'].isnot(None))

        ## 索引校验
        indices = self.show_indexs(table.__name__)
        for clause in clause_list:
            if clause.left.name in indices:
                #condition.append(clause)
                condition = condition & clause
            else:
                raise SQLException("table:{0} {1} not indices".format(
                    table.__name__, clause.left.name))

        cols = []
        if columns is not None:
            for col in columns:
                cols.append(table.__dict__[col])
        else:
            cols = [table]

        query = select(cols).where(
            condition) if clause_list is not None else select(cols)
        query = query if limit is None or pos is None else query.limit(
            limit).offset(pos).order_by(table.id)
        result = pd.read_sql(query, self._engine.sql_engine())
        return result