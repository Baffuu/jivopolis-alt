import os
import re
import time
import asyncio
import contextlib
import traceback

from datetime import timedelta
from . import cur, bot, init_ts
from .misc.constants import OfficialChats
from aiogram.types import Message, CallbackQuery, Update
from aiogram.utils.exceptions import RetryAfter
from aiogram.utils.text_decorations import HtmlDecoration
from typing import Union, Iterable, Coroutine, Optional, Any

from .misc import current_time

DEFAULT_MESSAGE = "🌔"
DEFAULT_SLEEP = 5


async def check_user(user_id: int | str, is_admin: bool = False) -> bool:
    if not user_exists(user_id):
        with contextlib.suppress(Exception):
            await bot.send_message(
                user_id,
                "🧑‍🎨 <i>Сэр, у вас нет аккаунта в Живополисе. Прежде чем"
                " использовать любые команды, вам нужно зарегистрироваться</i>"
            )
        return False

    is_banned = bool(cur.execute(
        f"SELECT is_banned FROM userdata WHERE user_id = {user_id}"
    ).fetchone()[0])

    if is_banned:
        with contextlib.suppress(Exception):
            await bot.send_message(
                user_id,
                '🧛🏻‍♂️ <i>Вы были забанены в боте. Если вы считаете, что это '
                'ошибка, обратитесь в <a href='
                f'"{OfficialChats.SUPPORTCHATLINK}">поддержку</a></i>'
            )
        return False

    in_prison = cur.select("prison_started", "userdata").where(
        user_id=user_id).one() - current_time()
    is_in_prison = in_prison > 0
    if is_in_prison and not is_admin:
        minutes = int(in_prison / 60)
        seconds = int(in_prison % 60)
        await bot.send_message(
            user_id,
            f'👮‍♂️<i> Вы находитесь в тюрьме. До выхода вам осталось {minutes}'
            f' минут {seconds} секунд</i>'
        )
        return False

    rank = cur.execute(
        f"SELECT rank FROM userdata WHERE user_id = {user_id}"
    ).fetchone()[0]
    if rank < 2 and is_admin:
        with contextlib.suppress(Exception):
            await bot.send_message(
                user_id,
                "👨‍⚖️ <i>Сударь, эта команда доступна только админам</i>"
            )
        return False
    return True


async def is_allowed_nonick(user_id: int) -> bool:
    return (
        bool(
            cur.select("nonick_cmds", "userdata").where(user_id=user_id).one()
        )
        if await check_user(user_id)
        else False
    )


def user_exists(user_id: str | int) -> bool:
    """returns `True` if user with such user_id exists, else `False`"""
    return (
        int(cur.execute(
            f"SELECT count(*) FROM userdata WHERE user_id={user_id}"
        ).one())
        > 0
    )


async def answer(
    event: Union[Message, CallbackQuery, Update],
    message: Optional[str] = None,
    editable: Optional[bool | list[str]] = False,
    edit_sleep: Union[bool, int, float] = 1,
    reply: bool = False,
    italise: bool = False,
    *args: Any,
    **kwargs: Any
) -> Message | list[Message] | bool | None:
    if type(event) is Message:
        return await _answer_message(
            event,
            message=message,
            editable=editable,
            reply=reply,
            edit_sleep=edit_sleep,
            italise=italise,
            **kwargs
        )
    elif type(event) is CallbackQuery:
        return


async def _answer_message(
    event: Message,
    message: Optional[str] = None,
    editable: Optional[list[str] | bool] = None,
    reply: bool = False,
    edit_sleep: Optional[float] = None,
    italise: bool = False,
    **kwargs: Any
) -> Union[Message, list[Message]]:
    message = await _italise(message) if italise else message  # type: ignore
    if editable:
        editable = await _italise(editable) if italise else editable  # type: ignore # noqa: E501

    if not message and not editable:
        raise AttributeError(
            "You should specify either message or list of messages"
            " to be edited"
        )
    elif message and not editable:
        return await event.answer(message, reply=reply, **kwargs)

    else:
        if not message:
            message = DEFAULT_MESSAGE
        messages = [await event.answer(message, reply=reply, **kwargs)]
        await asyncio.sleep(edit_sleep or DEFAULT_SLEEP)

        if not isinstance(editable, Iterable):
            raise TypeError('"editable" should be either Iterable or None')

        for _message in editable:  # type: ignore
            try:
                messages.append(await messages[0].edit_text(_message))
                await asyncio.sleep(edit_sleep or DEFAULT_SLEEP)
            except RetryAfter:
                await asyncio.sleep(60)
                messages.append(await messages[0].edit_text(_message))
        return messages


async def _italise(text: str | list[str]) -> list[str] | str:
    if type(text) is not str:
        return [str(await _italise(item)) for item in text]
    return HtmlDecoration().italic(text)


def escape_html(text: str, /) -> str:
    """
    :param text: Text to escape
    :return: Escaped text
    """

    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


line_regex = r'  File "(.*?)", line ([0-9]+), in (.+)'


def format_exception_line(line: str) -> str:
    filename_, lineno_, name_ = re.search(
        line_regex, line
    ).groups()  # type: ignore
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

    def _code_or_error(line: str):
        _line = f"<code>{escape_html(line)}</code>"
        return f"\n📛 <b>{escape_html(get_full_class_name(e))}</b>" if line == e.__class__.__name__ else _line  # noqa: E501

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


def run_async(
    coro: Coroutine[Any, Any, Any],
    loop: Optional[asyncio.AbstractEventLoop] = None
):
    loop = loop or asyncio.get_running_loop()
    return asyncio.run_coroutine_threadsafe(coro, loop).result()


def uptime() -> timedelta:
    """
    You can get bot uptime in seconds
    """
    return timedelta(seconds=round(time.perf_counter() - init_ts))


def ping(start: int) -> float:
    return round((time.perf_counter_ns() - start) / 10**6, 3)


async def check_current(user_id: int | str, place: str, call: CallbackQuery):
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place != place:
        await call.answer(
            text=(
                '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                'местности'
            ),
            show_alert=True
        )
        return False
    return True


async def check_places(user_id: int | str, call: CallbackQuery, *places: str):
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if current_place not in places:
        return await call.answer(
            text=(
                '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                'местности'
            ),
            show_alert=True
        )
