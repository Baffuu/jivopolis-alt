from ..database.functions import cur, conn
from .. import bot, Dispatcher, logger
from ..filters import RequireAdminFilter
from ..misc import constants
from .callbacks import lootbox_button

from aiogram.types import Message

async def sticker_handler(message: Message):
    try:
        match (message.sticker.emoji):
            case '📦':
                return await lootbox_button(message.from_user.id, message)
    except Exception as e:
        logger.exception(e)
        await bot.send_message(message.chat.id, constants.ERROR_MESSAGE.format(e))
    

def register(dp: Dispatcher):
    dp.register_message_handler(sticker_handler, RequireAdminFilter(), content_types=['sticker'])