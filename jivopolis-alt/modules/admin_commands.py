import contextlib
import sqlite3

from ..filters import RequireBetaFilter
from .. import bot, dp, Dispatcher, logger, utils

from ..database import cur, conn

from ..misc import OfficialChats, ITEMS, get_embedded_link, tglog, get_link
from ..utils import check_user
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram.utils.deep_linking import encode_payload
from aiogram.utils.exceptions import MessageIsTooLong


class sqlrun():
    async def cmd(self, message: Message) -> None:
        try:
            if not await check_user(message.from_user.id, True):
                return

            args = message.text[8:]

            if args.startswith("SELECT"):
                logger.info(f"someone catch data with SELECT: {args}")
                await message.reply(cur.execute(args).fetchone())
                return

            approve_request, request, rank = self._check_request(
                message, args)

            if approve_request and rank < 3:
                assert request is not None
                cur.update("userdata").set(sql=request).where(
                    user_id=message.from_user.id).commit()

                await message.answer(
                    "<i>🪐 Query's been sent to megaadmins for a review. "
                    "You'll have to wait until one of them approves or decline"
                    "s it.\n\n❗️If you make a new SQL query, the current one "
                    "will be vanished</i>"
                )

                await bot.send_message(
                    OfficialChats.MEGACHAT,
                    (
                        f"<i><a href=\"tg://user?id={message.from_user.id}\""
                        f">{message.from_user.full_name}</a> wants to make an "
                        f"SQL query:\n\n<code>{request}</code></i>"
                    ),
                    reply_markup=InlineKeyboardMarkup(row_width=1).add(
                            InlineKeyboardButton(
                                text="🔰 Approve",
                                callback_data=(
                                    f"sqlrun:approve:{message.from_user.id}"
                                )
                            ),
                            InlineKeyboardButton(
                                text="📛 Decline",
                                callback_data=(
                                    f"sqlrun:decline:{message.from_user.id}"
                                )
                            )
                        )
                )

            elif args.lower().startswith("select") and rank > 2:
                return await self._return_values(message, args)

            else:
                await message.reply('🧑‍🔧 sql cmd executed')
                cur.execute(args).commit()
                return logger.success(
                    (
                        f"🐦‍⬛ SQLQ was executed: {args}\n"
                        ">>> `nothing was returned`"
                    )
                )

        except Exception as e:
            await message.answer(
                "<b>🧯 <i>ERROR WHILE SQLQ:</i>\n\n:"
                f"{utils.get_full_class_name(e)}</b>\n<code>{e}</code>"
            )

    def _check_request(self, message: Message, args: str):
        approve_cmds = [
            "select",
            "update",
            "set",
            "delete",
            "alter",
            "drop",
            "insert",
            "replace"
        ]  # commands requiring mega admin approval

        approve_request = False
        request = None

        for request in args.split(' '):
            approve_request = request.lower() in approve_cmds

            if approve_request:
                break

        rank = cur.select("rank", "userdata").where(
                user_id=message.from_user.id).one()

        return approve_request, request, rank

    async def _return_values(self, message: Message, query: str) -> None:
        cur.execute(query)
        conn.commit()

        if values := cur.fetchall():

            values = str(values)

            try:
                await message.reply(
                    f"🪿 SQLQ was executed: {query}\n"
                    f">>> <i>{values}</i>"
                )
            except MessageIsTooLong:
                await message.reply(
                    f"🪿 SQLQ was executed: {query}\n"
                    f">>> <i>{values[:3800]}</i>"
                )
                try:
                    await message.reply(f"<i>{values[3800:]}</i>")
                except MessageIsTooLong:
                    await message.reply("🪿 Too many symbols")
            return logger.success(
                (
                    f"🪿 SQLQ was executed: {query}\n"
                    f">>> {values}"
                )
            )


async def batch_cmd(message: Message):
    '''
    .batch command adds certain columns to userdata (or specified table)
    '''
    user_id = message.from_user.id
    rank = cur.select("rank", "userdata").where(user_id=user_id).one()
    if rank < 3:
        return
    command = message.text.split('\n')[0]
    if command.startswith(".batch:"):
        table = command.replace(".batch:", "")
    else:
        table = "userdata"
    columns = message.text.lower().split('\n')[1:]
    text = f"<i>Adding columns to <b>{table}...</b>"
    for column in columns:
        try:
            cur.execute(
                f"ALTER TABLE {table} ADD {column} INTEGER DEFAULT 0 NOT NULL"
            ).commit()
            result = f"😃 Successfully added column <b>{column}</b>."
        except Exception as e:
            if "duplicate column name" in str(e):
                result = f"🤨 Column <b>{column}</b> already exists."
            else:
                result = f"😪 Couldn't add <b>{column}</b>: <code>{e}</code>."
        text += f"\n\n{result}"
    text += "\n\n💨 Adding columns completed. Don't forget to add those " +\
            "columns to the table creation query if you haven't yet!</i>"
    await message.answer(
        text, reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="🤔 Okay",
                callback_data="cancel_action"
            )
        )
    )


async def globan_cmd(message: Message):
    if not await check_user(message.from_user.id, True):
        return

    args = message.text[7:]

    if args == '':
        return await message.reply("🕵🏿‍♂️ Не хватает аргументов.")

    admin_nick = cur.select("nickname", "userdata").where(
        user_id=message.from_user.id).one()
    count = cur.select("count(*)", "userdata").where(user_id=args).one()
    user_nick = cur.select("nickname", "userdata").where(user_id=args).one()

    if count < 1:
        user_nick = 'user'
        cur.execute(f"""
            INSERT INTO userdata(user_id, nickname, login_id)
            VALUES ({args}, 'banned_user', "{encode_payload(args)}"
        """)
        await bot.send_message(
            message.chat.id,
            f'<i>👨‍🔬 Account of a <a href ="tg://user?id={args}>user</a> '
            'was created successfully. | <a href="tg://user?id='
            f'{message.from_user.id}>{admin_nick}</a></i>'
        )
        await tglog(
            f'👨‍🔬 Аккаунт <a href ="tg://user?id={args}">пользователя</a> '
            'насильно создан. | <a href="tg://user?id='
            f'{message.from_user.id}>{admin_nick}</a>',
            "#account_created_by_admin"
        )

    cur.execute(f"UPDATE userdata SET is_banned=True WHERE user_id={args}")
    conn.commit()

    await bot.send_message(
        message.chat.id,
        f'🥷 <a href="{await get_link(args)}">{user_nick}</a> [<code>id: '
        f'{args}</code>] has been successfully banned. | <a href = '
        f'"{await get_link(message.from_user.id)}">{admin_nick}</a>'
    )
    await tglog(
        f'🥷 <a href="{await get_link(args)}">{user_nick}</a> [<code>id: '
        f'{args}</code>] был успешно забанен. | <a href = '
        f'"{await get_link(message.from_user.id)}">{admin_nick}</a>',
        "#globan"
    )


async def getall_cmd(message: Message) -> None:
    if not await check_user(message.from_user.id, True):
        return

    await message.reply('🧬 Loading...')

    args = message.get_args()
    args = 1 if args is None else args

    for item in ITEMS:
        with contextlib.suppress(sqlite3.OperationalError):
            cur.update("userdata").add(**{item: args}).where(
                user_id=message.from_user.id).commit()
    await message.reply("<i>🪄 I've given you all items in Jivopolis</i>")


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
    else:
        text = None

    assert text is not None

    result = eval(text)
    await message.reply(f"🦑 RESULT: {result}")


def _raise(error: Exception):
    raise error


@dp.message_handler(
    Text(
        startswith=['/update', '.update'],
        ignore_case=True
    ),
    RequireBetaFilter()
)
async def update_cmd(message: Message):
    args = message.text.split(" ", maxsplit=3)
    _user_id = args[1]

    if _user_id == "self":
        _user_id = message.from_user.id
    elif _user_id == "reply":
        if not message.reply_to_message:
            raise ValueError("No reply message.")

        _user_id = message.reply_to_message.from_user.id
    try:
        int(_user_id)
    except ValueError:
        assert isinstance(_user_id, str)

        _adv_args = _user_id.split(':', maxsplit=2)
        _user_id = cur.select("user_id", "userdata").where(
            **{_adv_args[0]: _adv_args[1]}).one()

        _user_id = _user_id if _user_id is not None else _raise(
            ValueError("user with this param's does not exists."))

    column = args[2]
    new_value = args[3]
    user_id = message.from_user.id

    if not await check_user(user_id, True):
        return

    if column in ['user_id']:
        return await message.answer('&#10060; <i>СЛЫШЬ, ЭТО МЕНЯТЬ НЕЛЬЗЯ!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!</i>') # noqa

    _old_value = cur.select(column, "userdata").where(user_id=_user_id).one()
    cur.update("userdata").set(**{column: new_value}).where(
        user_id=_user_id).commit()
    _new_value = cur.select(column, "userdata").where(user_id=_user_id).one()

    await message.reply(
        (
            f"<i>🚀 Вы обновляете столбец <code>{column}</code> игрока "
            f"{await get_embedded_link(_user_id)}</i>"
            "\n>>> ☁️ старое значение: <code>"
            f"{_old_value or 'NULL'}</code>"
            "\n>>> ✨ новое значение: <code>"
            f"{_new_value or 'NULL'}</code>"
        )
    )

    await tglog(
        (
            f"<i>🚀 {await get_embedded_link(user_id)} обновляет столбец"
            f" <code>{column}</code> игрока "
            f"{await get_embedded_link(_user_id)}</i>"
            "\n>>> ☁️ старое значение: <code>"
            f"{_old_value or 'NULL'}</code>"
            "\n>>> ✨ новое значение: <code>"
            f"{_new_value or 'NULL'}</code>"
            f"\n\n<code>{message.text.lower()}</code>"
        ),
        "#update_cmd"
    )


@dp.message_handler(
    Text(
        startswith=['.select', '/select']
    ),
    RequireBetaFilter()
)
async def select_cmd(message: Message):
    args = message.text.lower().split(" ")
    _user_id = args[1]
    if _user_id == "self":
        _user_id = message.from_user.id
    try:
        int(_user_id)
    except ValueError:
        assert isinstance(_user_id, str)

        _adv_args = _user_id.split(':', maxsplit=2)
        _user_id = cur.select("user_id", "userdata").where(
            **{_adv_args[0]: _adv_args[1]}).one()

        _user_id = _user_id[0] if _user_id is not None else _raise(
            ValueError("user with this params does not exists."))
    user_id = message.from_user.id
    column = args[2]

    if not await check_user(user_id, True):
        return

    result = cur.select(column, "userdata").where(user_id=_user_id).one()
    await message.answer(
        (
            "🌪 Вы захватываете данные пользователя "
            f"{await get_embedded_link(user_id)}"
            f"\n>>> <code>{column}</code>: <code>"
            f"{result if result is not None else 'NULL'}</code>"
        )
    )

    await tglog(
        (
            f"🌪 {await get_embedded_link(user_id)} захватывает данные"
            f" пользователя {await get_embedded_link(user_id)}"
            f"\n>>> <code>{column}</code>: <code>"
            f"{result[0] if result else 'NULL'}</code>"
            f"\n\n<code>{message.text.lower()}</code>"
        ),
        "#select_cmd"
    )


def register(dp: Dispatcher):
    dp.register_message_handler(
        sqlrun().cmd,
        Text(startswith=".sqlrun"),
        RequireBetaFilter()
    )
    dp.register_message_handler(
        globan_cmd,
        Text(startswith='.globan'),
        RequireBetaFilter()
    )
    dp.register_message_handler(
        getall_cmd,
        Text(startswith='.getall'),
        RequireBetaFilter()
    )
    dp.register_message_handler(
        execute_cmd,
        Text(startswith='.exec'),
        RequireBetaFilter()
    )
    dp.register_message_handler(
        evaluate_cmd,
        Text(startswith=['.eval', '.e']),
        RequireBetaFilter()
    )
