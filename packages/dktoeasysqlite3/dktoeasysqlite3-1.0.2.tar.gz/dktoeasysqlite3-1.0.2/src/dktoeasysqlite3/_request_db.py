import sys
def request_db(self,query:str, datas:list=[]):
    """Request datas

:param str query: Query
:param list|tuple datas: List of arguments (same number as '?' in the query)


:returns: Result of the database
:rtype: list[list]
"""

    with self.lock:
        c = self.execute(query=query, datas=datas, lock=False)
        result = c.fetchall()
    #endWith

    return result
#endDef

