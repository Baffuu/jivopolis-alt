from loguru import logger

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text

from ..bot import bot, Dispatcher

from ..database.sqlitedb import cur, conn, encode_payload
from ..database.functions import get_link
from ..config import log_chat, MEGACHAT, ADMINS, SUPPORT_LINK

async def sqlrun_cmd(message: Message):
    try:
        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={message.from_user.id}").fetchone()[0]
        is_banned = bool(cur.execute(f"SELECT is_banned FROM userdata WHERE user_id = {message.from_user.id}").fetchone()[0])
    except TypeError:
        return await message.reply('🧑‍🎨 Сэр, у вас нет аккаунта в живополисе. Прежде чем использовать любые комманды вам нужно зарегистрироваться.')
    try:
        args = message.text[8:]

        if is_banned:
            return await bot.send_message(message.from_user.id, f'🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, обратитесь в <a href="{SUPPORT_LINK}">поддержку</a>.')

        if rank < 2:
            return await message.reply("👨‍⚖️ Сударь, эта команда доступна только админам.")

        if args.startswith("SELECT"):
            logger.info(f"someone catch data with SELECT: {args}")
            return await message.reply(cur.execute(args).fetchone())

        approve_cmds = ["select", "update", "set", "delete", "alter", "drop", "insert", "replace"] #команды, которые запрашивают одобрение мега-администрации
        
        for request in args.split(' '):
            if request.lower() in approve_cmds:
                approve_request = True

        if approve_request and rank < 3:
            cur.execute(f"UPDATE userdata SET sql='{request}' WHERE user_id={message.from_user.id}")
            conn.commit()

            await message.answer("<i>🪐 Запрос отправлен мега-админам на проверку. Вам придётся подождать, пока кто-нибудь примет или отклонит запрос.\n\
                \n❗️При повторной отправке любого другого запроса текущий будет стёрт.</i>", parse_mode="html")

            await bot.send_message(MEGACHAT, f"<i><a href=\"tg://user?id={message.from_user.id}\">{message.from_user.full_name}</a> хочет выполнить запрос:\n\
                                \n<code>{request}</code></i>", reply_markup=InlineKeyboardMarkup(row_width=1).\
                                add(InlineKeyboardButton(text="🔰 Подтвердить", callback_data=f"sqlrun:approve:{message.from_user.id}"), 
                                InlineKeyboardButton(text="📛 Отклонить", callback_data=f"sqlrun:reject:{message.from_user.id}")))
  
        elif args.lower().startswith("select"):
            cur.execute(args)

            values = ''

            for row in cur.fetchall():
                for raw in row:
                    values += "\n" + str(raw)

            if values == '':
                values = 'None'

            return await message.answer(f"<i><b>🧑‍🔧 SQLRun вернуло следующие значения: \n</b>{values}</i>", parse_mode="html")
        elif rank > 2:
            cur.execute(args)
            conn.commit()   
            await message.reply('🧑‍🔧 sql cmd executed')         
            return logger.success(f"SQL Query: {args}")
    
    except Exception as e:
        await message.answer(f"<i><b>something went wrong: </b>{e}</i>", parse_mode = "html")

async def globan_cmd(message: Message):    
    try:
        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id = {message.from_user.id}").fetchone()[0]
        is_banned = bool(cur.execute(f"SELECT is_banned FROM userdata WHERE user_id = {message.from_user.id}").fetchone()[0])
    except TypeError:
        return message.reply("🧑‍🎨 Сэр, у вас нет аккаунта в живополисе. Прежде чем использовать любые комманды вам нужно зарегистрироваться.")
    
    if is_banned:
        return bot.send_message(message.from_user.id, f'🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, обратитесь в <a href="{SUPPORT_LINK}">поддержку</a>.')

    if rank < 2:
        return message.reply("👨‍⚖️ Сударь, эта команда доступна только админам.")
    
    else:
        args = message.text[7:]

        if args == '':
            return message.reply("🕵🏿‍♂️ Не хватает аргументов.")
        
        try:
            user_nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id = '{args}'").fetchone()[0]
            admin_nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id={message.from_user.id}").fetchone()[0]
        except TypeError:
            user_nick = 'user'
            cur.execute(f"INSERT INTO userdata(user_id, nickname, login_id) VALUES ({args}, 'banned_user', \"{encode_payload(args)}\"")
            await bot.send_message(message.chat.id, f'👨‍🔬 Аккаунт <a href ="tg://user?id={args}>пользователя</a> насильно создан. | <a href="tg://user?id={message.from_user.id}>{admin_nick}</a>')
            await bot.send_message(log_chat, f'👨‍🔬 Аккаунт <a href ="tg://user?id={args}>пользователя</a> насильно создан. | <a href="tg://user?id={message.from_user.id}>{admin_nick}</a>')
        
        cur.execute(f"UPDATE userdata SET is_banned=True WHERE user_id={args}")
        conn.commit()

        await bot.send_message(message.chat.id, f'🥷 <a href="{get_link(args)}">{user_nick}</a> [<code>id: {args}</code>] был успешно забанен. | <a href = "{get_link(message.from_user.id)}">{admin_nick}</a>')
        await bot.send_message(log_chat, f'🥷 <a href="{get_link(args)}">{user_nick}</a> [<code>id: {args}</code>] был успешно забанен. | <a href = "{get_link(message.from_user.id)}">{admin_nick}</a>')

def register(dp: Dispatcher):
    dp.register_message_handler(sqlrun_cmd, Text(startswith=".sqlrun"))
    dp.register_message_handler(globan_cmd, Text(startswith='.globan'))