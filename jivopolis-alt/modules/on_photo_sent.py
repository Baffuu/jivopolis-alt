from .. import bot, Dispatcher

from ..database import cur, conn
from ..database.functions import check

from ..misc import OfficialChats

from ..utils import check_user
from aiogram.types import (
    ChatMemberAdministrator, ChatMemberOwner,
    InlineKeyboardMarkup, InlineKeyboardButton,
    Message
)


async def get_photo_messages(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if not await check_user(user_id):
        return
    await check(message.from_user.id, message.chat.id)

    try:
        process = cur.execute("SELECT process FROM userdata WHERE"
                              f" user_id={user_id}").fetchone()[0]
        is_banned = bool(cur.execute("SELECT is_banned FROM userdata WHERE "
                                     f"user_id = {message.from_user.id}"
                                     ).fetchone()[0])
        if is_banned:
            return await bot.send_message(message.from_user.id,
                                          '🧛🏻‍♂️ <i>Вы были забанены в боте. '
                                          'Если вы считаете, что это ошибка, '
                                          'обратитесь в <a href="'
                                          f'{OfficialChats.SUPPORTCHATLINK}">'
                                          'поддержку</a></i>')

    except TypeError:
        if (
            message.chat.type == "private"
            and message.text.lower() != 'создать персонажа'
        ):
            cur.execute("UPDATE userdata SET process=\"login\" WHERE"
                        f" user_id = {user_id}")
        else:
            process = ""

    if process == "setphoto":
        cur.execute(f"UPDATE userdata SET photo = {message.photo[0].file_id}"
                    f" WHERE user_id = {user_id}")
        conn.commit()

        photo = cur.execute("SELECT photo FROM userdata WHERE"
                            f" user_id = {user_id}").fetchone()[0]
        await bot.send_photo(message.chat.id,
                             photo, caption="<i>Ваше фото</i>")

        cur.execute(f"UPDATE userdata SET process='' WHERE user_id={user_id}")
        conn.commit()

    if process == "clanphoto":
        count = cur.execute("SELECT count(*) FROM clandata WHERE"
                            f" group_id = {chat_id}").fetchone()[0]

        if count == 0:
            return

        if not isinstance(await bot.get_chat_member(chat_id, user_id),
                          ChatMemberAdministrator) and not isinstance(
                await bot.get_chat_member(chat_id, user_id),
                ChatMemberOwner):
            return await bot.send_message(chat_id,
                                          "<i>&#10060; У вас недостаточно "
                                          "прав</i>")

        cur.execute("UPDATE clandata SET photo="
                    f"{message.photo[0].file_id, chat_id} WHERE"
                    f" group_id={chat_id}")
        conn.commit()

        photo = cur.execute("SELECT photo FROM clandata WHERE"
                            f" group_id={chat_id}").fetchone()[0]
        await bot.send_photo(message.chat.id, photo,
                             caption="<i>Фото клана</i>")

        cur.execute(f"UPDATE userdata SET process='' WHERE user_id={user_id}")
        conn.commit()


def register(dp: Dispatcher):
    dp.register_message_handler(get_photo_messages, content_types=['photo'])
