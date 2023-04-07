import random

from datetime import datetime
from math import floor
from typing import Union

from ..misc import OfficialChats
from ..misc.config import limeteds, leveldesc, levelrange, ITEMS, ach, ADMINS, clanitems

from .. import bot, logger

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup, 
    ReplyKeyboardRemove, 
    CallbackQuery, 
    User, 
    Message
)

from ..database.sqlitedb import cur, conn, insert_user
from ..misc import current_time, get_link, get_mask, allitems

async def check(user_id: int, chat_id: str) -> None:
    '''
    checks everything 
    '''
    try:
        lastfill = current_time() - cur.execute("SELECT lastfill FROM globaldata").fetchone()[0]

        if lastfill >= 86400:
            for item in limeteds:
                cur.execute(f"UPDATE globaldata SET {item}={random.randint(5, 15)}")
        cur.execute(f"UPDATE globaldata SET lastfill={current_time()}")

        cur.execute(f"UPDATE userdata SET lastseen={current_time()} WHERE user_id={user_id}")
        conn.commit()

        xp = cur.execute(f"SELECT xp FROM userdata WHERE user_id={user_id}").fetchone()[0]

        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]

        if user_id in ADMINS and rank < 2:
            cur.execute(f"UPDATE userdata SET rank=3 WHERE user_id={user_id}")
            conn.commit()

        '''
        lastelec = current_time() - cur.execute(f"SELECT lastelec FROM userdata WHERE user_id={user_id}").fetchone()[0]

        if lastelec > 86400:
            cur.execute(f"UPDATE userdata set electimes=0 WHERE user_id={user_id}")
            conn.commit()
            cur.execute(f"UPDATE userdata set lastelec={current_time()} WHERE user_id={user_id}")
            conn.commit()'''

        lvl = cur.execute(f"SELECT level FROM userdata WHERE user_id={user_id}").fetchone()[0]

        if lvl > len(levelrange): 
            return
        elif xp >= levelrange[lvl] and xp < levelrange[lvl+1]:
            return
        for i in levelrange: #todo recreate
            if xp >= i and levelrange.index(i) >= len(levelrange) - 1 and lvl != levelrange.index(i):
                cur.execute(f"UPDATE userdata SET lvl={levelrange.index(i)} WHERE user_id={user_id}")
                conn.commit()
                try:
                    return await bot.send_message(user_id, f"<i>&#128305; Теперь ваш уровень в Живополисе: <b>{levelrange.index(i)}</b>\nПоздравляем!\n{leveldesc[levelrange.index(i)]}</i>")
                except Exception:
                    return await bot.send_message(chat_id, f"<i>&#128305; Теперь ваш уровень в Живополисе: <b>{levelrange.index(i)}</b>\nПоздравляем!\n{leveldesc[levelrange.index(i)]}</i>")

            if xp>=i and xp<levelrange[levelrange.index(i)+1] and lvl!=levelrange.index(i):
                cur.execute("UPDATE userdata SET level=? WHERE user_id=?", (levelrange.index(i), user_id,))
                conn.commit()
                try:
                    return await bot.send_message(user_id, f"<i>&#128305; Теперь ваш уровень в Живополисе: <b>{levelrange.index(i)}</b>\nПоздравляем!\n{leveldesc[levelrange.index(i)]}</i>")
                except Exception:
                    return await bot.send_message(chat_id, f"<i>&#128305; Теперь ваш уровень в Живополисе: <b>{levelrange.index(i)}</b>\nПоздравляем!\n{leveldesc[levelrange.index(i)]}</i>")

    except Exception as e:
        if "NoneType" in str(e):
            logger.exception(e)
        else:
            return logger.exception(e)    


async def itemdata(user_id: int, item: str) -> Union[str, None, InlineKeyboardButton]:
    """
    :param user_id - telegram user ID
    :param item - item slot name

    :returns aiogram.types.InlineKeyboardButton - button with item icon && itemcount
    """
    try: 
        items = cur.execute(f"SELECT {item} FROM userdata WHERE user_id={user_id}").fetchone()[0]

        if items > 0:      
            return InlineKeyboardButton(text=f"{ITEMS[item][0]} {items}", callback_data=item)
                
        else:      
            return "emptyslot"           
    except Exception as e:         
        return logger.exception(e)


def buybutton(
    item: str, 
    status: str = None, 
    tip: int = 0
) -> Union[InlineKeyboardButton, None]:
    '''
    You can get special button for buying something
    
    :param item (str) - item index that will be bought
    :param status (str) - (Optional) special index for buying category
    :param tip (int) - (Optional) additional money to price
    
    :returns: None if item does not exists or an error occured; aiogram.types.InlineKeyboardButton
    '''
    if item not in allitems:
        return None
    itemob = allitems[item]

    cost = itemob.price if isinstance(itemob.price, int) else 0 + tip

    if (
        status
        and status == 'clan'
        and item in clanitems[0]
    ):
        return InlineKeyboardButton(text=f'{itemob.emoji} {itemob.ru_name} - ${clanitems[1][clanitems[0].index(item)+tip]}', callback_data=f'buyclan_{item}')
    elif (
        status 
        and status == 'clan' 
        or status 
        and status != 'limited'
    ):
        return None
    elif not status:
        if item.startswith('pill') and len(item) > 4:
            return InlineKeyboardButton(f'{itemob.emoji} {itemob.ru_name} - ${cost}', callback_data=f"buy_{item}:0:{item[5:]}")
        return InlineKeyboardButton(f'{itemob.emoji} {itemob.ru_name} - ${cost}', callback_data=f'buy_{item}:{tip}')
    else:
        return (
            InlineKeyboardButton(
                f'{itemob.emoji} {itemob.ru_name} - ${cost}', callback_data=f'buy24_{item}'
            )
            if item in limeteds
            else None
        )


async def eat(call: CallbackQuery, food: str) -> None:
    '''
    :param call (aiogram.types.CallbackQuery) - aiogram callback query
    :food (str) - food index 
    
    :raise ValueError if food does not exists
    '''

    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if food in ITEMS:
        heal = ITEMS[food][4][1]
    else:
        raise ValueError('no such food')

    health = cur.execute(f"SELECT health FROM userdata WHERE user_id={user_id}").fetchone()[0]
    
    if heal == 1000:
        heal = random.randint(-100,10)
    if heal == 900:
        heal = random.randint(-10,5)

    if health + heal > 100:
        return await call.answer('🧘 Вы недостаточно голодны для такой пищи', show_alert = True)
            
    health = cur.execute(f"SELECT health FROM userdata WHERE user_id={user_id}").fetchone()[0]
    food_amount = cur.execute(f"SELECT {food} FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if food_amount < 1:
        return await call.answer(text="🚫 У вас нет такой еды", show_alert = True)

    cur.execute(f"UPDATE userdata SET {food}={food}-1 WHERE user_id={user_id}")
    conn.commit()

    cur.execute(f"UPDATE userdata SET health=health+{heal} WHERE user_id={user_id}")
    conn.commit()

    if heal > 0:
        await call.answer(f"❤ +{heal} HP на здоровье!", show_alert = True)
    else:
        await call.answer("🤢 Зачем я это съел? Теперь мне нехорошо", show_alert = True)
        health = cur.execute(f"SELECT health FROM userdata WHERE user_id={user_id}").fetchone()[0]

        if health < 1:
            return await bot.send_message(chat_id, "<i>&#9760; Вы умерли</i>")


async def poison(user: User, target_id: int, chat_id: int) -> None:
    '''
    to use poison on a user 
    
    :param user (aiogram.types.User) - user that is poisoning another user 
    :param target_id (int) - telegram user ID of user that will be poisoned 
    :chat_id chat_id (int) - telegram chat ID to which messages will be sent 
    '''

    try:
        my_health = cur.execute(f"SELECT health FROM userdata WHERE user_id={user.id}").fetchone()[0]

        if my_health < 0:
            return await bot.send_message(chat_id, "<i>&#9760; Вы умерли. Попросите кого-нибудь вас воскресить</i>")

        poison = cur.execute(f"SELECT poison FROM userdata WHERE user_id={user.id}").fetchone()[0]

        if poison < 1:
            return await bot.send_message(chat_id, "<i>&#10060; У вас нет яда. Возможно, это к лучшему</i>")

        cur.execute(f"UPDATE userdata SET poison=poison-1 WHERE user_id={user.id}")
        conn.commit()

        nick = cur.execute(f"SELECT nick FROM userdata WHERE user_id={user.id}").fetchone()[0]
        mask = get_mask(user.id)

        target_nick = cur.execute(f"SELECT nick FROM userdata WHERE user_id={target_id}").fetchone()[0]
        target_mask = get_mask(target_id)

        random_damage = random.randint(50, 200)
        if done := random.choice([True, False]):
            cur.execute(f"UPDATE userdata SET health=health-{random_damage} WHERE user_id={target_id}")
            conn.commit()

            await bot.send_message(OfficialChats.LOGCHAT, f"<i><b><a href=\"{await get_link(user.id)}\">{mask}{nick}</a></b> отравил <b><a href=\"{await get_link(target_id)}\">{target_mask}{target_nick}</a></b>.\n#user_poison</i>")
            await bot.send_message(chat_id, f"<i>🧪 Вы отравили <b><a href=\"{await get_link(target_id)}\">{target_mask}{target_nick}</a></b></i>")
            await bot.send_message(target_id, f"<i>🧪 Вас отравил <b><a href=\"{await get_link(user.id)}\">{mask}{nick}</a></b></i>")
        else:
            return await bot.send_message(chat_id, "<i>😵‍💫 Неудача. Возможно, это к лучшему.\nЯд потрачен зря</i>")

    except Exception as e:
        await bot.send_message(chat_id, "&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>")
        await bot.send_message(chat_id, f"<i><b>Текст ошибки: </b>{e}</i>")
        return logger.exception(e)


async def shoot(user_id: int, target_id: int, chat_id: int) -> None: #function is useless now...
    '''
    shoot a person
    
    :param user_id (int) - Telegram User ID of user that is shooting another user 
    :param target_id (int) - Telegram User ID of user that will be shooted
    
    :param chat_id (int) - Telegram Chat ID of chat in which messages will be sent 
    '''
    try:
        my_health = cur.execute(f"SELECT health FROM userdata WHERE user_id={user_id}")

        if my_health < 0:
            return await bot.send_message(chat_id, "<i>&#9760; Вы умерли. Попросите кого-нибудь вас воскресить</i>")

        gun = cur.execute(f"SELECT gun FROM userdata WHERE user_id={user_id}").fetchone()

        if gun < 1:
            return await bot.send_message(chat_id, "<i>&#10060; У вас нет пистолета. Возможно, это к лучшему</i>")

        health = cur.execute(f"SELECT health FROM userdata WHERE user_id={target_id}").fetchone()

        cur.execute(f"UPDATE userdata SET gun=gun-1 WHERE user_id={user_id}")
        conn.commit()

        nick = cur.execute(f"SELECT nick FROM userdata WHERE user_id={user_id}").fetchone()
        mask = get_mask(user_id)
        target_nick = cur.execute(f"SELECT nick FROM userdata WHERE user_id={target_id}").fetchone()
        target_mask = get_mask(target_id)

        rand = random.randint(100,200)
        if done := random.choice([True, False]):
            cur.execute(f"UPDATE userdata SET health=health-{rand} WHERE user_id={target_id}")
            conn.commit()

            await bot.send_message(OfficialChats.LOGCHAT, f"<i><b><a href=\"{await get_link(user_id)}\">{mask}{nick}</a></b> застрелил <b><a href=\"{await get_link(user_id)}\">{target_mask}{target_nick}</a></b>\n#user_gunshoot</i>")
            await bot.send_message(chat_id, f"<i>&#128299; Вы застрелили <b><a href=\"{await get_link(target_id)}\">{target_mask}{target_nick}</a></b></i>")
            await bot.send_message(target_id, f"<i>&#128299; Вас застрелил <b><a href=\"{await get_link(user_id)}\">{mask}{nick}</a></b></i>")

            if prison := random.choice([True, False]):
                cur.execute(f"UPDATE userdata SET prison={current_time() + 1200} WHERE user_id={user_id}")
                conn.commit()

                await bot.send_message(chat_id, f"<i>&#128110; Господин <b><a href=\"{await get_link(user_id)}\">{mask}{nick}</a></b>, вы задержаны за убийство огнестрельным оружием. Пройдёмте в отделение.\n\nВы были арестованы на <b>20 минут</b></i>")
        else:
            await bot.send_message(chat_id, f"<i>&#10060; Вы выстрелили мимо. Возможно, это к лучшему.\nПистолет потрачен зря</i>")

    except Exception as e:
        await bot.send_message(chat_id, "&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>")
        await bot.send_message(chat_id, f"<i><b>Текст ошибки: </b>{e}</i>")


async def achieve(user_id: int, chat_id : int, achievement: str) -> None: #todo new ACHIEVEMENTS
    """
    achieve a user 
    
    :param user_id (int) - Telegram User ID of user that will be achieved 
    :param chat_id (int) - Telegram Chat ID of chat in which messages will be sent 
    :param achievement (str) - Index of achievement 
    """
    try:
        achieve = cur.execute(f"SELECT {achievement} FROM userdata WHERE user_id={user_id}").fetchone()
        
        if achieve != 0:
            return

        index = ach[0].index(achievement)
        name = ach[1][index]
        desc = ach[2][index]
        money = ach[3][index]
        points = ach[4][index]

        cur.execute(f"UPDATE userdata SET {achievement} = 1 WHERE user_id = {user_id}")
        conn.commit()

        rasa = cur.execute(f"SELECT rasa FROM userdata WHERE user_id = {user_id}").fetchone()
        nick = cur.execute(f"SELECT nick FROM userdata WHERE user_id = {user_id}").fetchone()

        cur.execute(f"UPDATE userdata SET balance = balance + {money} WHERE user_id = {user_id}")
        conn.commit()
        cur.execute(f"UPDATE userdata SET points = points+{points} WHERE user_id = {user_id}")
        conn.commit()

        chat_type = await bot.get_chat(chat_id)
        chat_type = chat_type.type

        if chat_type == "private":
            await bot.send_message(chat_id, f"<i>У вас новое достижение: <b>{name}</b>\n{desc}. \nВаша награда: <b>${money}</b> и &#128161; <b>{points}</b> очков</i>")
        else:
            await bot.send_message(chat_id, f"<i><b><a href=\"tg://user?id={user_id}\">{rasa}{nick}</a></b>, у вас новое достижение: <b>{name}</b>\n{desc}. \nВаша награда: <b>${money}</b> и &#128161; <b>{points}</b> очков</i>")
    except Exception as e:
        await bot.send_message(
            chat_id, 
            (
                "&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. "
                "Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт"
                " в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появля"
                "ется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную "
                "(t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>"
            ))
        await bot.send_message(chat_id, f"<i><b>Текст ошибки: </b>{e}</i>")


async def cure(user_id: str, target_id: str, chat_id: str) -> None: #function is useless now...
    '''
    to cure someone...
    '''
    try:
        nerr = 0
        medicine = cur.execute(f"SELECT medicine FROM userdata WHERE user_id={user_id}").fetchone()

        if medicine < 1:
            return await bot.send_message(chat_id, "<i>&#10060; У вас нет таблеток(</i>")

        health = cur.execute(f"SELECT health FROM userdata WHERE user_id={target_id}").fetchone()

        nick = cur.execute(f"SELECT nick FROM userdata WHERE user_id={user_id}").fetchone()
        mask = get_mask(user_id)

        target_nick = cur.execute(f"SELECT nick FROM userdata WHERE user_id={target_id}").fetchone()
        target_mask = get_mask(target_id)

        if health > 0 and health < 100:
            cur.execute(f"UPDATE userdata SET medicine=medicine-1 WHERE user_id={user_id}")
            conn.commit()

            rand = random.randint(1, 100-health)

            cur.execute(f"UPDATE userdata SET health=health+{rand} WHERE user_id={target_id}")
            conn.commit()

            if target_id == user_id:
                return await bot.send_message(chat_id, "<i>&#128138; Успех! Вы вылечили себя</i>")
            await bot.send_message(chat_id, f"<i>&#128138; Успех! Вы вылечили <b><a href=\"{await get_link(target_id)}\">{target_mask}{target_nick}</a></b></i>")
            await bot.send_message(target_id, f"<i>&#128138; Вас вылечил <b><a href=\"{await get_link(user_id)}\">{mask}{nick}</a></b></i>")
            nerr = 1

        elif health >= 100:
            if target_id != user_id:
                return await bot.send_message(chat_id, f"<i>&#128138; <b><a href=\"{await get_link(target_id)}\">{target_mask}{target_nick}</a></b> полностью здоров, зачем вам тратить лекарства впустую?\nЛекарства <b>не потрачены</b></i>")   
            else:                                   
                return await bot.send_message(chat_id, f"<i>&#128138; Вы полностью здоровы, зачем вам тратить лекарства впустую?\nЛекарства <b>не потрачены</b></i>")
        else:
            if target_id == user_id:
                return await bot.send_message(chat_id, "<i>&#10060; Вы не можете воскресить самого себя</i>")

            cur.execute(f"UPDATE userdata SET medicine=medicine-1 WHERE user_id={user_id}")
            conn.commit()

            rand = random.randint(50,100)

            cur.execute(f"UPDATE userdata SET health={rand} WHERE user_id={target_id}")
            conn.commit()

            await bot.send_message(chat_id, f"<i>&#128138; Успех! Вы воскресили <b><a href=\"{await get_link(target_id)}\">{target_mask}{target_nick}</a></b></i>")
            nerr = 1
            await bot.send_message(target_id, f"<i>&#128138; Вас воскресил <b><a href=\"{await get_link(user_id)}\">{mask}{nick}</a></b></i>")

            await achieve(user_id, chat_id, "helper")

        if nerr == 1:
            cur.execute(f"UPDATE userdata SET cured=cured+1 WHERE user_id={user_id}")
            conn.commit()

            cured = cur.execute(f"SELECT cured FROM userdata WHERE user_id={user_id}").fetchone()

            if cured >= 20:
                await achieve(user_id, chat_id, "medquest")
                cur.execute(f"UPDATE userdata SET medic=medic+1 WHERE user_id={user_id}")
                conn.commit()
                await bot.send_message(chat_id, "<i>Вы получаете <b>🩺 Стетоскоп</b>. Эта маска будет показывать всем, что вы профессиональный врач, и вам можно доверять</i>")

    except Exception as e:
        await bot.send_message(chat_id, "&#10060; <i>При выполнении команды произошла ошибка. Проверьте, есть ли у вас аккаунт в Живополисе. Если вы выполняли действие над другим пользователем, проверьте, есть ли у этого пользователя аккаунт в Живополисе. Помните, что выполнение действий над ботом Живополиса невозможно.\nЕсли ошибка появляется даже когда у вас есть аккаунт, возможно, проблема в коде Живополиса. Сообщите о ней в Приёмную (t.me/zhivolab), и мы постараемся исправить проблему.\nИзвините за предоставленные неудобства</i>")
        await bot.send_message(chat_id, f"<i><b>Текст ошибки: </b>{e}</i>")


async def profile(user_id: int, message: Message, called: bool = False): #todo: refactor
    nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    mask = get_mask(user_id)
    profile_type = cur.execute(f"SELECT profile_type FROM userdata WHERE user_id = {user_id}").fetchone()[0]

    if profile_type == "private" and user_id != message.from_user.id and not called:
        return await message.answer(f"🚫 <i><b><a href=\"tg://user?id={user_id}\">{mask}{nick}</a></b> скрыл свой профиль</i>")

    balance = cur.execute(f"SELECT balance FROM userdata WHERE user_id={user_id}").fetchone()[0]
    invited_by = cur.execute(f"SELECT inviter_id FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if invited_by != 0:
        invited_nick = cur.execute(f"SELECT nickname FROM userdata WHERE user_id = {invited_by}").fetchone()[0]
        invited_mask = get_mask(invited_by)
        inviter = f"\n📎 Пригласивший пользователь: <b><a href=\"{await get_link(user_id)}\">{invited_mask}{invited_nick}</a></b>"
    else:
        inviter = '' 

    description = cur.execute(f"SELECT description FROM userdata WHERE user_id={user_id}").fetchone()[0]
    ready = cur.execute(f"SELECT is_ready FROM userdata WHERE user_id={user_id}").fetchone()[0]
    xp = cur.execute(f"SELECT xp FROM userdata WHERE user_id={user_id}").fetchone()[0]

    clan_id = cur.execute(f"SELECT clan_id FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if clan_id != 0:
        clan_type = cur.execute(f"SElECT clan_type FROM clandata WHERE clan_id={clan_id}").fetchone()[0]
        clan_link = cur.execute(f"SELECT link FROM clandata WHERE clan_id={clan_id}").fetchone()[0]
        clan_name = cur.execute(f"SELECT clan_name FROM clandata WHERE clan_id={clan_id}").fetchone()[0]

    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]
    health = cur.execute(f"SELECT health FROM userdata WHERE user_id={user_id}").fetchone()[0]
    level = cur.execute(f"SELECT level FROM userdata WHERE user_id={user_id}").fetchone()[0]
    lastseen = cur.execute(f"SELECT lastseen FROM userdata WHERE user_id={user_id}").fetchone()[0]
    #photo = cur.execute(f"SELECT photo_id FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if level<len(levelrange)-1:
        xp_left = f"XP из {levelrange[level+1]}"
    else:
        xp_left = "(макс. уровень"
    if health < 0:
        health = "<b>мёртв</b>"

    match (rank):
        case 0:
            rank = "👤 Игрок"
        case 1:
            rank = "⚜️ VIP"
        case 2:
            rank = "🛠 Админ"
        case 3:
            rank = "👑 Создатель"
        case _:
            rank = '👽 Undefined'

    seconds = current_time() - lastseen

    years = floor(seconds / 31536000)
    monthes = floor((seconds % 31536000) / 2628000)
    days = floor(((seconds % 31536000) % 2628000) / 86400)
    hours = floor((seconds % (3600 * 24)) / 3600)
    minutes = floor((seconds % 3600) / 60)

    lastseen = ""

    if years > 1:
        lastseen = "очень давно"
    elif monthes != 0:
        match (monthes):
            case 1:
                month = "месяц"
            case [2 | 3 | 4]:
                month = "месяца"
            case _:
                month = "месяцев"

        lastseen += f"{monthes} {month} "
    elif days != 0:
        day_lastnum = str(days)[len(str(days))-1]

        match (int(day_lastnum)):
            case 1:
                day = "день"
            case [2 | 3 | 4]:
                day = "дня"
            case _:
                day = "дней"

        lastseen += f"{days} {day} "
    elif hours != 0:
        hour_lastnum = str(hours)[len(str(hours))-1]

        match (int(hour_lastnum)):
            case 1:
                hour = "час"
            case [2 | 3 | 4]:
                hour = "часа"
            case _:
                hour = "часов"

        lastseen += f"{hours} {hour} "
    elif minutes != 0:
        min_lastnum = str(minutes)[len(str(minutes)) - 1]

        match (int(min_lastnum)):
            case 1:
                minute = "минута"
            case [2 | 3 | 4]:
                minute = "минуты"
            case _:
                minute = "минут"
        lastseen += f"{minutes} {minute} "

    if years <= 0:
        lastseen += "назад"

    if lastseen == "назад":
        lastseen = "только что"
    try:
        register_date = datetime.fromtimestamp(cur.execute(f"SELECT register_date FROM userdata WHERE user_id={user_id}").fetchone()[0])
        reg_year = register_date.year
        reg_month = register_date.month
        reg_day = register_date.day
        months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        reg_month = months[reg_month-1]
        register_date = f"{reg_day} {reg_month} {reg_year}"
    except ValueError as e:
        if str(e).endswith('is out of range'):
            register_date = '🧌 Старше нашей планеты.'
        else: return logger.exception(e)


    markup = InlineKeyboardMarkup()

    if (message.chat.type == "private" and message.from_user.id == user_id) or called:

        markup.add(InlineKeyboardButton(text="💡 Достижения", callback_data="achievements"))
        markup.add(InlineKeyboardButton(text="⚙ Настройки", callback_data="user_settings"))
        markup.add(InlineKeyboardButton(text="🖇 Реферальная ссылка", callback_data="my_reflink"))
        markup.add(InlineKeyboardButton(text="👥 Привлечённые пользователи", callback_data="refusers"))
    try:
        clan_link = f'"{clan_link}"'
    except UnboundLocalError:
        clan_link = ''
    prof = f"<i><b><a href=\"tg://user?id={user_id}\">{mask}{nick}</a></b>\n\
<b>{rank}</b>\n\
<b>Был(-а)</b> {lastseen}\n\
<b>Аккаунт создан:</b> {register_date}{inviter}\n\
💰 Баланс: <b>${balance}</b>\n\
📝 Описание: \n\
<b>{description}</b>\n\
⚔️ Режим готовности: <b>{'не готов' if ready == 0 else 'готов'}</b>\n\
💡 Уровень: {level} ({xp} {xp_left})\n\
🛡 Клан: <b>{(f'<a href={clan_link}>{clan_name}</a>' if clan_type == 'public' else clan_name) if clan_id != 0 else 'отсутствует'}</b>\n\
💊 Здоровье: {health}</i>"

    await message.reply(prof, reply_markup=markup)
    '''if photo == "":
        await message.reply(prof, reply_markup = markup)
    else:
        try:
            await bot.send_photo(message.chat.id, photo, caption=prof, reply_markup = markup)
        except:
            await message.answer(prof, reply_markup = markup)'''


async def earn(money: int, message: Message = None, user_id: int = None) -> None:
    '''
    To give money to a user 

    :param money (int) - how many money will be given
    :param user_id (int) -  Telegram User ID of user to which money will be given
    '''
    if not message and not user_id:
        raise ValueError("You must provide either message or user_id")
    elif not user_id:
        user_id = message.from_user.id

    cur.execute(f"UPDATE userdata SET balance = balance+{money} WHERE user_id = {user_id}")
    conn.commit()


async def buy(call: CallbackQuery, item: str, user_id: int, cost: int = None, amount: int = 1):
    '''
    buy an item 
    
    :param call (aiogram.types.CallbackQuery) - callback 
    :param item (str) - item that will be bought 
    :param user_id (int) - Telegram User ID of user who is buying an item 
    :param cost (int) - (Optional) cost of an item. Don't specify if you want to use default 
    :param amount (int) - amount
    '''
    if item not in ITEMS:
        raise ValueError("no such item")

    if not cost:
        cost = ITEMS[item][3]

    balance = cur.execute(f"SELECT balance FROM userdata WHERE user_id = {user_id}").fetchone()[0]

    if balance >= cost*amount:
        cur.execute(f"UPDATE userdata SET {item} = {item} + {amount} WHERE user_id = {user_id}"); conn.commit()

        cur.execute(f"UPDATE userdata SET balance = balance - {cost*amount} WHERE user_id = {user_id}"); conn.commit()

        await call.answer(f'Покупка прошла успешно. Ваш баланс: ${balance-cost*amount}', show_alert = True)

        cur.execute(f"UPDATE globaldata SET treasury=treasury+{cost*amount//2}"); conn.commit()
    else:
        await call.answer('🚫 У вас недостаточно денег', show_alert = True)
