import contextlib
import random
import asyncio
from ..filters import RequireBetaFilter
from ..database.functions import check, earn, current_time
from ..database import cur
from ..misc import OfficialChats, get_embedded_link
from ..misc.constants import SLOTMACHINE_TOKEN_COST, ERROR_MESSAGE
from .. import bot, Dispatcher, logger
from aiogram.types import (
    Message, ChatType, InlineKeyboardMarkup, InlineKeyboardButton
)


async def dice_handler(message: Message):
    try:
        with contextlib.suppress(AttributeError):
            await check(message.from_user.id, message.chat.id)
        health = cur.select("health", "userdata").where(
            user_id=message.from_user.id).one()

        is_banned = bool(
            cur.select("is_banned", "userdata").where(
                user_id=message.from_user.id).one()
        )

        if is_banned:
            await message.answer(
                '🧛🏻‍♂️ <i>Вы были забанены в боте. Если вы считаете, что это '
                'ошибка, обратитесь в '
                '<a href="{OfficialChats.SUPPORTCHATLINK}">поддержку</a></i>'
            )
            return await bot.send_message(
                message.from_user.id,
                (
                    "🧛🏻‍♂️ <i>Вы были забанены в боте. Если вы считаете, что "
                    "это ошибка, "
                    f"обратитесь в <a href='{OfficialChats.SUPPORTCHATLINK}'>"
                    "поддержку</a></i>"
                ),
            )

        if health < 0:
            await message.answer(text='<i>☠️ Вы умерли</i>')

            if message.chat.type == ChatType.PRIVATE:
                return await message.answer(
                    '<i>☠️ Вы умерли. Попросите кого-нибудь вас воскресить</i>'
                )

        count = cur.select("count(*)", "clandata").where(
            clan_id=message.chat.id).one()

        if count == 1:
            dice = cur.select("filter_dice", "clandata").where(
                clan_id=message.chat.id).one()
            if dice:
                with contextlib.suppress(Exception):
                    return await message.delete()

            gameclub = cur.select("addon_gameclub", "clandata").where(
                clan_id=message.chat.id).one()
            if not gameclub:
                return
            if message.dice.emoji == '🎰':
                return await slot_machine(message)
    except Exception as e:
        logger.exception(e)
        await message.answer(ERROR_MESSAGE.format(e))


async def slot_machine(message: Message, user_id: int | None = None):
    if message.forward_date:  # to avoid dupe with forward
        return
    user_id = user_id or message.from_user.id
    chat_id = message.chat.id

    balance = cur.select("balance", "userdata").where(
        user_id=user_id).one()
    lastplay = cur.select("last_gameclub", "userdata").where(
        user_id=user_id).one()
    timeout = cur.select("game_timeout", "clandata").where(
        clan_id=chat_id).one()
    if current_time() - lastplay < timeout:
        return await message.reply(
            "😠 <i>Пользоваться игровыми автоматами в данном клане "
            f"можно раз в <b>{timeout}</b> секунд</i>",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    text="👌 Понятно",
                    callback_data="cancel_action"
                )
            )
        )

    if balance < SLOTMACHINE_TOKEN_COST:
        return await message.answer(
            "<i>У вас недостаточно денег. Стоимость одной попытки: <b>$10</b>"
            "</i>"
        )

    _message = await message.answer(
        f"<i><b>{await get_embedded_link(user_id)}</b> бросает в автомат жетон"
        f" стоимостью <b>${SLOTMACHINE_TOKEN_COST}</b></i>"
    )
    cur.update("userdata").add(balance=-SLOTMACHINE_TOKEN_COST).where(
        user_id=message.from_user.id).commit()

    cur.update("clandata").add(clan_balance=SLOTMACHINE_TOKEN_COST//2).where(
        clan_id=chat_id).commit()
    cur.update("clandata").add(clan_balance=SLOTMACHINE_TOKEN_COST//2).where(
        clan_id=OfficialChats.CASINOCHAT).commit()

    value = message.dice.value

    match (value):
        case 1:  # bar bar bar
            rand = random.randint(50, 75)
            is_win = await _slots_win(user_id, chat_id, 1, rand)
        case x if x in [22, 43]:  # 🍇🍇🍇, 🍋🍋🍋
            rand = random.randint(100, 125)
            is_win = await _slots_win(user_id, chat_id, 2, rand)
        case 64:  # 777
            rand = random.randint(225, 275)
            is_win = await _slots_win(user_id, chat_id, 3, rand)
        case _:
            is_win = False
    cur.update("userdata").set(last_gameclub=current_time()).where(
        user_id=user_id).commit()
    await asyncio.sleep(60)
    await _message.delete()

    if not is_win:
        await message.delete()

WIN_MESSAGE = [
    "<i>😞 В игровом клубе Живополиса не осталось денег, мы не можем выдать вам"
    " ваше вознаграждение</i>",
    "<i>🎏 Неплохо! Вы получаете <b>${}</b></i>",
    "<i>🎉 А вам сегодня определённо везёт! Вы получаете <b>${}</b></i>",
    "<i>🎊 ДЖЕКПОТ! Вы получаете <b>${}</b></i>"
]


async def _slots_win(
    user_id,
    chat_id: int | str = 0,
    winner: int = 0,
    price: int = 0
):
    message = WIN_MESSAGE[winner]
    await earn(price, user_id=user_id)
    treasury = cur.execute("SELECT treasury FROM globaldata").fetchone()[0]

    if treasury < price:
        await bot.send_message(chat_id, WIN_MESSAGE[0])
        return False

    cur.update("clandata").add(clan_balance=price//4).where(
        clan_id=OfficialChats.CASINOCHAT).commit()
    cur.update("globaldata").add(treasury=-price//4*3).commit()
    await bot.send_message(chat_id, message.format(price))
    return True


def register(dp: Dispatcher):
    dp.register_message_handler(
        dice_handler,
        RequireBetaFilter(),
        content_types=['dice']
    )
