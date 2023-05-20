import random

from datetime import datetime
from math import floor
from typing import Union, Optional

from .jivopolis-alt.database import cur, conn
from .jivopolis-alt import bot, logger, get_link, tglog, utils
from .jivopolis-alt.misc import current_time, ITEMS, constants
from .jivopolis-alt.misc.config import limeteds, leveldesc, levelrange, ach, ADMINS, clanitems

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup, 
    CallbackQuery, 
    User, 
    Message
)
from aiogram.utils.text_decorations import HtmlDecoration


async def poison(user: User, target_id: int | str, chat_id: int| str) -> None | Message | bool:
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

        random_damage = random.randint(50, 200)
        if random.choice([True, False]):
            cur.execute(f"UPDATE userdata SET health=health-{random_damage} WHERE user_id={target_id}")
            conn.commit()

            await tglog(f"<i><b>{await utils.get_embedded_link(user.id)}</b> отравил <b>{await utils.get_embedded_link(target_id)}\"</b></i>.", "#user_poison")
            await bot.send_message(chat_id, f"<i>🧪 Вы отравили <b>{await utils.get_embedded_link(target_id)}</b></i>")
            await bot.send_message(target_id, f"<i>🧪 Вас отравил <b>{await utils.get_embedded_link(user.id)}</b></i>")
        else:
            return await bot.send_message(chat_id, "<i>😵‍💫 Неудача. Возможно, это к лучшему.\nЯд потрачен зря</i>")

    except Exception as e:
        await bot.send_message(chat_id, constants.ERROR_MESSAGE.format(e))
        return logger.exception(e)


async def shoot(user_id: int | str, target_id: int | str, chat_id: int | str) -> None | Message: #function is useless now...
    '''
    shoot a person
    
    :param user_id (int) - Telegram User ID of user that is shooting another user 
    :param target_id (int) - Telegram User ID of user that will be shooted
    
    :param chat_id (int) - Telegram Chat ID of chat in which messages will be sent 
    '''
    gun = cur.execute(f"SELECT gun FROM userdata WHERE user_id={user_id}").fetchone()

    if gun < 1:
        return await bot.send_message(chat_id, "<i>&#10060; У вас нет пистолета. Возможно, это к лучшему</i>")

    cur.execute(f"UPDATE userdata SET gun=gun-1 WHERE user_id={user_id}")
    conn.commit()

    rand = random.randint(100,200)
    if random.choice([True, False]):
        cur.execute(f"UPDATE userdata SET health=health-{rand} WHERE user_id={target_id}")
        conn.commit()

        await tglog(f"<i><b>{await utils.get_embedded_link(user_id)}</a></b> застрелил <b>{await utils.get_embedded_link(target_id)}</b>", "#user_gunshoot")
        await bot.send_message(chat_id, f"<i>&#128299; Вы застрелили <b>{await utils.get_embedded_link(target_id)}</b></i>")
        await bot.send_message(target_id, f"<i>&#128299; Вас застрелил <b>{await utils.get_embedded_link(user_id)}</b></i>")

        if random.choice([True, False]):
            cur.execute(f"UPDATE userdata SET prison={current_time() + 1200} WHERE user_id={user_id}")
            conn.commit()

            await bot.send_message(
                chat_id, 
                (
                    f"<i>&#128110; Господин <b>{await utils.get_embedded_link(target_id)}</b>, вы задержаны за убийство огнестрельным оружием. "
                    "Пройдёмте в отделение.\n\nВы были арестованы на <b>20 минут</b></i>"
                )
            )
        else:
            await bot.send_message(chat_id, f"<i>&#10060; Вы выстрелили мимо. Возможно, это к лучшему.\nПистолет потрачен зря</i>")


async def achieve(user_id: int | str, chat_id : int | str, achievement: str) -> None: #todo new ACHIEVEMENTS
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


async def cure(user_id: str, target_id: str, chat_id: str) -> None | Message: #function is useless now...
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
        mask = utils.get_mask(user_id)

        target_nick = cur.execute(f"SELECT nick FROM userdata WHERE user_id={target_id}").fetchone()
        target_mask = utils.get_mask(target_id)

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

