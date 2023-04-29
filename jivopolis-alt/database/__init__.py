from .sqlitedb import connect_database
conn, cur = connect_database()
from ..fyCursor import fyCursor 
cur: fyCursor
from .sqlitedb import insert_clan, insert_user
