from typing import Optional

import aiogram

from .database import cur, insert_user
from .misc.config import ADMINS
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
            await self._check_user(
                event.from_user.id, 0, send,
                user=event.from_user, exists=False)
            return not self.is_beta

    async def _check_user(
        self,
        id: int,
        rank: int,
        send: bool,
        reply: Optional[int] = None,
        exists: bool = True,
        user: aiogram.types.User = None
    ):
        if (
            (self.is_beta and rank > BETATEST_MINIMUM_RANK)
            or not self.is_beta
        ):
            return True
        elif id in ADMINS and rank < 2:
            if not exists:
                insert_user(user)
            cur.update("userdata").set(rank=3).where(user_id=id).commit()
            return True

        if send:
            await bot.send_message(
                id,
                "🤵 <i>Доброго дня, сударь. Увы, на данный момент идёт бет"
                "а-тест, поэтому вы не можете использовать данного бота, так "
                "как не являетесь бета-тестером</i>",
                reply_to_message_id=reply
            )
        return False
