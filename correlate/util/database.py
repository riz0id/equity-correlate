
from datetime import datetime
from sqlite3 import (Connection, Cursor)
from typing import (Any, Iterator, List, Union)
from util.ohlcv import (OHLCV)

import sqlite3

def init() -> None:

    """
    Initializes the SQLite database for storing OHLCV data.
    """

    con: Connection = sqlite3.connect("olhcv.db")
    cur: Cursor = con.cursor()

    with open("sql/create_table_ohlcv.sql", "r") as file:
        try:
            sql_script: str = file.read()
        except Exception as e:
            con.close()

            raise e

        cur.executescript(sql_script)
        con.commit()

    file.close()
    con.close()

def insert_ohlcv(aggs: Union[OHLCV, List[OHLCV]]) -> None:

    """
    Inserts an Agg, or a list of Agg objects as rows into the OHLCV database.
    """

    if isinstance(aggs, OHLCV):
        aggs = [aggs]

    con: Connection = sqlite3.connect("olhcv.db")
    cur: Cursor = con.cursor()

    for agg in aggs:
        cur.execute("""
            INSERT OR IGNORE INTO ohlcv (
                t, -- timestamp as a UNIX epoch in minutes
                s, -- symbol
                o, -- open
                h, -- high
                l, -- low
                c, -- close
                v  -- volume
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, agg.to_tuple())

    con.commit()
    con.close()

def select_ohlcv(ticker: str, t0: datetime, t1: datetime) -> List[OHLCV]:

    """
    Selects an Agg object from the database for the given symbol and timestamp.
    """

    con: Connection = sqlite3.connect("olhcv.db")
    cur: Cursor = con.cursor()

    cur.execute(
        'SELECT * FROM ohlcv WHERE s = ? AND t >= ? AND t <= ?',
        (ticker, t0.timestamp(), t1.timestamp())
    )

    rows = list(map(OHLCV.from_tuple, cur.fetchall()))

    con.close()

    return rows








