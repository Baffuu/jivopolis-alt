from .marketplace import market
from .constants import MAX_KEYBOARD_LENGTH, GROUP_ID, ROW_WIDTH
from ...filters import RequireBetaFilter

from typing import Coroutine, Any
from aiogram import Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import BoundFilter


class IsInMarket(BoundFilter):
    def __init__(self) -> None:
        super().__init__()
        self.marketplace_id = GROUP_ID

    async def check(self, event: Message) -> Coroutine[Any, Any, bool]:
        return self.marketplace_id == event.chat.id


async def on_start_pressed(message: Message):
    markup = InlineKeyboardMarkup(row_width=ROW_WIDTH)

    buttons = []
    for product in market.get_all():
        if len(buttons) > MAX_KEYBOARD_LENGTH:
            break
        buttons.append(
            InlineKeyboardButton(
                f"{product.item.emoji} {product.cost}",
                callback_data=f"product_info_{product.id}"
            )
        )

    await message.reply("🕸️ WELCOME", reply_markup=markup.add(*buttons))


def register(dp: Dispatcher):
    dp.register_message_handler(
        on_start_pressed,
        IsInMarket(),
        RequireBetaFilter(),
        commands=["start"]
    )
