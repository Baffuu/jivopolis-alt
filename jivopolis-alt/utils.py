import asyncio
from . import cur
from aiogram.types import Message, CallbackQuery, Update
from aiogram.utils.exceptions import RetryAfter
from typing import overload, Union, Any


DEFAULT_MESSAGE = "🌔"
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
