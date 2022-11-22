import os
from pathlib import Path
from ImageManager.data import globals as data_globals
from ImageManager.app import globals as app_globals
import sqlite3
from enum import Enum


class RequestTypes(Enum):
    NoReturn = 'no_return'
    ReturnData = 'return data'


def database_file():
    data_globals.db_file = Path(os.getcwd(), 'data', 'im.atd')


def new_database():
    con = sqlite3.connect(str(data_globals.db_file))
    con.close()
    _init_data()


def _init_data():
    pass
    # for sql_file in Path(os.getcwd(), 'data', 'sql').iterdir():
    #     with open(str(sql_file), mode='r') as sql_data:
    #         sql_scripts = sql_data.read().split(';')
    #         for sql_script in sql_scripts:
    #             execute(sql_script, RequestTypes.NoReturn)


def execute(query, type: RequestTypes = RequestTypes.ReturnData):
    try:
        if data_globals.con is None:
            connection()
        if type == RequestTypes.NoReturn:
            data_globals.cur.execute(query)
            data_globals.con.commit()
            return data_globals.cur.lastrowid
        if type == RequestTypes.ReturnData:
            data_globals.cur.execute(query)
            return data_globals.cur.fetchall()
    except Exception as ex:
        print(ex)


def connection():
    data_globals.con = sqlite3.connect(str(data_globals.db_file))
    data_globals.cur = data_globals.con.cursor()
