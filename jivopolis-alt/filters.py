import typing
from .database import cur
from .misc.constants import BETATEST_MINIMUM_RANK
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import CallbackQuery, Message

class RequireBetaFilter(BoundFilter):
    def __init__(self, *args, **kwargs):
        self.is_beta = False

    async def check(self, event: Message | CallbackQuery) -> bool:
        try:
            rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={event.from_user.id}").fetchone()[0]
            return rank > BETATEST_MINIMUM_RANK if self.is_beta else True
        except TypeError:
            return not self.is_beta
