import random
import time
import contextlib
from ..items import ITEMS
from .. import utils
from typing import Iterable
from ..filters import RequireBetaFilter
from .emoji_handler import slot_machine
from .. import dp, cur, bot, tglog, get_embedded_link
from ..utils import is_allowed_nonick
from ..database.functions import profile, can_interact, get_process
from ..misc.config import hellos
from .callbacks.inventory import lootbox_button
from aiogram.types import Message, ChatType
from aiogram.dispatcher.filters import Text
from .callbacks.traveling import find_address
from .callbacks.clans import confirm_clan_profile_setting, confirm_clan_photo


def contains(text: str | Iterable, content: str) -> bool:
    if type(text) is str:
        items = [content.__contains__(text)]
    elif isinstance(text, Iterable):
        items = [content.__contains__(t) for t in text]
    else:
        return False
    return True in items


@dp.message_handler(
    Text(startswith="живополис", ignore_case=True),
    RequireBetaFilter()
)
async def chatbot_functions(message: Message):
    if not await can_interact(message.from_user.id):
        return
    if not await RequireBetaFilter().check(message, False):
        return
    text = message.text[9:].lower()
    if text.startswith(', '):
        text = text[1:]
    if text.startswith(" "):
        text = text[1:]
    match (text):
        case t if 'привет' in t:
            await message.reply(f'<i>{random.choice(hellos)}</i>')
        case t if contains('казино', t):
            _message = await message.answer_dice("🎰")
            await slot_machine(_message, message.from_user.id)
            del _message
        case t if t.startswith('выйди'):
            await message.reply(
                "<i>😭 Мне следует уйти? Очень жаль. Прощайте, друзья…</i>"
            )
            await bot.leave_chat(message.chat.id)
        case t if t.startswith(('передать ', 'пожертвовать ')):
            message.text = text
            await give_money(message, False)
    if text.__contains__('как дела'):
        await message.reply(f"<i>{choice_how()}</i>")
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
        await message.reply(f"<i>{choice_else()}</i>")


@dp.message_handler(
    Text(
        startswith="профиль",
        ignore_case=True
    ),
    RequireBetaFilter()
)
async def profile_alias_text(message: Message, nonick=True):
    if not await can_interact(message.from_user.id):
        return
    if not await is_allowed_nonick(message.from_user.id) and nonick:
        return
    if message.reply_to_message:
        await profile(message.reply_to_message.from_user.id, message)
    else:
        await profile(message.from_user.id, message)


@dp.message_handler(
    Text(
        equals='мой баланс',
        ignore_case=True
    ),
    RequireBetaFilter()
)
async def my_balance_text(message: Message, nonick: bool = True):
    if not await can_interact(message.from_user.id):
        return
    if not await is_allowed_nonick(message.from_user.id) and nonick:
        return
    user_id = message.from_user.id
    money = cur.select("balance", "userdata").where(user_id=user_id).one()

    await message.answer(
        f'<i><b>{await get_embedded_link(user_id)}</b> размахивает перед всеми'
        f' своими накоплениями в количестве <b>${money}</b></i>'
    )


@dp.message_handler(
    Text(
        equals=['ид', 'id'],
        ignore_case=True
    ),
    RequireBetaFilter()
)
async def user_id_text(message: Message, nonick: bool = True):
    if not await can_interact(message.from_user.id):
        return
    if not await is_allowed_nonick(message.from_user.id) and nonick:
        return
    await message.reply(
        f"<code>{message.reply_to_message.from_user.id}</code>"
        if message.reply_to_message
        else f"<code>{message.from_user.id}</code>"
    )


@dp.message_handler(
    Text(
        startswith=["ping", "пинг"],
        ignore_case=True
    ),
    RequireBetaFilter()
)
async def ping_text(message: Message):
    start = time.perf_counter_ns()
    message = await message.reply("🌘")

    await message.edit_text(
        (
            f"<b>PONG ⚡️ </b><code>{utils.ping(start)}</code><b> ms.</b>"
            f"<b>\n🚀 UPTIME: </b><code>{str(utils.uptime())}</code>"
        )
    )
    from .marketplace.marketplace import market
    market.publish(ITEMS["lootbox"], message.from_id, 23)


@dp.message_handler(
    Text(
        startswith=["ящик"],
        ignore_case=True
    ),
    RequireBetaFilter()
)
async def lootbox_text(message: Message, nonick: bool = True):
    if not await can_interact(message.from_user.id):
        return
    if not await is_allowed_nonick(message.from_user.id) and nonick:
        return
    with contextlib.suppress(Exception):
        await lootbox_button(message.from_user.id, message)


@dp.message_handler(
    lambda message: (not message.text.startswith('/') and
                     not message.text.startswith('.')),
    RequireBetaFilter())
async def processes_text(message: Message):
    process = await get_process(message.from_user.id)
    if process == '':
        return

    if not await can_interact(message.from_user.id):
        return
    match (process):
        case 'search_address':
            await find_address(message)
        case 'set_clan_name':
            await confirm_clan_profile_setting(message, 'clan_name')
        case 'set_clan_bio':
            await confirm_clan_profile_setting(message, 'description')
        case 'set_clan_link':
            await confirm_clan_profile_setting(message, 'link')
        case 'set_clan_photo':
            await confirm_clan_photo(message)
        case _:
            return
    cur.update("userdata").set(process='').where(
        user_id=message.from_user.id).commit()


async def give_money(message: Message, nonick=True):
    if not await can_interact(message.from_user.id):
        return
    if not await is_allowed_nonick(message.from_user.id) and nonick:
        return

    amount = int(message.text.split(" ")[1])

    user_id = message.from_user.id
    # chat_id = message.chat.id

    if message.chat.type == ChatType.PRIVATE:
        return

    if not message.reply_to_message:
        return

    money = cur.select("balance", from_="userdata").where(
        user_id=user_id).one()
    other_id = message.reply_to_message.from_user.id

    if money < amount:
        return await utils.answer(
            message,
            "💨 Недостаточно денег",
            italise=True,
            reply=True
        )
    elif money < 0:
        return await utils.answer(
            message,
            "😧 Нельзя передать отрицательное количество денег!",
            italise=True,
            reply=True
        )
    elif user_id == other_id:
        return await utils.answer(
            message,
            f'<b>{await get_embedded_link(user_id)}</b> перекладывает из'
            f' кармана в карман <b>${amount}</b>',
            italise=True
        )

    cur.update("userdata").add(balance=-amount).where(user_id=user_id).commit()
    cur.update("userdata").add(balance=amount).where(user_id=other_id).commit()

    await utils.answer(
        message,
        f'<b>{await get_embedded_link(user_id)}</b> передал <b'
        f'>{await get_embedded_link(other_id)}</b> ${amount}',
        italise=True,
        reply=True
    )
    await tglog(
        f"{await get_embedded_link(user_id)} передал "
        f"{await get_embedded_link(other_id)} ${amount}",
        "#moneyshare"
    )


def choice_how() -> str:
    return random.choice(
        [
            'Нормально',
            'Нормально. А у тебя?',
            'Типа того',
            'Норм',
            'Ну, нормас типа'
        ]
    )


def choice_else() -> str:
    return random.choice(
        [
            'А?',
            'Что надо?',
            'Чё звал?',
            'Ещё раз позовёшь - получишь бан!',
            'И тебе привет',
            'Да?'
        ]
    )
