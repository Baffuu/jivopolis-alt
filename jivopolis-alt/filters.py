import typing
from .database.sqlitedb import cur
from .misc.constants import BETATEST_MINIMUM_RANK
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

class  RequireBetaFilter(BoundFilter):
    def __init__(self, *args, **kwargs):
        self.is_beta = True

    async def check(self, event) -> bool:
        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={event.from_user.id}").fetchone()[0]
        print("hello")
        return rank > BETATEST_MINIMUM_RANK if self.is_beta else True
