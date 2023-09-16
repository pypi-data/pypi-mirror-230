"""
@author: Pierre
"""
import os, sys
import sqlite3
from threading import Lock # verrou




class GlobalVarStorage:
    def __init__(self):
        self.db_name=os.environ.get("API_BIBLE_GLOBAL_DB_NAME")
        self.conn = sqlite3.connect(f"{self.db_name}.db")

        self.to_html=True

        #self.lock = Lock()
    #endDef

    def set_global_var(self, name, value):
        #with self.lock:
        c = self.conn.cursor()
        c.execute(f"CREATE TABLE IF NOT EXISTS {self.db_name} (name text, value text)")
        c.execute(f"INSERT OR REPLACE INTO {self.db_name} (name, value) VALUES (?, ?)", (name, value))
        self.conn.commit()
        #endWith
    #endDef

    def get_global_var(self, name):
        #with self.lock:
        c = self.conn.cursor()
        c.execute(f"CREATE TABLE IF NOT EXISTS {self.db_name} (name text, value text)")
        c.execute(f"SELECT value FROM  {self.db_name} WHERE name=?", (name,))
        result = c.fetchone()
        if result is None:
            return None
        elif self.to_html:
            return accents2html(result[0])
        #endIf
        return result[0]
        #endWith
    #endDef
#endClass


