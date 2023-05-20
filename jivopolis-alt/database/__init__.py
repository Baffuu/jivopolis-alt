from .sqlitedb import connect_database  # pyright: ignore
from .sqlitedb import insert_clan, insert_user  # noqa: F401, E402
conn, cur = connect_database()

__all__ = ["cur", "conn", "insert_clan", "insert_user"]
