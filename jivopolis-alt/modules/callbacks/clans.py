from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from ...database.sqlitedb import cur, conn, insert_clan
from ...bot import bot
from ...misc import get_mask, get_link
from ...config import log_chat

async def create_clan(call: CallbackQuery):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    member = await bot.get_chat_member(chat_id, user_id)

    if not member.is_chat_admin() and not member.is_chat_creator():
        return await bot.send_message(chat_id, '👀 <i>Создать клан может только администратор чата</i>', parse_mode = 'html')
        
    count = cur.execute(f"SELECT count(*) FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]

    if count < 1:
        link = await insert_clan(call.message.chat, call.from_user)
        #await startdef(call.message)
        mask = get_mask(user_id)
        nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id={user_id}").fetchone()[0]
        await bot.send_message(log_chat, f"🏘 #new_clan | <a href='{get_link(user_id)}'>{mask}{nick}</a> создал новый клан: <a href='{link}'>{call.message.chat.title}</a>. <code>[{chat_id}]</code>")
        return await bot.send_message(chat_id, f'<i>🏘 <a href="{get_link(user_id)}">{mask}{nick}</a> создал новый клан. Скорее присоединяйтесь!</i>\n\
        \n<code>🪝 Для дальнейшей настройки клана напишите</code> /start', reply_markup=InlineKeyboardMarkup().\
        add(InlineKeyboardButton('➕ Присоединиться', callback_data='join_clan')))
    else:
        return await bot.send_message(chat_id, '<i>🚥 Такой клан уже существует. Для создания нового сначала удалите старый.</i>')

async def joinclan(call: CallbackQuery, user_id: int):
    chat_id = call.message.chat.id
    
    count = cur.execute(f"SELECT count(*) FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]
    
    mask = get_mask(user_id)
    nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    
    if count < 1:
        return #todo call answer
    elif count > 1:
        raise ValueError("there are more than 1 chat with such id.")

    #cur.execute(f"SELECT clan_type FROM clandata WHERE clan_id={chat_id}").fetchone()[0]
    user_clan = cur.execute(f"SELECT clan_id FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if user_clan != chat_id and user_clan:
        cur.execute(f"UPDATE userdata SET clan_id={chat_id} WHERE user_id={user_id}"); conn.commit()
        return await bot.send_message(chat_id, '<i><b><a href="tg://user?id={2}">{0}{1}</a></b> присоединился к клану</i>'.format(mask, nick, user_id))
    elif user_clan != chat_id:
        cur.execute(f"UPDATE userdata SET clan_id={chat_id} WHERE user_id={user_id}"); conn.commit()
        return await bot.send_message(chat_id, '<i><b><a href="tg://user?id={2}">{0}{1}</a></b> присоединился к клану</i>'.format(mask, nick, user_id)) 
    else:
        cur.execute('UPDATE userdata SET clan=? WHERE user_id=?', (0, a,))
        cur.execute('UPDATE userdata SET clanname=? WHERE user_id=?', ('', a,))
        conn.commit()
        await bot.send_message(chat_id, '<i><b><a href="tg://user?id={2}">{0}{1}</a></b> вышел из клана</i>'.format(mask, nick, user_id), parse_mode = 'html')
            