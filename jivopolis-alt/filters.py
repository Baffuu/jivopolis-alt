from typing import Optional
from .database import cur
from . import bot
from .misc.constants import BETATEST_MINIMUM_RANK
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import CallbackQuery, Message


class RequireBetaFilter(BoundFilter):
    def __init__(self, *args, **kwargs):
        self.is_beta = True

    async def check(
        self,
        event: Message | CallbackQuery,
        send: bool = True
    ) -> bool:
        try:
            rank = cur.execute(
                f"SELECT rank FROM userdata WHERE user_id={event.from_user.id}"
            ).fetchone()[0]
            if isinstance(event, Message):
                await self._check_user(
                    event.chat.id,
                    rank,
                    send,
                    event.message_id
                )
            elif isinstance(event, CallbackQuery):
                await self._check_user(
                    event.from_user.id,
                    rank,
                    send=send
                )
            return rank >= BETATEST_MINIMUM_RANK if self.is_beta else True
        except TypeError:
            await self._check_user(event.from_user.id, 0, send)
            return not self.is_beta

    async def _check_user(self, id, rank, send, reply: Optional[int] = None):
        if self.is_beta and rank >= BETATEST_MINIMUM_RANK or not self.is_beta:
            return True
        if send:
            await bot.send_message(
                id,
                "🤵 Доброго дня, сударь. Увы, на данный момент идёт бет"
                "а-тест, и вы не можете использовать данного бота так "
                "как не являете бета-тестером.",
                reply_to_message_id=reply
            )
        return False
