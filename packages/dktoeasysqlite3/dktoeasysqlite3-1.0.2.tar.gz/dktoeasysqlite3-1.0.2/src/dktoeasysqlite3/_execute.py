import sys
import logging
# import traceback

def _execute(conn, query, datas):
    """
    :param sqlite3.connector conn: Connector
    :param str query: Query
    :param list|tuple datas: List of arguments (same number as '?' in the query)

    :returns: cursor of the db
    """

    c = conn.cursor()

    if datas is not None:
        try:
            c.execute( query, datas )
        except:
            logging.critical(f"""Query : {query}
Datas : {datas}
""")
            raise
        #
    else:
        try:
            c.execute( query )
        except:
            logging.critical(f"""Query : {query}""")
            raise
        #
    #endIf

    return c

def execute(self, query:str, datas:list=[], lock:bool=False):
    """
    :param str query: Query
    :param list|tuple datas: List of arguments (same number as '?' in the query)

    :param book lock: enable/disable lock

    :raise ValueError: query not a string
    :raise ValueError: datas is not a list

    :returns: cursor of the db
    """

    if not isinstance(query, str):
        raise ValueError(f"""query is expected to be a string, not {type(query)}
Query={query}""")
    #endIf
    if not isinstance(datas, list) and not isinstance(datas, tuple):
        logging.warning(f"datas is expected to be a list, not {type(datas)}, convert to list.")
        datas=[datas,]
    #endIf

    if lock:
        
        with self.LockContext(self.lock):
            with sqlite3.connect(self.db_path) as conn:
                execution = _execute(conn, query, datas)
            #
            
        #EndWith
    else:
        execution = _execute(self.conn, query, datas)
    #

    return execution
#endDef
