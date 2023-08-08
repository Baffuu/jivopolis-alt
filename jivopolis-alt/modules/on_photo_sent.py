from .. import bot, Dispatcher

from ..database import cur
from ..database.functions import check, get_process

from .callbacks.clans import confirm_clan_photo
from .callbacks.user_profile import confirm_photo

from ..misc import OfficialChats

from ..utils import check_user
from aiogram.types import (
    Message
)

import contextlib


async def get_photo_messages(message: Message):
    user_id = message.from_user.id
    if not await check_user(user_id):
        return
    await check(message.from_user.id, message.chat.id)

    is_banned = bool(
        cur.select("is_banned", "userdata").where(
            user_id=message.from_user.id).one()
    )
    if is_banned:
        return await bot.send_message(
            message.from_user.id,
            f'🧛🏻‍♂️ <i>Вы были забанены в боте. Если вы считаете, что эт'
            'о ошибка, обратитесь в <a href="'
            f'{OfficialChats.SUPPORTCHATLINK}">поддержку</a></i>'
        )

    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1:
        dice = cur.select("filter_photo", "clandata").where(
            clan_id=message.chat.id).one()
        if dice:
            with contextlib.suppress(Exception):
                return await message.delete()

    process = await get_process(user_id)

    if process == "set_photo":
        await confirm_photo(message)
        cur.update("userdata").set(process="").where(
            user_id=user_id).commit()

    elif process == "set_clan_photo":
        await confirm_clan_photo(message)
        cur.update("userdata").set(process="").where(
            user_id=user_id).commit()


async def delete_videos(message: Message):
    count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

    if count == 1:
        dice = cur.select("filter_photo", "clandata").where(
            clan_id=message.chat.id).one()
        if dice:
            with contextlib.suppress(Exception):
                return await message.delete()


def register(dp: Dispatcher):
    dp.register_message_handler(get_photo_messages, content_types=['photo'])
    dp.register_message_handler(delete_videos, content_types=['video'])
