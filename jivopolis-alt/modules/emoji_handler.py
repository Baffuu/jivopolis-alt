import contextlib 
import random
import asyncio
from ..filters import RequireBetaFilter
from ..database.functions import check, earn
from ..database import cur, conn
from ..misc import OfficialChats, get_embedded_link
from ..misc.constants import SLOTMACHINE_TOKEN_COST, ERROR_MESSAGE
from .. import bot, Dispatcher, logger
from aiogram.types import Message, ChatType

async def dice_handler(message: Message):
    try:
        with contextlib.suppress(AttributeError):
            await check(message.from_user.id, message.chat.id)
        health = cur.execute(f"SELECT health FROM userdata WHERE user_id={message.from_user.id}").fetchone()[0]
        is_banned = bool(cur.execute(f"SELECT is_banned FROM userdata WHERE user_id={message.from_user.id}").fetchone()[0])

        if is_banned:
            await message.answer(
                '🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, обратитесь в поддержку.',
                show_alert=True,
            )
            return await bot.send_message(
                message.from_user.id, 
                ("🧛🏻‍♂️ Вы были забаненны в боте. Если вы считаете, что это - ошибка, "
                f"обратитесь в <a href='{OfficialChats.SUPPORTCHATLINK}'>поддержку</a>."),
            )

        if health < 0:
            await message.answer(text='☠️ Вы умерли')

            if message.chat.type == ChatType.PRIVATE:
                return await message.answer('<i>☠️ Вы умерли. Попросите кого-нибудь вас воскресить</i>' )

        cur.execute('SELECT count(*) FROM clandata WHERE clan_id = ?', (message.chat.id,))
        count = 0 #cur.fetchone()[0] = 0
        if count != 0:
            cur.execute("SELECT dice FROM clandata WHERE group_id=?", (message.chat.id,))
            dice = cur.fetchone()[0]
            if dice == 0:
                await bot.delete_message(message.chat.id, message.message_id)
                return
        '''
        cur.execute("SELECT count(*) FROM clandata WHERE clan_id = ?", (message.chat.id,))
        count = cur.fetchone()[0]
        if count == 0:
            return
        cur.execute("SELECT gameclub FROM clandata WHERE clan_id = ?", (message.chat.id,))
        gameclub = cur.fetchone()[0]
        if gameclub == 1:
            return
        '''
            
        if message.dice.emoji == '🎰':   
            return await slot_machine(message)
    except Exception as e:
        logger.exception(e)
        await message.answer(ERROR_MESSAGE.format(e))

async def slot_machine(message: Message, user_id: int | None = None):
    if message.forward_date: #to avoid dupe with forward
        return
    user_id = user_id or message.from_user.id
    chat_id = message.chat.id 

    balance = cur.execute(f"SELECT balance FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if balance < SLOTMACHINE_TOKEN_COST:
        return await message.answer("<i>У вас недостаточно денег. Стоимость одной попытки: <b>$10</b></i>")

    _message = await message.answer(f'<i><b>{await get_embedded_link(user_id)}</b> бросает в автомат жетон стоимостью <b>${SLOTMACHINE_TOKEN_COST}</b></i>')
    await earn(-SLOTMACHINE_TOKEN_COST, message)

    cur.execute(f"UPDATE clandata SET clan_balance=clan_balance+{SLOTMACHINE_TOKEN_COST//2} WHERE clan_id={chat_id}")
    conn.commit()
    cur.execute(f"UPDATE clandata SET clan_balance=clan_balance+{SLOTMACHINE_TOKEN_COST//2} WHERE clan_id={OfficialChats.CASINOCHAT}")
    conn.commit()

    value = message.dice.value

    match (value):
        case 1: # bar bar bar
            rand = random.randint(50,75)
            is_win = await _slots_win(user_id, chat_id, 1, rand)
        case x if x in [22, 43]: # 🍇🍇🍇, 🍋🍋🍋
            rand = random.randint(100,125)
            is_win = await _slots_win(user_id, chat_id, 2, rand) 
        case 64: # 777
            rand = random.randint(225,275)
            is_win = await _slots_win(user_id, chat_id, 3, rand)
        case _:
            is_win = False
    await asyncio.sleep(60)
    await _message.delete()
    
    if not is_win:
        await message.delete()

WIN_MESSAGE = [
    "😞 В игровом клубе живополиса не осталось денег, мы не можем выдать вам ваше вознаграждение",
    "🎏 Неплохо! Вы получаете ${}.",
    "🎉 А вам сегодня определённо везёт! Вы получаете ${}.",
    "🎊 ДЖЕКПОТ! Вы получаете ${}."
]

async def _slots_win(user_id, chat_id = None, winner: int = 0, price: int = None):
    message = WIN_MESSAGE[winner]
    await earn(price, user_id=user_id)
    treasury = cur.execute("SELECT treasury FROM globaldata").fetchone()[0]

    if treasury < price:
        await bot.send_message(chat_id, WIN_MESSAGE[0])
        return False
    cur.execute(f"UPDATE clandata SET clan_balance=clan_balance+{price//4} WHERE clan_id={OfficialChats.CASINOCHAT}")
    cur.execute(f"UPDATE globaldata SET treasury=treasury-{price+price//4}")
    conn.commit()
    await bot.send_message(chat_id, message.format(price))
    return True

def register(dp: Dispatcher):
    dp.register_message_handler(dice_handler,  RequireBetaFilter(), content_types=['dice'])