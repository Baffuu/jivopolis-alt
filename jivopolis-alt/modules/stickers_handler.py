from ..database.functions import cur, conn
from .. import bot, Dispatcher, logger
from .callbacks import lootbox_button

from aiogram.types import Message

async def sticker_handler(message: Message):
    match (message.sticker.emoji):
        case '📦':
            return await lootbox_button(message.from_user.id, message)
    

def register(dp: Dispatcher):
    dp.register_message_handler(sticker_handler, content_types=['sticker'])