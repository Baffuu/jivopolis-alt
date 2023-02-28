from loguru import logger

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text

from ..bot import bot, Dispatcher

from ..database.sqlitedb import cur, conn

from ..config import CREATOR

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
def register(dp: Dispatcher):
    dp.register_message_handler(sqlrun_cmd, Text(startswith=".sqlrun"))