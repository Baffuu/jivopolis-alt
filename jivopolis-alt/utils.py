import asyncio
import contextlib
from . import cur, bot
from .misc.constants import OfficialChats
from aiogram.types import Message, CallbackQuery, Update
from aiogram.utils.exceptions import RetryAfter
from typing import overload, Union, Awaitable, Any

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


# --------------------------
@overload
async def answer(
    event: Message, 
    message: str = None,
    editable: bool | list = False, 
    edit_sleep: Union[bool, int, float] = 1,
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
    **kwargs
) -> Union[Message, list[Message]]:
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
