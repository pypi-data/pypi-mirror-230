import os, sys
import sqlite3
from threading import Lock # verrou

def request_db(path, query, args=[]):
    conn = sqlite3.connect(f"{path}")

    c = conn.cursor()

    if args:
        c.execute( query, args )
    else:
        c.execute( query )
    #endIf

    result = c.fetchall()

    conn.close()
    return result



#endDef





def structBDD(f="bdd.bd"):
    query = f"""
SELECT book, chapter, MIN(verse_id), MAX(verse_id)
FROM verses
GROUP BY book, chapter
"""
    result = request_db(f, query)
    #print(f"DB_BOOK_NAME> {result}")

    d = ({"book":e[0], "chapter":e[1], "vidmin":e[2], "vidmax":e[3]} for e in result)
    sys.stdout.write("First request ok")
    d1 = []
    for e in d:
        sys.stdout.write(f"\r {e['book']} -- {e['chapter']} request")

        query = f"""
SELECT verse
FROM verses
WHERE verse_id={e['vidmin']}"""
        e["vmin"] = request_db(f, query)[0][0]
        query = f"""
SELECT verse
FROM verses
WHERE verse_id={e['vidmax']}"""
        e["vmax"] = request_db(f, query)[0][0]

        d1 += [(e["book"],e["chapter"], e["vmin"], e["vmax"])]
    #endFor

    print(d1)
    return 1
#endDef



if __name__=="__main__":
    path="/home/pierre/Documents/Projets/api-bible-aelf/script/external/bible.db"
    structBDD(f=path)
