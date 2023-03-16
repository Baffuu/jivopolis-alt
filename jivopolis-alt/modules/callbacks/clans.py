from aiogram.types import CallbackQuery
from ...database.sqlitedb import cur, conn
from ...bot import bot
from ...misc import get_mask, get_link


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
            