import os
import re
import asyncio
import contextlib
import traceback

from . import cur, bot
from .misc.constants import OfficialChats
from aiogram.types import Message, CallbackQuery, Update
from aiogram.utils.exceptions import RetryAfter
from aiogram.utils.text_decorations import HtmlDecoration
from typing import overload, Union, Awaitable, Any, Iterable

DEFAULT_MESSAGE = "🌔"

async def check_user(user_id, is_admin = False) -> bool:
    if not user_exists(user_id):
        with contextlib.suppress(Exception):
            await bot.send_message(user_id, "🧑‍🎨 Сэр, у вас нет аккаунта в живополисе. Прежде чем использовать любые комманды вам нужно зарегистрироваться.") 
        return False

    is_banned = bool(cur.execute(f"SELECT is_banned FROM userdata WHERE user_id = {user_id}").fetchone()[0])

    if is_banned:
        with contextlib.suppress(Exception):
            await bot.send_message(
                user_id, 
                f'🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, обратитесь в <a href="{OfficialChats.SUPPORTCHATLINK}">поддержку</a>.'
            )
        return False

    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    if rank < 2 and is_admin:
        with contextlib.suppress(Exception):
            await bot.send_message(user_id, "👨‍⚖️ Сударь, эта команда доступна только админам.")
        return False
    return True


async def is_allowed_nonick(user_id: int) -> bool:
    if not await check_user(user_id):
        return

    return bool(
        cur.execute(
            f"SELECT nonick_cmds FROM userdata WHERE user_id={user_id}"
        ).fetchone()[0]
    )


def user_exists(user_id: str | int) -> bool:
    """returns `True` if user with such user_id exists, else `False`"""
    return (
        cur.execute(
            f"SELECT count(*) FROM userdata WHERE user_id={user_id}"
        ).fetchone()[0]
        > 0
    )


@overload
async def answer(
    event: Message, 
    message: str = None,
    editable: bool | list = False, 
    edit_sleep: Union[bool, int, float] = 1,
    italise: bool = False,
    reply: bool = False,
    *args, 
    **kwargs
):
    ...

@overload
async def answer(
    event: CallbackQuery, 
    message: str,
    *args, 
    **kwargs
):
    ...

@overload
async def answer(event: Update, *args, **kwargs):
    ...

async def answer(
    event: Union[Message, CallbackQuery, Update],  
    message: str = None,
    editable: Union[bool, list] = False,
    edit_sleep: Union[bool, int, float] = 1,
    reply: bool = False,
    italise: bool = False,
    *args, 
    **kwargs
) -> Union[None, Message, bool]:
    if type(event) is Message:
        return await _answer_message(
            event=event,
            message=message,
            editable=editable,
            reply=reply, 
            edit_sleep=edit_sleep,
            italise = italise,
            **kwargs
        )
    elif type(event) is CallbackQuery:
        return 
        
async def _answer_message(
    event : Message, 
    message, 
    editable, 
    reply, 
    edit_sleep, 
    italise,
    **kwargs
) -> Union[Message, list[Message]]:
    message = await _italise(message) if italise else message
    editable = await _italise(editable) if editable else editable
    print(message)
    if not message and not editable:
        raise AttributeError("You should specify either message or list of messages to be edited")
    elif message and not editable:
        return await event.answer(message, reply, **kwargs)
    else:
        if not message:
            message = DEFAULT_MESSAGE
        messages = [await event.answer(message, reply=reply, **kwargs)]
        await asyncio.sleep(edit_sleep)
        for _message in editable:
            try:
                messages.append(await messages[0].edit_text(_message))
                await asyncio.sleep(edit_sleep)
            except RetryAfter:
                await asyncio.sleep(60)
                messages.append(await messages[0].edit_text(_message))
        return messages


async def _italise(text: str | Iterable[str]):
    if type(text) is not str:
        return [await _italise(item) for item in text]
    return HtmlDecoration().italic(text)


def escape_html(text, /) -> str:
    """
    :param text: Text to escape
    :return: Escaped text
    """
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


line_regex = r'  File "(.*?)", line ([0-9]+), in (.+)'


def format_exception_line(line: str) -> str:
    filename_, lineno_, name_ = re.search(line_regex, line).groups()
    with contextlib.suppress(Exception):
        filename_ = os.path.basename(filename_)
    return (
        f"👉 <code>{escape_html(filename_)}:{lineno_}</code> <b>in</b>"
        f"     <code>{escape_html(name_)}</code>"
    )


def get_trace(e: Exception):
    full_stack = traceback.format_exc().replace(
            "Traceback (most recent call last):\n", ""
        )
    def _code_or_error(line):
        _line = f"<code>{escape_html(line)}</code>"
        return f"\n📛 <b>{escape_html(get_full_class_name(e))}</b>" if line == e.__class__.__name__ else _line

    return "\n".join(
            [
                (
                    format_exception_line(line)
                    if re.search(line_regex, line)
                    else _code_or_error(line)
                )
                for line in full_stack.splitlines()
            ]
        )

def get_full_class_name(object: object):
    module = object.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return object.__class__.__name__
    return f'{module}.{object.__class__.__name__}'
