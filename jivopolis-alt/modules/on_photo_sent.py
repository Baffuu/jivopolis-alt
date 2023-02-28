from ..database.functions import check, cur, InlineKeyboardMarkup, InlineKeyboardButton, Message, bot, conn, SUPPORT_LINK
from aiogram.types import ChatMemberAdministrator, ChatMemberOwner
from aiogram import Dispatcher

async def get_photo_messages(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    await check(message.from_user.id, message.chat.id)

    try:
        process = cur.execute(f"SELECT process FROM userdata WHERE user_id={user_id}").fetchone()[0]
        is_banned = bool(cur.execute(f"SELECT is_banned FROM userdata WHERE user_id = {message.from_user.id}").fetchone()[0])

    except TypeError:
        if message.chat.type == "private" and message.text.lower() != 'создать персонажа':
            cur.execute(f"UPDATE userdata SET process=\"login\" WHERE user_id = {user_id}")
        else:
            process = ""
                
    if is_banned:
        return await bot.send_message(message.from_user.id, f'🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, обратитесь в <a href="{SUPPORT_LINK}">поддержку</a>.')

    if process=="setphoto":
        cur.execute(f"UPDATE userdata SET photo = {message.photo[0].file_id} WHERE user_id = {user_id}")
        conn.commit()

        photo = cur.execute(f"SELECT photo FROM userdata WHERE user_id = {user_id}").fetchone()[0]
        await bot.send_photo(message.chat.id, photo, caption = "<i>Ваше фото</i>", parse_mode = "html")

        cur.execute(f"UPDATE userdata SET process='' WHERE user_id={user_id}")
        conn.commit()

    if process=="clanphoto":
        count = cur.execute(f"SELECT count(*) FROM clandata WHERE group_id = {chat_id}").fetchone()[0]

        if count == 0:
            return

        if not isinstance(await bot.get_chat_member(chat_id, user_id), ChatMemberAdministrator) and not isinstance(await bot.get_chat_member(chat_id, user_id), ChatMemberOwner):
            return await bot.send_message(chat_id, "<i>&#10060; У вас недостаточно прав</i>", parse_mode="html")

        cur.execute(f"UPDATE clandata SET photo={message.photo[0].file_id, chat_id} WHERE group_id={chat_id}")
        conn.commit()

        photo = cur.execute(f"SELECT photo FROM clandata WHERE group_id={chat_id}").fetchone()[0]
        await bot.send_photo(message.chat.id, photo, caption = "<i>Фото клана</i>", parse_mode = "html")

        cur.execute(f"UPDATE userdata SET process='' WHERE user_id={user_id}")
        conn.commit()

def register(dp: Dispatcher):
    dp.register_message_handler(get_photo_messages, content_types=['photo'])