from .. import bot, Dispatcher, logger
from ..filters import RequireBetaFilter
from ..misc import constants
from ..misc.moder import mute_member, unmute_member
from .callbacks import lootbox_button, rob_clan
from ..database import cur
from ..utils import check_user

from aiogram.types import Message
import contextlib


async def sticker_handler(message: Message):
    try:
        count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

        if count == 1:
            filter = cur.select("filter_sticker", "clandata").where(
                clan_id=message.chat.id).one()
            if filter:
                with contextlib.suppress(Exception):
                    return await message.delete()

        feature_emojis = ['📦', '🖥']

        if message.sticker.emoji in feature_emojis or \
                message.chat.type == 'private':
            if not await check_user(message.from_user.id):
                return

        match (message.sticker.emoji):
            case '📦':
                return await lootbox_button(message.from_user.id, message)
            case '🖥':
                return await rob_clan(message)
            case '⛔':
                return await mute_member(message)
            case '📣':
                return await unmute_member(message)

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
