import typing
from .database.sqlitedb import cur
from .misc.constants import BETATEST_MINIMUM_RANK
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

class RequireAdminFilter(BoundFilter):
    def __init__(self, *args, **kwargs):
        pass

    async def check(self, message: Message) -> bool:
        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={message.from_user.id}").fetchone()[0]
        return rank > BETATEST_MINIMUM_RANK
