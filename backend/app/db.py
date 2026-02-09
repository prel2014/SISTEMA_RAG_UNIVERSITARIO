import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor
from flask import g

_pool = None


def init_pool(app):
    global _pool
    _pool = ThreadedConnectionPool(
        minconn=2,
        maxconn=10,
        dsn=app.config['DATABASE_URL'],
        cursor_factory=RealDictCursor,
    )

    @app.teardown_appcontext
    def return_conn(exc):
        conn = g.pop('db_conn', None)
        if conn is not None:
            if exc:
                conn.rollback()
            _pool.putconn(conn)


def get_conn():
    """Get a connection from the pool, stored in Flask g (auto-returned on teardown)."""
    if 'db_conn' not in g:
        g.db_conn = _pool.getconn()
        g.db_conn.autocommit = False
    return g.db_conn


def get_conn_raw():
    """Get a connection for background threads (NOT stored in Flask g). Caller must put_conn_raw()."""
    conn = _pool.getconn()
    conn.autocommit = False
    return conn


def put_conn_raw(conn):
    """Return a raw connection to the pool."""
    if conn is not None:
        _pool.putconn(conn)


def call_fn(fn_name, params=None, fetch_one=False, fetch_all=False, conn=None):
    """Call a stored function: SELECT * FROM fn_name(params...)"""
    own_conn = conn is None
    if own_conn:
        conn = get_conn()

    placeholders = ', '.join(['%s'] * len(params)) if params else ''
    sql = f'SELECT * FROM {fn_name}({placeholders})'

    cur = conn.cursor()
    try:
        cur.execute(sql, params or ())
        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        else:
            result = None
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def execute(query, params=None, fetch_one=False, fetch_all=False, conn=None):
    """Execute raw SQL."""
    own_conn = conn is None
    if own_conn:
        conn = get_conn()

    cur = conn.cursor()
    try:
        cur.execute(query, params or ())
        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        else:
            result = None
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
