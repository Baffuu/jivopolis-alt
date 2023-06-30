from .. import bot, Dispatcher

from ..database import cur
from ..database.functions import check

from ..misc import OfficialChats

from ..utils import check_user
from aiogram.types import (
    ChatMemberAdministrator, ChatMemberOwner,
    Message
)


async def get_photo_messages(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if not await check_user(user_id):
        return
    await check(message.from_user.id, message.chat.id)

    try:
        process = cur.select("process", "userdata").where(
            user_id=user_id).one()

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

    except TypeError:
        if (
            message.chat.type == "private"
            and message.text.lower() != 'создать персонажа'
        ):
            cur.update("userdata").set(process="login").where(
                user_id=user_id).commit()
        else:
            process = ""

    if process == "setphoto":
        cur.update("userdata").set(photo=message.photo[0].file_id).where(
            user_id=user_id).commit()
        photo = cur.select("photo", "userdata").where(user_id=user_id).one()
        await bot.send_photo(message.chat.id,
                             photo, caption="<i>Ваше фото</i>")
        cur.update("userdata").set(process="").where(
                user_id=user_id).commit()

    if process == "clanphoto":
        count = cur.select("count(*)", "clandata").where(
            group_id=chat_id).one()

        if count == 0:
            return

        if (
            not isinstance(
                await bot.get_chat_member(chat_id, user_id),
                ChatMemberAdministrator
            )
            and not isinstance(
                await bot.get_chat_member(chat_id, user_id),
                ChatMemberOwner
            )
        ):
            return await bot.send_message(
                chat_id,
                "<i>&#10060; У вас недостаточно прав</i>"
            )

        cur.update("clandata").set(photo=message.photo[0].file_id).where(
            group_id=chat_id).commit()

        photo = cur.select("photo", "clandata").where(group_id=chat_id).one()

        await bot.send_photo(
            message.chat.id,
            photo,
            caption="<i>Фото клана</i>"
        )

        cur.update("userdata").set(process="NULL").where(
            user_id=user_id).commit()


def register(dp: Dispatcher):
    dp.register_message_handler(get_photo_messages, content_types=['photo'])
