from flask import g


def query_db(query, args=(), one=False):
    """
    Executes a query on the current request's DB connection (g.db).
    Returns a list of sqlite3.Row -- or a single row if `one=True`.
    """
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if one:
        return rv[0] if rv else None
    return rv