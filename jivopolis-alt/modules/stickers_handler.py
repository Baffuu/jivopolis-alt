from .. import bot, Dispatcher, logger
from ..filters import RequireBetaFilter
from ..misc import constants
from .callbacks import lootbox_button
from ..database import cur

from aiogram.types import Message
import contextlib


async def sticker_handler(message: Message):
    try:
        count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

        if count == 1:
            dice = cur.select("filter_sticker", "clandata").where(
                clan_id=message.chat.id).one()
            if dice:
                with contextlib.suppress(Exception):
                    return await message.delete()

        match (message.sticker.emoji):
            case '📦':
                return await lootbox_button(message.from_user.id, message)
    except Exception as e:
        logger.exception(e)
        await bot.send_message(
            message.chat.id,
            constants.ERROR_MESSAGE.format(e)
        )


def register(dp: Dispatcher):
    dp.register_message_handler(
        sticker_handler,
        RequireBetaFilter(),
        content_types=['sticker']
    )
