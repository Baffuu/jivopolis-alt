from loguru import logger

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text

from ..bot import bot, Dispatcher

from ..database.sqlitedb import cur, conn, encode_payload
from ..database.functions import get_link
from ..config import CREATOR, log_chat

async def sqlrun_cmd(message: Message):
    try:
        msg = message.text[8:]
        if msg.startswith("SELECT"):
            logger.info(f"someone catch data with SELECT: {msg}")
            message.reply(cur.execute(msg).fetchone())
        cur.execute(msg)
        conn.commit()            
        return logger.success(f"SQL command was runned: {msg}")
    
        '''
        request=message.text[8:].replace("<concat>", "||")
        a = message.from_user
        try:
            cur.execute("SELECT rank FROM userdata WHERE user_id=?", (a.id,))
            rang = cur.fetchone()[0]
        except:
            return
        if rang<2:
            return
        rec = request.lower().replace(";", "").split(" ")
        if not "update" in rec and not "set" in rec and not "delete" in rec and not "alter" in rec and not "drop" in rec and not "insert" in rec and not "replace" in rec:
            try:
                cur.execute(request)
                conn.commit()
                try:
                    rval = ""
                    for row in cur.fetchall():
                        for raw in row:
                            rval = rval+"\n"+str(raw)
                    await message.answer("<i><b>Значения: \n</b>{0}</i>".format(rval), parse_mode="html")
                except Exception as e:
                    await message.answer("<i><b>Произошла незначительная ошибка при обработке запроса:</b> {0}</i>".format(e), parse_mode="html")
                    await message.answer("<i>Запрос обработан</i>", parse_mode="html")
            except Exception as e:
                await message.answer("<i><b>Запрос не обработан: \n</b>{0}</i>".format(e), parse_mode = "html")
            return
        cur.execute("UPDATE userdata SET sql=? WHERE user_id=?", (request, a.id,))
        conn.commit()
        await message.answer("<i>Ваш запрос отправлен создателю бота на проверку. Если запрос не содержит код, вредящий базе данных, создатель одобрит код и вы получите результат.\n\n<b>Помните:</b> пока ваш запрос не будет одобрен или отклонён, вы не сможете отправить другой запрос</i>", parse_mode="html")
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text="✅ Подтвердить", callback_data="approve {0}".format(a.id)))
        markup.add(InlineKeyboardButton(text="❌ Отклонить", callback_data="reject {0}".format(a.id)))
        await bot.send_message(CREATOR, "<i><a href=\"tg://user?id={0}\">{1}{2}</a> хочет выполнить запрос:\n\n<code>{3}</code></i>".format(a.id, a.first_name, " "+a.last_name if a.last_name!=None else "", request), reply_markup=markup)
       '''
    except Exception as e:
        await message.answer("<i><b>Текст ошибки: </b>{0}</i>".format(e), parse_mode = "html")

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
        args = message.get_args()

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