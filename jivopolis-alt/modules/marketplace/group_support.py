from ... import dp
from typing import Coroutine, Any
from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter


class IsInMarket(BoundFilter):
    def __init__(self) -> None:
        super().__init__()
        self.marketplace_id = None  # todo: implement id from constants

    async def check(self, event: Message) -> Coroutine[Any, Any, bool]:
        return self.marketplace_id == event.chat.id


@dp.message_handler(IsInMarket(), commands=["start"])
async def on_start_pressed(message: Message):
    pass
