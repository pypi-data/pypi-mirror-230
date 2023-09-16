import os
import sys
import sqlite3

from dktotoolkit.sqlite3 import recursive_sql
from dktotoolkit import write_message

class MyDB:
    """Class to create and access with a minimum of efforts to databases sqlite3

    :param str db_path: Path to the database
    :param Lock lock: A lock to avoid concurrential access
    :param sqlite3.connector conn: The connector to the database


    :func:`MydDB.__init__` : The constructor
    :func:`MydDB.commit` : Commit the modifications
    :func:`MydDB.end_conn`) (alias :func:`MydDB.close`) : Disconnect

    :func:`MyDB.execute` : call connector.execute(), with/out lock and datas
    :func:`MyDB.add_db` : Add datas to the DB
    :func:`MyDB.insert_data` : insert datas to the database
    :func:`MyDB.request_db` : Request datas to the db from a query and column names (opt)
"""
    class LockContext:
        def __init__(self, lock_function=None):
            self.lock_function = lock_function
        #
        def __enter__(self):
            if self.lock_function:
                self.lock_function.acquire()
            #
            return self
        #

        def __exit__(self, exc_type, exc_value, traceback):
            if self.lock_function:
                self.lock_function.release()
            #
            pass
        #
    #

    def __init__(self, db_path:str=None, lock_in=None, createIfNotExists:dict=None, connect:bool=False):
        """
Constructor

:param str db_path: Path of the database
:param Lock lock_in: Lock the database
:param str|list|dict createIfNotExists: Create table (or several tables) if path not exists ;
                                       dict : {table1:{col1 : type_sql, col2: type_sql, ...}, ...}
                                       str : try to find a path to an sql script (extensino = .sql)

TODO :
------
Authorize usage of type Python or type SQL for createIfNotExists cols

"""
        self.lock=lock_in

        if not self.options:
            self.options = {}
        #
        if not "verbose" in self.options.keys():
            self.options["verbose"]=False
        #

        if db_path:
            self.db_path = db_path
        #endIf

        if self.db_path is not None and os.path.exists(self.db_path):
            pass

        elif createIfNotExists is not None:
            with self.LockContext(self.lock):
                self._create_db()
                self._init_bdd(createIfNotExists)
            #

        else:

            raise ValueError(f"path for DATABASE not exist: {self.db_path}")

        #endIf


        self.conn = sqlite3.connect(self.db_path) if connect else None


    #endDef

    def __enter__(self):
        # l'init est deja faite au moment d'entrer avec with.

        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
        #

        return self
    #

    def __exit__(self, exc_type, exc_value, exc_traceback):

        if self.conn:
            self.conn.close()
        else:
            write_message("not db setup here (activate verbose to get the trace)", verbose=self.options.get("verbose"))
            if self.options.get("verbose"):
                write_message(exc_traceback)
            #
        #
    #

    from ._request_db import request_db
    from ._add_db import add_db
    from ._insert_data import insert_data
    from ._execute import execute
    from ._get_datas import get_datas

    def commit(self):
        if not self.conn:
            self.conn.commit()
        #

    def end_conn(self):
        if not self.conn:
            return
        #

        self.conn.close()
    #endDef

    def close(self):
        return self.end_conn()
    #endDef

    def _create_db(self):

        # Creer la BDD
        # On fait le lock au dessus

        msg = f"DATABASE not exist, create a database:\n{self.db_path}\n"
        write_message(msg, verbose=self.options.get('verbose'), level="warning")

        try:

            conn = sqlite3.connect(self.db_path)

        except sqlite3.OperationalError:

            os.makedirs(os.path.dirname(self.db_path), exist_ok=True) # exist_ok : ne pas lever d'erreur si existe
            msg = f"path for DATABASE not exist, create a directory:\n{os.path.dirname(self.db_path)}\n"
            write_message(msg, verbose=self.options.get('verbose'), level="warning")

        finally:

            conn = sqlite3.connect(self.db_path)

        #endTry

        conn.commit()
        conn.close()
        #

        return 0


    def _init_bdd(self, createIfNotExists):
        # On fait le lock au dessus, dans __init__

        if isinstance(createIfNotExists, bool) and createIfNotExists:

            # On cree une bdd vide si on n'a rien pour la creer mais qu'il faut le faire

            return 0

        elif (
                isinstance(createIfNotExists, str) and
                len(os.path.splitext(createIfNotExists)) == 2 and
                os.path.splitext(createIfNotExists)[1] == ".sql") :

            # On a un fichier sql pour creer la bdd

            if self._init_bdd_from_sqlfile(filename=createIfNotExists) != 0:
                raise Exception
            #

        elif isinstance(createIfNotExists, str):

            # On a un nom de table

            createIfNotExists = [createIfNotExists,]

        #endIf

        if isinstance(createIfNotExists, list) or isinstance(createIfNotExists, tuple):

            # On a une liste de noms de tables
            if self._init_bdd_from_tablename(tablenames=createIfNotExists) != 0:
                raise Exception
            #

        # enfIf



        sys.stderr.write(f"! END WARNING : database is created\n")

    def _init_bdd_from_sqlfile(self, filename)->int:
        # Le lock est fait au-dessus, dans __init__

        if not os.path.exists(filename):
            msg = "filename variable : "
            msg += "I have a non existing path to the file : "
            msg += f"{filename} references to"
            msg += f"{os.path.abspath(filename)}"
            raise ValueError(msg)
        else:
            msg = f"> Create table using {filename}\n"
            write_message(msg, verbose=self.options.get('verbose'))
        #

        scripts = recursive_sql(filename)
        scripts = scripts if isinstance(scripts, list) else [scripts,]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for elt in scripts:
                cursor.executescript(elt)
            # endFor

            conn.commit()
        #

        return 0
    #

    def _init_bdd_from_tablename(self, tablenames)->int:
        # Le lock est fait au-dessus, dans __init__

        tablenames = {e:{"useless_col":"INTEGER"} for e in tablenames}

        with sqlite3.connect(self.db_path) as conn:

            cursor = conn.cursor()

            for elt, cols in tablenames.items():

                slist_cols = ",".join(
                    [f"{k}  {v}" for k, v in cols.items()]
                )
                query = f'CREATE TABLE {elt} ({slist_cols});'

                cursor.execute(query)

                msg = f"! Added table: {elt} with columns: {', '.join(cols.keys())}\n"
                write_message(msg, verbose=self.options.get('verbose'))

            #endFor

            conn.commit()
        #

        return 0
    #

#endClass

