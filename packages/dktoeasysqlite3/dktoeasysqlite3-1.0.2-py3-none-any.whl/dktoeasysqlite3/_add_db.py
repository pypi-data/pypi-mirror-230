import sys
def add_db(self,query:str, datas:list=[], commit:bool=True):
    """Add to database

:param str query: Query
:param list|tuple datas: ([]) List of arguments (same number as '?' in the query)
:param bool commit: (True) Commit or not commit, that is the question (if in loop, commit can be done after

:returns: 0 (= ok)
:rtypes: int
"""

    with self.lock:

        self.execute(query=query, datas=datas, lock=False)

        if commit:
            self.conn.commit()
        #endIf

    #endWith
    return 0
#endDef

