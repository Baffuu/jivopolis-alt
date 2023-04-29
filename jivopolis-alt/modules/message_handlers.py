import random
import time
from datetime import timedelta
from .emoji_handler import slot_machine
from .. import dp, init_ts, cur, bot, get_embedded_link, constants
from ..utils import is_allowed_nonick
from ..database.functions import profile
from ..misc.config import hellos
from .callbacks.inventory import lootbox_button
from aiogram.types import Message
from aiogram.dispatcher.filters import Text
from aiogram.utils.text_decorations import HtmlDecoration

def contains(text: str | tuple, content: str) -> bool:
    if type(text) in [tuple, list]:
        items = [content.__contains__(t) for t in text]
    else:
        items = [content.__contains__(text)]
    return True in items
    
@dp.message_handler(Text(startswith="живополис", ignore_case=True))
async def chatbot_functions(message: Message):
    text = message.text[9:].lower()
    if text.startswith(', '): text = text[1:]

    match (text):
        case t if 'привет' in t:
            await message.reply(f'<i>{random.choice(hellos)}</i>')
        case t if contains('казино', t):
            _message = await message.answer_dice("🎰")
            await slot_machine(_message, message.from_user.id)
            del _message
        case t if t.startswith(' выйди'):
            await message.reply("😭 Мне следует уйти? Очень жаль, прощайте, друзья…")
            await bot.leave_chat(message.chat.id)
    if text.__contains__('как дела'):
        await message.reply(f"<i>{random.choice(['Нормально', 'Нормально. А у тебя?', 'Типа того', 'Норм', 'Ну, нормас типа'])}</i>")
    elif text.__contains__('или'):
        await message.reply(f'<i>{random.choice(text.split(" или "))}</i>')
    elif text.__contains__('профиль'):
        await profile_alias_text(message, False)
    elif text.__contains__("баланс"):
        await my_balance_text(message, False)
    elif contains(["ид", "id"], text):
        await user_id_text(message, False)
    elif contains(["ping", "пинг"], text):
        await ping_text(message)
    elif text.__contains__("ящик"):
        await lootbox_text(message, False)
    else:
        await message.reply(f"<i>{random.choice(['А?', 'Что надо?', 'Чё звал?', 'Ещё раз позовёшь - получишь бан!', 'И тебе привет', 'Да?'])}</i>")
        
@dp.message_handler(Text(startswith="профиль", ignore_case=True))
async def profile_alias_text(message: Message, nonick = True):
    if not await is_allowed_nonick(message.from_user.id) and nonick:
        return
    if message.reply_to_message:
        await profile(message.reply_to_message.from_user.id, message)
    else:
        await profile(message.from_user.id, message)

@dp.message_handler(Text(equals='мой баланс', ignore_case=True))
async def my_balance_text(message: Message, nonick = True):
    if not await is_allowed_nonick(message.from_user.id) and nonick:
        return
    user_id = message.from_user.id
    money = cur.execute(f'SELECT balance FROM userdata WHERE user_id={user_id}').fetchone()[0]
    await message.answer(f'<i><b>{await get_embedded_link(user_id)}</b> размахивает перед всеми своими накоплениями в количестве <b>${money}</b></i>')
    
@dp.message_handler(Text(equals=['ид', 'id'], ignore_case=True))
async def user_id_text(message: Message, nonick = True):
    if not await is_allowed_nonick(message.from_user.id) and nonick:
        return
    await message.reply(
        f"<code>{message.reply_to_message.from_user.id}</code>"
        if message.reply_to_message
        else f"<code>{message.from_user.id}</code>"
    )

@dp.message_handler(Text(startswith=["ping", "пинг"], ignore_case=True))
async def ping_text(message: Message):
    start = time.perf_counter_ns()
    message = await message.reply("🌘")

    await message.edit_text(
        (
            f"<b>PONG ⚡️ </b><code>{round((time.perf_counter_ns() - start) / 10**6, 3)}</code><b> ms.</b>"
            f"<b>\n🚀 UPTIME: </b><code>{str(timedelta(seconds=round(time.perf_counter() - init_ts)))}</code>"
        )
    )

@dp.message_handler(Text(startswith=["ящик"], ignore_case=True))
async def lootbox_text(message: Message, nonick = True):
    if not await is_allowed_nonick(message.from_user.id) and nonick:
        return
    await lootbox_button(message.from_user.id, message)
