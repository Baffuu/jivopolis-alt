from .. import bot, Dispatcher, logger
from ..filters import RequireBetaFilter
from ..misc import constants
from ..misc.moder import (
    mute_member, unmute_member, promote_member, demote_member, pin_message
)
from .callbacks import lootbox_button, rob_clan
from ..database import cur
from ..database.functions import cure, shoot
from ..utils import check_user

from aiogram.types import Message
import contextlib


async def sticker_handler(message: Message):
    try:
        count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

        if count == 1 and cur.select("filter_sticker", "clandata").where(
                    clan_id=message.chat.id).one():
            with contextlib.suppress(Exception):
                return await message.delete()

        feature_emojis = ['📦', '🖥', '💊', '🔫']

        if ((message.sticker.emoji in feature_emojis
                or message.chat.type == 'private') and
                not await check_user(message.from_user.id)):
            return

        match (message.sticker.emoji):
            case '📦':
                return await lootbox_button(message.from_user.id, message)
            case '🖥':
                return await rob_clan(message)
            case '⛔':
                if message.reply_to_message:
                    return await mute_member(message)
            case '📣':
                if message.reply_to_message:
                    return await unmute_member(message)
            case '👑':
                if message.reply_to_message:
                    return await promote_member(message)
            case '💥':
                if message.reply_to_message:
                    return await demote_member(message)
            case '📌':
                if message.reply_to_message:
                    return await pin_message(message)
            case '💊':
                if message.reply_to_message:
                    return await cure(
                        message.from_user.id,
                        message.reply_to_message.from_user.id,
                        message.chat.id
                    )
            case '🔫':
                if message.reply_to_message:
                    return await shoot(message)

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
