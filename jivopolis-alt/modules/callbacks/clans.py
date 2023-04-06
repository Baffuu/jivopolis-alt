from ... import bot
from ...misc import OfficialChats

from ...misc import get_mask, get_link
from ...database.sqlitedb import cur, conn, insert_clan

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

async def create_clan(call: CallbackQuery) -> None:
    '''
    Callback for clan creating. 
    
    :param call - callback:
    '''
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    member = await bot.get_chat_member(chat_id, user_id)

    if (
        not member.is_chat_admin() 
        and not member.is_chat_creator()
    ):
        return await bot.send_message(chat_id, '👀 <i>Создать клан может только администратор чата</i>')
        
    count = cur.execute(f"SELECT count(*) FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]

    if count < 1:
        link = await insert_clan(call.message.chat, call.from_user)
        #await startdef(call.message)
        mask = get_mask(user_id)
        nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id={user_id}").fetchone()[0]
        await bot.send_message(
            OfficialChats.LOGCHAT, 
            text=(
                f"🏘 #new_clan | <a href='{get_link(user_id)}'>{mask}{nick}</a>"
                f" создал новый клан: <a href='{link}'>{call.message.chat.title}</a>. <code>[{chat_id}]</code>"
            )
        )
        return await bot.send_message(
            chat_id, 
            text = (
                f"<i>🏘 <a href='{get_link(user_id)}'>{mask}{nick}</a> создал новый клан. Скорее присоединяйтесь!</i>"
                "\n<code>🪝 Для дальнейшей настройки клана напишите</code> /start"
            ), 
            reply_markup=InlineKeyboardMarkup().\
                add(InlineKeyboardButton('➕ Присоединиться', callback_data='join_clan'))
        )
    else:
        return await bot.send_message(chat_id, '<i>🚥 Такой клан уже существует. Для создания нового сначала удалите старый.</i>')


async def joinclan(call: CallbackQuery, user_id: int) -> None:
    '''
    Callback for clan joining
    
    :param call - callback:
    :param user_id:
    '''
    chat_id = call.message.chat.id

    count = cur.execute(f"SELECT count(*) FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]

    if count < 1:
        return call.answer("😓 Похоже, такого клана не существует.", show_alert=True)
    elif count > 1:
        raise ValueError("found more than one clan with such ID")

    mask = get_mask(user_id)
    nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    user_clan = cur.execute(f"SELECT clan_id FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if user_clan != chat_id and user_clan:
        cur.execute(f"UPDATE userdata SET clan_id={chat_id} WHERE user_id={user_id}"); conn.commit()
        return await bot.send_message(
            chat_id, 
        f'<i><b><a href="{get_link(user_id)}">{mask}{nick}</a></b> присоединился к клану</i>')
    else:
        cur.execute(f"UPDATE userdata SET clan_id=NULL WHERE user_id={user_id}")
        conn.commit()
        await bot.send_message(chat_id, f"<i><b><a href=\"tg://user?id={2}\">{0}{1}</a></b> вышел из клана</i>".format(mask, nick, user_id))
            