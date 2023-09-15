import sqlite3
import contextlib
from typing import Tuple, Union
from custom_types import TokenData


def db_connection_handler(query: str, params: Tuple[str] = None) -> Union[TokenData, bool]:
    query_results = ''
    with contextlib.closing(sqlite3.connect('tokens.db')) as con:
        con.row_factory = sqlite3.Row
        with con as cur:
            if params:
                query_results = cur.execute(query, params)
            else:
                query_results = cur.execute(query)

            if 'select' in query.lower():
                query_results = [dict(t) for t in query_results.fetchall()]

    return query_results
