from enum import Enum
from typing import Union

import sqlite3
import oracledb
import pandas as pd
import pymssql
import pyodbc
import psycopg2
import psycopg2.extras

from . import _config as config
from ._helpers import dict_factory
from .exceptions import NotDatabaseError


class Database(Enum):
    MSSQL = 'mssql'
    ORACLE = 'oracle'
    POSTGRESQL = 'postgresql'
    SQLITE = 'sqlite'
    ACCESS = 'access'


def connect(database: Database):
    if not isinstance(database, Database):
        raise NotDatabaseError('Must be a database.Database instance.')

    if database == Database.MSSQL:
        return pymssql.connect(
            server=config.mssql_server,
            user=config.mssql_user,
            password=config.mssql_password,
            database=config.mssql_database,
        )

    elif database == Database.ORACLE:
        oracledb.init_oracle_client()
        return oracledb.connect(
            user=config.oracle_user,
            password=config.oracle_password,
            dsn=config.oracle_dsn,
        )

    elif database == Database.POSTGRESQL:
        return psycopg2.connect(
            dsn=config.postgresql_url,
            cursor_factory=psycopg2.extras.RealDictCursor
        )

    elif database == Database.SQLITE:
        return sqlite3.connect(database=config.sqlite_path)

    elif database == Database.ACCESS:
        return pyodbc.connect(
            f'''
            Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};
            DBQ={config.access_path};
            '''
        )


def query(
    database: Database,
    query: str,
    params: Union[list, tuple] = None,
    fetch: bool = True,
    as_df: bool = True,
    datetime_cols: list = None,
    index_col: str = None
) -> Union[list, pd.DataFrame]:
    con = connect(database)
    if database == Database.MSSQL:
        cur = con.cursor(as_dict=True)

    elif database == Database.SQLITE:
        con.row_factory = dict_factory
        cur = con.cursor()

    elif database in [Database.ORACLE, Database.ACCESS, Database.POSTGRESQL]:
        cur = con.cursor()

    cur.execute(query) if params is None else (
        cur.executemany(query, params)
        if isinstance(params, list) else cur.execute(query, params)
    )

    if database == Database.ORACLE:
        cols = [col[0] for col in cur.description]
        cur.rowfactory = lambda *args: dict(zip(cols, args))

    obj = None
    if fetch:
        obj = cur.fetchall()

        if database == Database.POSTGRESQL:
            obj = [dict(row) for row in obj]

        elif database == Database.ACCESS:
            obj = [
                dict(zip([col[0] for col in cur.description], row))
                for row in obj
            ]

        if as_df:
            obj = make_tabular(obj, index_col, datetime_cols)

    con.commit()
    con.close()

    return obj


def make_tabular(
    obj: list[dict],
    index_col: str,
    datetime_cols: list = None
) -> pd.DataFrame:
    df = pd.DataFrame(obj)
    if index_col:
        df.set_index(index_col, inplace=True)
    if datetime_cols:
        df[datetime_cols] = df[datetime_cols].apply(pd.to_datetime)

    return df