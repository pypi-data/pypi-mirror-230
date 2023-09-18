#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '1.0.1'

__all__ = ["DbDialect", "database", "SQLConn", "SQLRow", "SQLRowCollection", "SQLParser", "Connection", "BaseDbs",
           "MultipleBaseDbs"]

import os
import re
from collections import OrderedDict
from contextlib import contextmanager

from sqlalchemy import (
    create_engine,
    exc,
    inspect,
    text
)

try:
    string_types = (str, unicode)
except:
    string_types = str


class SQLRow(dict):
    def __init__(self, keys, values):
        assert len(keys) == len(values)
        super(SQLRow, self).__init__(zip(keys, values))
        self.cursor_description = [x for x in keys]

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, super(SQLRow, self).__repr__())

    def __getitem__(self, key):
        if isinstance(key, int):
            if key > len(self.cursor_description):
                raise IndexError("data index out of range")
            key = self.cursor_description[key]
            return super(SQLRow, self).__getitem__(key)

        if key in self.cursor_description:
            return super(SQLRow, self).__getitem__(key)

        raise KeyError("SQLRow contains no '{}' field.".format(key))

    def __getattr__(self, key):
        if key in self.cursor_description:
            return super(SQLRow, self).__getitem__(key)
        return None

    def __len__(self):
        return len(self.cursor_description)

    def as_dict(self, ordered=False):
        return OrderedDict(self) if ordered else dict(self)

    def __getstate__(self):
        return self.as_dict()

    def __setstate__(self, state):
        self.__init__(state.keys(), state.values())


class SQLRowCollection(object):
    def __init__(self, rows):
        self._rows = rows
        self._all_rows = []
        self.pending = True

    def __repr__(self):
        return '<SQLRowCollection size={} pending={}>'.format(len(self), self.pending)

    def __iter__(self):
        i = 0
        while True:
            if i < len(self):
                yield self[i]
            else:
                try:
                    yield next(self)
                except StopIteration:
                    return
            i += 1

    def next(self):
        return self.__next__()

    def __next__(self):
        try:
            nextrow = next(self._rows)
            self._all_rows.append(nextrow)
            return nextrow
        except StopIteration:
            self.pending = False
            raise StopIteration('SQLRowCollection contains no more rows.')

    def __getitem__(self, key):
        is_int = isinstance(key, int)

        if is_int:
            key = slice(key, key + 1)

        while key.stop is None or len(self) < key.stop:
            try:
                next(self)
            except StopIteration:
                break

        rows = self._all_rows[key]
        if is_int:
            return rows[0]
        else:
            return SQLRowCollection(iter(rows))

    def __len__(self):
        return len(self._all_rows)

    def list(self, as_dict=False, as_ordereddict=False):
        rows = list(self)

        if as_dict:
            return [r.as_dict() for r in rows]
        elif as_ordereddict:
            return [r.as_dict(ordered=True) for r in rows]

        return rows

    def as_dict(self, ordered=False):
        return self.list(as_dict=not (ordered), as_ordereddict=ordered)

    def first(self, default=None, as_dict=False, as_ordereddict=False):
        try:
            record = self[0]
        except IndexError:
            if isexception(default):
                raise default
            return default

        if as_dict:
            return record.as_dict()
        elif as_ordereddict:
            return record.as_dict(ordered=True)
        else:
            return record

    def one(self, default=None, as_dict=False, as_ordereddict=False):
        try:
            self[1]
        except IndexError:
            return self.first(default=default, as_dict=as_dict, as_ordereddict=as_ordereddict)
        else:
            raise ValueError('SQLRowCollection contained more than one row. '
                             'Expects only one row when using '
                             'SQLRowCollection.one')

    def scalar(self, default=None):
        row = self.one()
        return row[0] if row else default


def isexception(obj):
    if isinstance(obj, Exception):
        return True
    if isinstance(obj, type) and issubclass(obj, Exception):
        return True
    return False


class SQLParser:
    params_mark = "_leafdb_argv_"

    @staticmethod
    def select(query, *args, **kwargs):
        """转换查询语句"""
        paramstyle_count = query.count('?')

        # 参数长度和query字符串中的?个数必须一致
        assert len(args) == paramstyle_count

        keys = kwargs.keys()
        if paramstyle_count == 0 and len(keys) <= 0:
            return query, {}

        params = {}
        if paramstyle_count > 0:
            query_list = query.split('?')
            param_len = len(query_list)
            result = []
            for i, q in enumerate(query_list):
                result.append(q)
                if param_len > (i + 1):
                    result.append(":%s%d" % (SQLParser.params_mark, i))
            query = "".join(result)
            for i, argv in enumerate(args):
                _key = "%s%d" % (SQLParser.params_mark, i)
                params.update({_key: argv})

        if len(keys) > 0:
            extparams = []
            for key in keys:
                extparams.append("%s=:%s" % (key, key))
            extparams_str = " AND ".join(extparams)
            ret = re.findall("where", query, flags=re.IGNORECASE)
            if len(ret) > 0:
                extparams_str = "WHERE (%s) AND" % extparams_str
                query = re.sub("where", extparams_str, query, flags=re.IGNORECASE)
            else:
                extparams_str = "WHERE %s" % extparams_str
                query = "%s %s" % (query, extparams_str)
            params.update(kwargs)

        return query, params

    @staticmethod
    def insert(table, **kwargs):
        """转换插入语句"""
        keys = kwargs.keys()
        params = []
        values = []
        for key in keys:
            params.append(key)
            values.append(":%s" % key)
        return "INSERT INTO %s (%s) VALUES (%s)" % (table, ",".join(params), ",".join(values))

    @staticmethod
    def update(table, *args, **kwargs):
        """转换更新语句"""
        where = kwargs.pop("where", None)
        sqls = ["UPDATE %s SET" % table]

        keys = kwargs.keys()
        params = []
        for key in keys:
            params.append("%s=:%s" % (key, key))
        sqls.append(",".join(params))

        if where:
            sqls.append("WHERE")
            paramstyle_count = where.count('?')
            assert len(args) == paramstyle_count

            where_list = where.split('?')
            where_len = len(where_list)
            where_result = []
            for i, w in enumerate(where_list):
                where_result.append(w)
                if where_len > (i + 1):
                    where_result.append(":%s%d" % (SQLParser.params_mark, i))
            where = "".join(where_result)
            sqls.append(where)

            params = {}
            for i, argv in enumerate(args):
                _key = "%s%d" % (SQLParser.params_mark, i)
                params.update({_key: argv})
            kwargs.update(params)
        return " ".join(sqls), kwargs

    @staticmethod
    def delete(table, *args, **kwargs):
        """转换删除语句"""
        where = kwargs.pop("where", None)
        sqls = ["DELETE FROM %s" % table]

        keys = kwargs.keys()
        if len(keys) > 0:
            sqls.append("WHERE")
            result = []
            for key in keys:
                result.append("%s=:%s" % (key, key))
            sqls.append("(")
            sqls.append(" AND ".join(result))
            sqls.append(")")

        if where:
            if "WHERE" in sqls:
                sqls.append("AND")

            paramstyle_count = where.count('?')
            assert len(args) == paramstyle_count

            where_list = where.split('?')
            where_len = len(where_list)
            where_result = []
            for i, w in enumerate(where_list):
                where_result.append(w)
                if where_len > (i + 1):
                    where_result.append(":%s%d" % (SQLParser.params_mark, i))
            where = "".join(where_result)
            sqls.append(where)

            params = {}
            for i, argv in enumerate(args):
                _key = "%s%d" % (SQLParser.params_mark, i)
                params.update({_key: argv})
            kwargs.update(params)
        return " ".join(sqls), kwargs


class Connection(object):
    def __init__(self, connection):
        self._conn = connection
        self._dbtype = (connection.engine.name or "").lower().strip()
        self.open = not connection.closed

    def close(self):
        self._conn.close()
        self.open = False

    def __enter__(self):
        return self

    def __exit__(self, exc, val, traceback):
        self.close()

    def __repr__(self):
        return '<Connection open={}>'.format(self.open)

    def query(self, query, fetchall=False, **params):
        cursor = self._conn.execute(text(query), **params)
        if not cursor.keys():  # Skip insert,update has none return values error
        	return None
        row_gen = (SQLRow(cursor.keys(), row) for row in cursor)
        results = SQLRowCollection(row_gen)
        if fetchall:
            results.list()
        return results

    def bulk_query(self, query, *multiparams):
        self._conn.execute(text(query), *multiparams)

    def query_file(self, path, fetchall=False, **params):
        if not os.path.exists(path):
            raise IOError("File '{}' not found!".format(path))
        if os.path.isdir(path):
            raise IOError("'{}' is a directory!".format(path))
        with open(path) as f:
            query = f.read()
        return self.query(query=query, fetchall=fetchall, **params)

    def bulk_query_file(self, path, *multiparams):
        if not os.path.exists(path):
            raise IOError("File '{}'' not found!".format(path))
        if os.path.isdir(path):
            raise IOError("'{}' is a directory!".format(path))
        with open(path) as f:
            query = f.read()
        self._conn.execute(text(query), *multiparams)

    def select(self, query, *args, **kwargs):
        """SELECT 语句"""
        _test = kwargs.pop("_test", False)
        _fetchall = True if self._dbtype == "mssql" else False
        fetchall = kwargs.pop("fetchall", _fetchall)
        query, params = SQLParser.select(query, *args, **kwargs)
        if _test:
            return query, params
        return True, self.query(query, fetchall=fetchall, **params)

    def selectone(self, query, *args, **kwargs):
        """SELECT 第一个结果"""
        _test = kwargs.pop("_test", False)
        _fetchall = True if self._dbtype == "mssql" else False
        fetchall = kwargs.pop("fetchall", _fetchall)

        query, params = SQLParser.select(query, *args, **kwargs)
        if _test:
            return query, params

        row = self.query(query, fetchall=fetchall, **params).first()
        if not row:
            return False, row
        return True, row

    def insert(self, table, **kwargs):
        """插入单条数据"""
        _test = kwargs.pop("_test", False)
        query = SQLParser.insert(table, **kwargs)
        if _test:
            return query, kwargs

        return True, self.query(query, **kwargs)

    def multiple_insert(self, table, values, **kwargs):
        """同时插入多条数据"""
        if not isinstance(values, list):
            return ValueError("values must be a list for dict.")

        if len(values) <= 0:
            if len(kwargs) > 0:
                return self.insert(table, **kwargs)
            return ValueError("values must be not empty.")

        _test = kwargs.pop("_test", False)
        query = SQLParser.insert(table, **values[0])
        if _test:
            return query, values

        return True, self.bulk_query(query, values)

    def update(self, table, *args, **kwargs):
        """更新数据"""
        _test = kwargs.pop("_test", False)
        where = kwargs.pop("where", None)

        if not where:
            # 从第一个参数获取where语句
            if len(args) > 0:
                where = args[0]
                args = args[1:]
        if where:
            kwargs.update(dict(where=where))

        query, params = SQLParser.update(table, *args, **kwargs)
        if _test:
            return query, params

        return True, self.query(query, **params)

    def delete(self, table, *args, **kwargs):
        """删除数据"""
        _test = kwargs.pop("_test", False)
        where = kwargs.pop("where", None)

        if not where:
            # 从第一个参数获取where语句
            if len(args) > 0:
                where = args[0]
                args = args[1:]
        if where:
            kwargs.update(dict(where=where))

        query, params = SQLParser.delete(table, *args, **kwargs)
        if _test:
            return query, params

        return True, self.query(query, **params)

    def transaction(self):
        return self._conn.begin()


class BaseDbs(object):
    # 定义默认的数据库驱动字典
    engines = {
        "mssql": "pymssql",
        "mysql": "pymysql",
        "oracle": "cx_oracle",
        "postgresql": "psycopg2"
    }

    def __init__(self, db_url=None, **kwargs):
        if not db_url:
            db_url, kwargs = self.gen_dburl(**kwargs)

        # Create an engine.
        self._engine = create_engine(db_url, **kwargs)
        self.open = True
        self.version = None

    def gen_dburl(self, **kwargs):
        """
        自定义从字典中获取链接串
        """
        engine = kwargs.pop("ENGINE", None)
        if not engine:
            return None

        driver = kwargs.pop("ODBC", self.engines.get(engine))
        if driver:
            engine = "%s+%s" % (engine, driver)

        dbname = kwargs.pop("NAME", None)
        if not dbname:
            return None

        user = kwargs.pop("USER", "")
        pwd = kwargs.pop("PASSWORD", kwargs.pop("PWD", ""))
        host = kwargs.pop("HOST", "127.0.0.1")
        port = kwargs.pop("PORT", None)
        if port:
            host = "%s:%s" % (host, port)
        charset = kwargs.pop("CHARSET", "utf8")

        echo = kwargs.pop("PRINTING", False)
        pool_size = kwargs.pop("CONNECTIONS", 5)
        pool_recycle = kwargs.pop("TIMEOUT", 3600)

        kwargs.update(dict(echo=echo, pool_size=pool_size, pool_recycle=pool_recycle))

        configs = {"engine": engine, "user": user, "pwd": pwd, "host": host, "dbname": dbname, "charset": charset}
        db_url = "{engine}://{user}:{pwd}@{host}/{dbname}?charset={charset}".format(**configs)
        return db_url, kwargs

    def close(self):
        self._engine.dispose()
        self.open = False

    def __enter__(self):
        return self

    def __exit__(self, exc, val, traceback):
        self.close()

    def __repr__(self):
        return '<BaseDbs open={}>'.format(self.open)

    def get_table_names(self, internal=False):
        # Setup SQLAlchemy for BaseDbs inspection.
        return inspect(self._engine).get_table_names()

    def get_version(self):
        if not self.version:
            _fetchall = True if self._engine.name.lower() == "mssql" else False
            self.version = self.query("select @@version", fetchall=_fetchall).first()[0]
        return self.version

    def get_connection(self):
        if not self.open:
            raise exc.ResourceClosedError('BaseDbs closed.')
        return Connection(self._engine.connect())

    def query(self, query, fetchall=False, **params):
        with self.get_connection() as conn:
            return conn.query(query, fetchall, **params)

    def bulk_query(self, query, *multiparams):
        with self.get_connection() as conn:
            conn.bulk_query(query, *multiparams)

    def query_file(self, path, fetchall=False, **params):
        with self.get_connection() as conn:
            return conn.query_file(path, fetchall, **params)

    def bulk_query_file(self, path, *multiparams):
        with self.get_connection() as conn:
            conn.bulk_query_file(path, *multiparams)

    @contextmanager
    def transaction(self):
        conn = self.get_connection()
        tx = conn.transaction()
        try:
            yield conn
            tx.commit()
        except Exception:
            tx.rollback()
        finally:
            conn.close()

    def select(self, query, *args, **kwargs):
        with self.get_connection() as conn:
            return conn.select(query, *args, **kwargs)

    def selectone(self, query, *args, **kwargs):
        with self.get_connection() as conn:
            return conn.selectone(query, *args, **kwargs)

    def insert(self, table, **kwargs):
        with self.get_connection() as conn:
            return conn.insert(table, **kwargs)

    def multiple_insert(self, table, values, **kwargs):
        with self.get_connection() as conn:
            return conn.multiple_insert(table, values, **kwargs)

    def update(self, table, *args, **kwargs):
        with self.get_connection() as conn:
            return conn.update(table, *args, **kwargs)

    def delete(self, table, *args, **kwargs):
        with self.get_connection() as conn:
            return conn.delete(table, *args, **kwargs)


class MultipleBaseDbs(object):
    def __init__(self, **kwargs):
        self._baseconn = kwargs.pop("_baseconn", "default")
        self._dbs = {}

        for k, v in kwargs.items():
            self._dbs[k] = BaseDbs(**v)

    def __len__(self):
        return len(self._dbs)

    def __repr__(self):
        return "MultipleBaseDbs {}".format(self._dbs)

    def __getattr__(self, name):
        if name in self._dbs:
            return self._dbs.get(name)
        elif (self._baseconn in self._dbs) and hasattr(self._dbs.get(self._baseconn), name):
            return getattr(self._dbs.get(self._baseconn), name)

        raise KeyError("not find database: %s in DB Config" % name)

    def close(self):
        for v in self._dbs.values():
            v.close()


class DbDialect:
    def __init__(self, dialect, version=None):
        self.params_mark = BaseDbs.params_mark
        self.dialect = dialect
        self.version = version

    def _getversion(self):
        if not self.version:
            return None

        _vstr = self.version.upper()
        if self.dialect.lower() == "mssql":
            if "SQL SERVER 2014" in _vstr:
                return 12
            elif "SQL SERVER 2012" in _vstr:
                return 11
            elif "SQL SERVER 2008R2" in _vstr:
                return 10.5
            elif "SQL SERVER 2008" in _vstr:
                return 10
            elif "SQL SERVER 2005" in _vstr:
                return 9
        return None

    def _parseKwargs(self, **kwargs):
        if len(kwargs) <= 0:
            return ""

        sql = []
        for key in kwargs.keys():
            sql.append("%s=:%s" % (key, key))
        sql = " AND ".join(sql)
        return "(" + sql + ")"

    def _parseArgs(self, where, *args):
        if not where:
            return "", {}

        if len(args) <= 0:
            return where or "", {}

        paramstyle_count = where.count('?')
        assert paramstyle_count == len(args)

        where_list = where.split('?')
        where_len = len(where_list)
        where_result = []
        for i, w in enumerate(where_list):
            where_result.append(w)
            if where_len > (i + 1):
                where_result.append(":%s%d" % (self.params_mark, i))
        where = "".join(where_result)

        params = {}
        for i, argv in enumerate(args):
            _key = "%s%d" % (self.params_mark, i)
            params.update({_key: argv})

        return where, params

    def _parseFields(self, fields, temp=None):
        def not_empty(s):
            return str(s) and str(s).strip()

        if isinstance(fields, str):
            fields = fields.split(",")
        if not isinstance(fields, list) and not isinstance(fields, tuple):
            raise KeyError("fields must be string or list/tuple for string")

        fields = list(set(fields))
        fields = list(filter(not_empty, fields))
        if temp:
            fields = ["{temp}.{value}".format(temp=temp, field=field) for field in fields]
        return ",".join(fields)

    def MySqlDialect(self, table, fields, page, pagesize, where, order, primarykey, *args, **kwargs):
        offset = (page - 1) * pagesize
        if offset < 0:
            offset = 0

        sql = ["SELECT {fields} FROM {table}".format(fields=self._parseFields(fields), table=table)]

        where_result = []
        _where1 = self._parseKwargs(**kwargs)
        _where2, _params = self._parseArgs(where, *args)
        kwargs.update(_params)

        if _where1:
            where_result.append(_where1)
        if _where2:
            where_result.append(_where2)
        if len(where_result) > 0:
            where = " AND ".join(where_result)
            sql.append("WHERE {where}".format(where=where))

        if order:
            sql.append("ORDER BY {order}".format(order=order))

        sql.append("LIMIT {offset},{pagesize}".format(offset=offset, pagesize=pagesize))
        return " ".join(sql), kwargs

    def Mssql2012Dialect(self, table, fields, page, pagesize, where, order, primarykey, *args, **kwargs):
        offset = (page - 1) * pagesize
        if offset < 0:
            offset = 0

        sql = ["SELECT {fields} FROM {table}".format(fields=self._parseFields(fields), table=table)]

        where_result = []
        _where1 = self._parseKwargs(**kwargs)
        _where2, _params = self._parseArgs(where, *args)
        kwargs.update(_params)

        if _where1:
            where_result.append(_where1)
        if _where2:
            where_result.append(_where2)
        if len(where_result) > 0:
            where = " AND ".join(where_result)
            sql.append("WHERE {where}".format(where=where))

        if order:
            sql.append("ORDER BY {order}".format(order=order))
        else:
            sql.append("ORDER BY {primarykey}".format(primarykey=primarykey))

        sql.append("OFFSET {offset} ROWS FETCH NEXT {pagesize} ROWS ONLY".format(offset=offset, pagesize=pagesize))
        return " ".join(sql), kwargs

    def MssqlDialect(self, table, fields, page, pagesize, where, order, primarykey, *args, **kwargs):
        offset = (page - 1) * pagesize
        if offset < 0:
            offset = 0

        fields = self._parseFields(fields)
        sql = ["SELECT TOP {pagesize} {fields} FROM {table}".format(pagesize=pagesize, fields=fields, table=table)]
        tsql = ["SELECT TOP {offset} {prikey} FROM {table}".format(offset=offset, prikey=primarykey, table=table)]

        where_result = []
        _where1 = self._parseKwargs(**kwargs)
        _where2, _params = self._parseArgs(where, *args)
        kwargs.update(_params)

        if _where1:
            where_result.append(_where1)
        if _where2:
            where_result.append(_where2)
        if len(where_result) > 0:
            where = " AND ".join(where_result)
            sql.append("WHERE")
            sql.append(where)
            tsql.append("WHERE")
            tsql.append(where)

        kwargs.update(_params)

        if order:
            order = "ORDER BY {order}".format(order=order)
        else:
            order = "ORDER BY {primarykey}".format(primarykey=primarykey)
        tsql.append(order)

        if offset > 0:
            if "WHERE" in sql:
                sql.append("AND")
            else:
                sql.append("WHERE")
            sql.append("{primarykey} NOT IN ({tsql})".format(primarykey=primarykey, tsql=" ".join(tsql)))

        sql.append(order)
        return " ".join(sql), kwargs

    def OracleDialect(self, table, fields, page, pagesize, where, order, primarykey, *args, **kwargs):
        raise TypeError("Not Support {dialect} in this version.".format(dialect=self.dialect))

    def SqliteDialect(self, table, fields, page, pagesize, where, order, primarykey, *args, **kwargs):
        raise TypeError("Not Support {dialect} in this version.".format(dialect=self.dialect))

    def PostgreSqlDialect(self, table, fields, page, pagesize, where, order, primarykey, *args, **kwargs):
        raise TypeError("Not Support {dialect} in this version.".format(dialect=self.dialect))

    def AnsiSqlDialect(self, table, fields, page, pagesize, where, order, primarykey, *args, **kwargs):
        raise TypeError("Not Support {dialect} in this version.".format(dialect=self.dialect))

    def forPaginate(self, table, fields, page, pagesize, where, order, primarykey, *args, **kwargs):
        if self.dialect.lower() == "mssql":
            version = self._getversion()
            if version and version >= 11:
                return self.Mssql2012Dialect(table, fields, page, pagesize, where, order, primarykey, *args, **kwargs)
            return self.MssqlDialect(table, fields, page, pagesize, where, order, primarykey, *args, **kwargs)
        elif self.dialect.lower() == "mysql":
            return self.MySqlDialect(table, fields, page, pagesize, where, order, primarykey, *args, **kwargs)
        elif self.dialect.lower() == "oracle":
            return self.OracleDialect(table, fields, page, pagesize, where, order, primarykey, *args, **kwargs)
        elif self.dialect.lower() == "sqlite":
            return self.SqliteDialect(table, fields, page, pagesize, where, order, primarykey, *args, **kwargs)
        elif self.dialect.lower() == "postgresql":
            return self.PostgreSqlDialect(table, fields, page, pagesize, where, order, primarykey, *args, **kwargs)
        else:
            return self.AnsiSqlDialect(table, fields, page, pagesize, where, order, primarykey, *args, **kwargs)


class database(BaseDbs):
    params_mark = "_leafdb_argv_"

    def _converModify(self, sql, *args, **kwargs):
        paramstyle_count = sql.count('?')
        assert len(args) == paramstyle_count

        q_list = sql.split('?')
        q_len = len(q_list)
        q_result = []
        for i, q in enumerate(q_list):
            q_result.append(q)
            if q_len > (i + 1):
                q_result.append(":%s%d" % (self.params_mark, i))

        params = {}
        for i, argv in enumerate(args):
            _key = "%s%d" % (self.params_mark, i)
            params.update({_key: argv})
        kwargs.update(params)

        return "".join(q_result), kwargs

    def selectpage(self, table, fields, page, pagesize, **kwargs):
        where = kwargs.pop("where", None)
        args = kwargs.pop("args", ())
        order = kwargs.pop("order", None)
        primarykey = kwargs.pop("primarykey", "id")
        _fetchall = True if self._engine.name.lower() == "mssql" else False
        fetchall = kwargs.pop("fetchall", _fetchall)

        _test = kwargs.pop("_test", False)
        dbDialect = DbDialect(self._engine.name, self.get_version())
        query, params = dbDialect.forPaginate(table, fields, page, pagesize, where, order, primarykey, *args, **kwargs)
        if _test:
            return query, params

        return True, self.query(query, fetchall=fetchall, **params)

    def modify(self, sql, *args, **kwargs):
        _test = kwargs.pop("_test", False)
        query, params = self._converModify(sql, *args, **kwargs)
        if _test:
            return query, params

        return True, self.query(query, **params)


class SQLConn(object):
    def __init__(self, *args, **configs):
        _baseconn = None
        if len(args) > 0:
            assert isinstance(args[0], string_types)
            _baseconn = args[0].strip()
        _baseconn = _baseconn or configs.pop("_baseconn", "default")

        self._baseconn = _baseconn
        self._dbc = configs.copy()
        self._dbs = {}

    def __len__(self):
        return len(self._dbs)

    def __repr__(self):
        return "SQLConn {}".format(self._dbs)

    def __getattr__(self, name):
        db = None
        if name.lower() not in dir(database):
            db = self._gen_conn(name)
            return db

        if not db:
            db = self._gen_conn(self._baseconn)
            if hasattr(db, name):
                return getattr(db, name)

        raise KeyError("not find database: %s in DB Config" % name)

    def _gen_conn(self, name):
        if name in self._dbs:
            return self._dbs.get(name)
        else:
            _dbc = self._dbc.get(name)
            _lpt = _dbc.pop("printing", False)
            printing = any([_lpt, _dbc.get("PRINTING")])
            _dbc.update(dict(PRINTING=printing))
            if _dbc:
                _db = database(**_dbc)
                self._dbs[name] = _db
                return _db
        return None

    def close(self):
        for v in self._dbs.values():
            v.close()
        self._dbs.clear()
