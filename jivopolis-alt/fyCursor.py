from sqlite3 import Cursor, Connection, ProgrammingError, connect
import logging
from typing import Union, Any


class fyCursor(Cursor):
    """
    Custom `sqlite3.Cursor` that can be used without string query. \n
    I just hate query because it does not have any highlighting, yeah.
    """
    def __init__(
        self, 
        __cursor: Connection, 
        logger = None
    ) -> None:
        """
        Initialise a cursor.

        :param __cursor - sqlite3 connection
        :param logger - custom logger (Optional) 
        """
        super().__init__(__cursor)
        self._logger = logging.getLogger("fyCursor") if logger is None else logger
        

    def update(self, table) -> 'fyCursor':
        self._query = f"UPDATE {table}"
        return self

    def add(self, **kwargs) -> 'fyCursor':
        if not self._query:
            raise ProgrammingError("You should use something before `add`")
        column = list(kwargs.keys())[0]
        value = list(kwargs.values())[0]
        self._query += f" SET {column} = {column} + {value}"
        return self
        
    def set(self, **kwargs) -> 'fyCursor':
        if not self._query:
            raise ProgrammingError("You should use something before `set`")

        column = list(kwargs.keys())[0]
        value: str = list(kwargs.values())[0]
        self._query += f" SET {column} = {f'{column} + {value[6:]}' if value.startswith('column') else value}"
        return self
        

    def select(self, value, from_ = None) -> 'fyCursor':
        self._query = f"SELECT {value}"
        if from_ is not None:
            self._from(from_)
        return self

    def _from(self, table) -> 'fyCursor':
        self._query += f" FROM {table}"
        return self

    def where(self, **kwargs) -> 'fyCursor':
        if not self._query:
            raise ProgrammingError("You should use something before `where`")
        self._query += f" WHERE {list(kwargs.keys())[0]} = {list(kwargs.values())[0]}"
        return self


    def fetch(self, one: bool = False) -> Union[list, tuple[Any], None]:
        """
        fetch values from cursor query
        
        :param one - if `True` provided, the `cursor.fetchone()` function will be used
        """
        if not self._query:
            raise ProgrammingError("Nothing to fetch")
        super().execute(self._query)
        super().connection.commit()
        return super().fetchone() if one else super().fetchall()        


    def one(self) -> Any:
        """
        returns exact one result of fetching, not tuple
        """
        fetching = self.fetch(True)

        if fetching is None:
            return None
        elif type(fetching) in [list, tuple]:
            return fetching[0]
        return fetching


    def commit(self) -> 'fyCursor':
        if self._query:
            super().execute(self._query)
        super().connection.commit()
        return self