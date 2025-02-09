from .sqlitedb import connect_database
from .sqlitedb import insert_clan, insert_user
conn, cur, tables = connect_database()

__all__ = ["cur", "conn", "insert_clan", "insert_user"]
