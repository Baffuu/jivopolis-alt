import contextlib
import sqlite3

from ..filters import  RequireBetaFilter
from .. import bot, Dispatcher, logger

from ..database.sqlitedb import cur, conn
from ..database.functions import get_link, check

from ..misc import OfficialChats, ITEMS, check_user
from ..misc.config import SUPPORT_LINK

from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram.utils.deep_linking import encode_payload
from aiogram.utils.exceptions import MessageIsTooLong
async def sqlrun_cmd(message: Message) -> None:
    try:
        if not await check_user(message.from_user.id, True):
             return
        args = message.text[8:]
        if args.startswith("SELECT"):
            logger.info(f"someone catch data with SELECT: {args}")
            return await message.reply(cur.execute(args).fetchone())

        approve_cmds = ["select", "update", "set", "delete", "alter", "drop", "insert", "replace"] #команды, которые запрашивают одобрение мега-администрации

        for request in args.split(' '):
            approve_request = request.lower() in approve_cmds
        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={message.from_user.id}").fetchone()[0]
        if approve_request and rank < 3:
            cur.execute(f"UPDATE userdata SET sql='{request}' WHERE user_id={message.from_user.id}")
            conn.commit()

            await message.answer(
                "<i>🪐 Запрос отправлен мега-админам на проверку. Вам придётся подождать, пока кто-нибудь примет или отклонит запрос.\n"
                "\n❗️При повторной отправке любого другого запроса текущий будет стёрт.</i>"
            )

            await bot.send_message(
                OfficialChats.MEGACHAT, 
                (
                    f"<i><a href=\"tg://user?id={message.from_user.id}\">{message.from_user.full_name}</a> хочет выполнить запрос:\n"
                    f"\n<code>{request}</code></i>",
                ),
                reply_markup=InlineKeyboardMarkup(row_width=1).\
                    add(
                        InlineKeyboardButton(text="🔰 Подтвердить", callback_data=f"sqlrun:approve:{message.from_user.id}"), 
                        InlineKeyboardButton(text="📛 Отклонить", callback_data=f"sqlrun:decline:{message.from_user.id}")
                    )
            )

        elif args.lower().startswith("select") and rank < 3:
            cur.execute(args)

            values = ''

            for row in cur.fetchall():
                for raw in row:
                    values += "\n" + str(raw)

            if values == '':
                values = 'None'

            return await message.answer(f"<i><b>🧑‍🔧 SQLRun вернуло следующие значения: \n</b>{values}</i>")
        elif rank > 2:
            cur.execute(args)
            conn.commit()   
            if values := cur.fetchall():
                try:
                    await message.reply(f"<i><b>🧑‍🔧 SQLRun вернуло следующие значения: \n</b><code>{values}</code></i>")
                except MessageIsTooLong:
                    await message.reply(f"<i><b>🧑‍🔧 SQLRun вернуло следующие значения: \n</b><code>{values[:3800]}</code></i>")
                    await message.reply(values[3800:])
                return logger.success(
                    (
                        f"🪿 SQLQ was executed: {args}\n"
                        f">>> {values}"
                    )
                )
            await message.reply('🧑‍🔧 sql cmd executed')         
            return logger.success(
                (
                    f"🐦‍⬛ SQLQ was executed: {args}\n"
                    ">>> `nothing was returned`"
                )
            )

    except Exception as e:
        await message.answer(f"<i><b>something went wrong: </b>{e}</i>")


async def globan_cmd(message: Message) -> None:    
    if not await check_user(message.from_user.id, True):
        return

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
        await bot.send_message(OfficialChats.LOGCHAT, f'👨‍🔬 Аккаунт <a href ="tg://user?id={args}>пользователя</a> насильно создан. | <a href="tg://user?id={message.from_user.id}>{admin_nick}</a>')

    cur.execute(f"UPDATE userdata SET is_banned=True WHERE user_id={args}")
    conn.commit()

    await bot.send_message(message.chat.id, f'🥷 <a href="{await get_link(args)}">{user_nick}</a> [<code>id: {args}</code>] был успешно забанен. | <a href = "{await get_link(message.from_user.id)}">{admin_nick}</a>')
    await bot.send_message(OfficialChats.LOGCHAT, f'🥷 <a href="{await get_link(args)}">{user_nick}</a> [<code>id: {args}</code>] был успешно забанен. | <a href = "{await get_link(message.from_user.id)}">{admin_nick}</a>')


async def getall_cmd(message: Message) -> None:
    if not await check_user(message.from_user.id, True):
        return

    await message.reply('🧬 Loading...')

    for item in ITEMS:
        with contextlib.suppress(sqlite3.OperationalError):
            cur.execute(f"UPDATE userdata SET {item}={item}+1 WHERE user_id={message.from_user.id}"); conn.commit()
    await message.reply('🪄 Я дал вам все предметы в Живополисе')


async def execute_cmd(message: Message):
    if not await check_user(message.from_user.id, True):
        return
    exec(message.text.replace('.exec ', ''))
    await message.reply("🪼 Executed succesfully")


async def evaluate_cmd(message: Message):
    if not await check_user(message.from_user.id, True):
        return
    if message.text.startswith('.evaluate'):
        text = message.text.replace(".evaluate", '')
    elif message.text.startswith('.eval'):
        text = message.text.replace('.eval', '')
    elif message.text.startswith('.e'):
        text = message.text.replace('.e', '')    
    
    result = eval(text)
    await message.reply(f"🦑 RESULT: {result}")


def register(dp: Dispatcher):
    dp.register_message_handler(sqlrun_cmd, Text(startswith=".sqlrun"),  RequireBetaFilter())
    dp.register_message_handler(globan_cmd, Text(startswith='.globan'),  RequireBetaFilter())
    dp.register_message_handler(getall_cmd, Text(startswith='.getall'),  RequireBetaFilter())
    dp.register_message_handler(execute_cmd, Text(startswith='.exec'),  RequireBetaFilter())
    dp.register_message_handler(evaluate_cmd, Text(startswith=['.eval', '.e']), RequireBetaFilter())