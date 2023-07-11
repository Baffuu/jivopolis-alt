# type: ignore
# flake8: noqa

# ! I ignored the whole file because i'm not currently supporting it
import random
import asyncio

from datetime import datetime
from math import floor
import sqlite3
from typing import Union, Optional

from . import cur, conn
from .. import bot, logger, get_embedded_link, get_link, get_mask, tglog, utils
from ..misc import current_time, ITEMS, constants
from ..misc.config import (
    limeteds, leveldesc,
    levelrange, ach, ADMINS,
    clanitems
)

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    User,
    Message
)
from aiogram.utils.text_decorations import HtmlDecoration


async def check(user_id: int | str, chat_id: int | str) -> None | Message:
    '''
    checks everything
    '''
    try:
        cur.execute(
            "UPDATE userdata SET "
            f"lastseen={current_time()} WHERE user_id={user_id}"
        )
        conn.commit()

        xp = cur.execute(
            f"SELECT xp FROM userdata WHERE user_id={user_id}"
        ).fetchone()[0]

        rank = cur.execute(
            f"SELECT rank FROM userdata WHERE user_id={user_id}"
        ).fetchone()[0]

        if user_id in ADMINS and rank < 2:
            cur.execute(f"UPDATE userdata SET rank=3 WHERE user_id={user_id}")
            conn.commit()

        lastgears = current_time() - cur.select("last_gears", "userdata").where(user_id=user_id).one()

        if lastgears > 86400:
            cur.update("userdata").set(gears_today=0).where(user_id=user_id).commit()
            conn.commit()
            cur.update("userdata").set(last_gears=current_time()).where(user_id=user_id).commit()
            conn.commit()

        lvl = cur.execute(
            f"SELECT level FROM userdata WHERE user_id={user_id}"
        ).fetchone()[0]

        if lvl >= len(levelrange)-1:
            return
        elif xp >= levelrange[lvl] and xp < levelrange[lvl+1]:
            return
        for i in levelrange:
            if (
                xp >= i 
                and levelrange.index(i) >= len(levelrange) - 1 
                and lvl != levelrange.index(i)
            ):
                cur.execute(f"UPDATE userdata SET level={levelrange.index(i)} WHERE user_id={user_id}")
                conn.commit()
                try:
                    return await bot.send_message(
                        user_id, 
                        f"<i>&#128305; Теперь ваш уровень в Живополисе: <b>{levelrange.index(i)}</b>\nПоздравляем!\n{leveldesc[levelrange.index(i)]}</i>")
                except Exception:
                    return await bot.send_message(chat_id, f"<i>&#128305; Теперь ваш уровень в Живополисе: <b>{levelrange.index(i)}</b>\nПоздравляем!\n{leveldesc[levelrange.index(i)]}</i>")

            if xp>=i and xp<levelrange[levelrange.index(i)] and lvl!=levelrange.index(i):
                cur.execute("UPDATE userdata SET level=? WHERE user_id=?", (levelrange.index(i), user_id,))
                conn.commit()
                try:
                    return await bot.send_message(user_id, f"<i>&#128305; Теперь ваш уровень в Живополисе: <b>{levelrange.index(i)}</b>\nПоздравляем!\n{leveldesc[levelrange.index(i)]}</i>")
                except Exception:
                    return await bot.send_message(chat_id, f"<i>&#128305; Теперь ваш уровень в Живополисе: <b>{levelrange.index(i)}</b>\nПоздравляем!\n{leveldesc[levelrange.index(i)]}</i>")

    except Exception as e:
        logger.exception(e)


async def itemdata(
    user_id: int, item: str
) -> Union[str, None, InlineKeyboardButton]:
    """
    :param user_id - telegram user ID
    :param item - item slot name

    :returns aiogram.types.InlineKeyboardButton - button with item icon && itemcount
    """
    try:
        items = cur.select(item, "userdata").where(user_id=user_id).one()

        if not isinstance(items, int):
            items = 0

        if items > 0:
            return InlineKeyboardButton(text=f"{ITEMS[item].emoji} {items}", callback_data=item)

        else:
            return "emptyslot"
    except sqlite3.OperationalError:
        return None
    except Exception as e:
        return logger.exception(e)


def buybutton(
    item: str,
    status: str | None = None,
    tip: int = 0
) -> Union[InlineKeyboardButton, None]:
    '''
    You can get special button for buying something

    :param item (str) - item index that will be bought
    :param status (str) - (Optional) special index for buying category
    :param tip (int) - (Optional) additional money to price

    :returns: None if item does not exists or an error occured; aiogram.types.InlineKeyboardButton
    '''
    amount = ''
    if len(item.split(" ")) > 1:
        amount = item.split(" ")[1][1:]
        item = item.split(" ")[0]
    
    if item not in ITEMS:
        return None
    itemob = ITEMS[item]

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
        if amount != '':
            return InlineKeyboardButton(f'{itemob.emoji} {itemob.ru_name} x{amount} - ${cost * int(amount)}', callback_data=f"buy_{item}:0:{amount}")
        return InlineKeyboardButton(f'{itemob.emoji} {itemob.ru_name} - ${cost}', callback_data=f'buy_{item}:{tip}')
    else:
        return (
            InlineKeyboardButton(
                f'{itemob.emoji} {itemob.ru_name} - ${cost}', callback_data=f'buy24_{item}'
            )
            if item in limeteds
            else None
        )


async def eat(call: CallbackQuery, food: str) -> None | bool | Message:
    '''
    :param call (aiogram.types.CallbackQuery) - aiogram callback query
    :food (str) - food index 
    
    :raise ValueError if food does not exists
    '''

    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if food in ITEMS:
        heal = int(ITEMS[food].type_param) # type: ignore    
    else:
        raise ValueError('no such food')

    health = cur.execute(f"SELECT health FROM userdata WHERE user_id={user_id}").one()
    
    if heal == 1000:
        heal = random.randint(-100,10)
    if heal == 900:
        heal = random.randint(-10,5)

    if health + heal > 100:
        return await call.answer('🧘 Вы недостаточно голодны для такой пищи', show_alert = True)
            
    health = cur.execute(f"SELECT health FROM userdata WHERE user_id={user_id}").one()
    food_amount = cur.execute(f"SELECT {food} FROM userdata WHERE user_id={user_id}").one()

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
        health = cur.execute(f"SELECT health FROM userdata WHERE user_id={user_id}").one()

        if health < 1:
            return await bot.send_message(chat_id, "<i>&#9760; Вы умерли</i>")


async def poison(user: User, target_id: int | str, chat_id: int| str) -> None | Message | bool:
    '''
    to use poison on a user 
    
    :param user (aiogram.types.User) - user that is poisoning another user 
    :param target_id (int) - telegram user ID of user that will be poisoned 
    :chat_id chat_id (int) - telegram chat ID to which messages will be sent 
    '''

    try:
        my_health = cur.select("health", "userdata").where(user_id=user.id).one()

        if my_health < 0:
            return await bot.send_message(chat_id, "<i>&#9760; Вы умерли. Попросите кого-нибудь вас воскресить</i>")

        poison = cur.execute(f"SELECT poison FROM userdata WHERE user_id={user.id}").one()

        if poison < 1:
            return await bot.send_message(chat_id, "<i>&#10060; У вас нет яда. Возможно, это к лучшему</i>")

        cur.execute(f"UPDATE userdata SET poison=poison-1 WHERE user_id={user.id}")
        conn.commit()

        random_damage = random.randint(50, 200)
        if random.choice([True, False]):
            cur.execute(f"UPDATE userdata SET health=health-{random_damage} WHERE user_id={target_id}")
            conn.commit()

            await tglog(f"<i><b>{await get_embedded_link(user.id)}</b> отравил <b>{await get_embedded_link(target_id)}\"</b></i>.", "#user_poison")
            await bot.send_message(chat_id, f"<i>🧪 Вы отравили <b>{await get_embedded_link(target_id)}</b></i>")
            await bot.send_message(target_id, f"<i>🧪 Вас отравил <b>{await get_embedded_link(user.id)}</b></i>")
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

        await tglog(f"<i><b>{await get_embedded_link(user_id)}</a></b> застрелил <b>{await get_embedded_link(target_id)}</b>", "#user_gunshoot")
        await bot.send_message(chat_id, f"<i>&#128299; Вы застрелили <b>{await get_embedded_link(target_id)}</b></i>")
        await bot.send_message(target_id, f"<i>&#128299; Вас застрелил <b>{await get_embedded_link(user_id)}</b></i>")

        if random.choice([True, False]):
            cur.execute(f"UPDATE userdata SET prison={current_time() + 1200} WHERE user_id={user_id}")
            conn.commit()

            await bot.send_message(
                chat_id, 
                (
                    f"<i>&#128110; Господин <b>{await get_embedded_link(target_id)}</b>, вы задержаны за убийство огнестрельным оружием. "
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

class profile_():
    def __init__(self, dont_init: bool = False, user_id: Optional[int] = None, message: Optional[Message] = None, called: bool = False) -> None:
        if (
            dont_init 
            or not user_id 
            or not message
        ):
            return
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init_(user_id, message, called))

    async def init_(self, user_id: int, message: Message, called: bool = False):
        # sourcery skip: remove-unreachable-code
        profile_type = cur.select("profile_type", "userdata").where(user_id=user_id).one()

        if profile_type == "private" and user_id != message.from_user.id and not called:
            return await message.answer(f"🚫 <i><b>{await get_embedded_link(user_id)}</b> скрыл свой профиль</i>")

        clan_id = cur.select("clan_id", "userdata").where(user_id=user_id).one()
        
        balance, inviter, description, xp, rank, health, level, lastseen, photo, register_date,\
        clan_id, clan_type, clan_link, clan_name = await self._get_everything(user_id, clan_id)
        

        if health < 0:
            health = "<b>мёртв</b>"

        markup = InlineKeyboardMarkup(row_width=2)

        if (message.chat.type == "private" and message.from_user.id == user_id) or called:
            markup = self._add_setting_buttons(markup)

        PROFILE_TEXT = (
            f"{await get_embedded_link(user_id)} {f'[{rank}]' or ''}"
            f"\n🌟{level} 💖 {health} 💡{xp}  💸 {balance}"
            f"\n{random.choice(constants.TIME_EMOJIS)} Был(-а) {lastseen}"
            f"\n🎞 Aккаунт создан: {register_date} {inviter}"
            f"\n\n<i>{description}</i>"
            f"\n\n🛡 Клан: <b>{(HtmlDecoration().link(str(clan_name), str(clan_link)) if clan_type == 'public' else clan_name) if clan_id is not None else 'отсутствует'}</b>"
        )
        if photo:
            return await message.reply_photo(photo, PROFILE_TEXT)
        await message.reply(PROFILE_TEXT, reply_markup=markup)


    def _add_setting_buttons(self, markup):
        markup.add(
                InlineKeyboardButton(
                    text="💡 Достижения", 
                    callback_data="achievements"
                ),
                InlineKeyboardButton(
                    text="⚙ Настройки", 
                    callback_data="user_settings"
                ),
                InlineKeyboardButton(
                    text="🖇 Реферальная ссылка", 
                    callback_data="my_reflink"
                )
        ).add(
                InlineKeyboardButton(
                    text="👥 Привлечённые пользователи", 
                    callback_data="refusers"
                )
            )
        return markup


    async def _get_everything(self, user_id, clan_id):
        balance = cur.select("balance", "userdata").where(user_id=user_id).one()
        invited_by = cur.select("inviter_id", "userdata").where(user_id=user_id).one()
        inviter = f"\n📎 Пригласивший пользователь: <b>{await get_embedded_link(invited_by)}</b>" if invited_by != 0 else ''
        description = cur.select("description", "userdata").where(user_id=user_id).one()
        xp = cur.select("xp", "userdata").where(user_id=user_id).one()
        rank = cur.select("rank", "userdata").where(user_id=user_id).one()
        health = cur.select("health", "userdata").where(user_id=user_id).one()
        level = cur.select("level", "userdata").where(user_id=user_id).one()
        lastseen = cur.select("lastseen", "userdata").where(user_id=user_id).one()
        photo = cur.select("photo_id", "userdata").where(user_id=user_id).one()
        rank = self._get_rank_name(rank)
        seconds = current_time() - lastseen
        lastseen = self._get_lastseen(seconds)
        register_date = self._get_register_date(user_id)
        clan_id, clan_type, clan_link, clan_name = self._get_clan(clan_id)

        return (
            balance, inviter, description,
            xp, rank, health, level,
            lastseen, photo, register_date, 
            clan_id, clan_type, clan_link, clan_name
        )


    def _get_register_date(self, user_id):
        try:
            register_date = datetime.fromtimestamp(cur.select("register_date", "userdata").where(user_id=user_id).one())
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
        return register_date


    def _get_lastseen(self, seconds):
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
        return lastseen


    def _get_clan(self, clan_id):
        if clan_id != 0 and clan_id:
            if (
                cur.execute(
                    f"SELECT count(*) FROM clandata WHERE clan_id={clan_id}"
                ).fetchone()[0]
                == 0
            ):
                return None, None, None, None
            clan_type = cur.select("clan_type", "clandata").where(clan_id=clan_id).one()
            clan_link = cur.select("link", 'clandata').where(clan_id=clan_id).one()
            clan_name = cur.select("clan_name", "clandata").where(clan_id=clan_id).one()
            return clan_id, clan_type, clan_link, clan_name
        return None, None, None, None


    def _get_rank_name(self, rank):
        match (rank):
            case 0:
                rank = None
            case 1:
                rank = "⚜️ VIP"
            case 2:
                rank = "🛠 Админ"
            case 3:
                rank = "👑 Создатель"
            case _:
                rank = '👽 Undefined'
        return rank

profile = profile_(dont_init=True).init_ # async version of profile_

async def earn(money: int, message: Message | None = None, user_id: int | None = None) -> None:
    '''
    To give money to a user 

    :param money (int) - how many money will be given
    :param user_id (int) -  Telegram User ID of user to which money will be given
    '''
    if not message and not user_id:
        raise ValueError("You must provide either message or user_id")
    elif not message:
        pass
    elif not user_id:
        user_id = message.from_user.id

    cur.execute(f"UPDATE userdata SET balance = balance+{money} WHERE user_id = {user_id}")
    conn.commit()


async def buy(call: CallbackQuery, item: str, user_id: int, cost: Optional[int] = None, amount: int = 1):
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
        cost = ITEMS[item].cost
        if not cost or cost < 0:
            return

    balance = cur.select("balance", "userdata").where(user_id=user_id).one()

    if balance >= cost*amount:
        cur.execute(f"UPDATE userdata SET {item} = {item} + {amount} WHERE user_id = {user_id}"); conn.commit()

        cur.execute(f"UPDATE userdata SET balance = balance - {cost*amount} WHERE user_id = {user_id}"); conn.commit()

        await call.answer(f'Покупка прошла успешно. Ваш баланс: ${balance-cost*amount}', show_alert = True)

        cur.execute(f"UPDATE globaldata SET treasury=treasury+{cost*amount//2}"); conn.commit()
    else:
        await call.answer('🚫 У вас недостаточно денег', show_alert = True)
