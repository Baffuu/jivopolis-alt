# type: ignore
# flake8: noqa

# ! I ignored the whole file because i'm not currently supporting it
import random
import asyncio

from datetime import datetime
from math import floor
from enum import IntEnum
import sqlite3
from typing import Union, Optional

from . import cur, conn
from .. import bot, logger, get_embedded_link, get_link, get_mask, tglog, utils
from ..misc import current_time, ITEMS, constants, ACHIEVEMENTS, RESOURCES
from ..misc.config import (
    limited_items, leveldesc,
    levelrange, ADMINS,
    clanitems, oscar_levels
)
from ..misc.constants import OfficialChats

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    User,
    Message
)
from aiogram.utils.text_decorations import HtmlDecoration


async def get_process(user_id: int | str) -> str:
    '''
    Get current process performed by the user.

    :param user_id - user's id:
    '''
    try:
        return cur.select("process", "userdata").where(
            user_id=user_id).one()

    except TypeError:
        if (
            message.chat.type == "private"
            and message.text.lower() != 'создать персонажа'
        ):
            cur.update("userdata").set(process="login").where(
                user_id=user_id).commit()
            return "login"
        return ""


async def can_interact(user_id: int | str) -> bool:
    '''
    Checks whether the user can interact with the bot.
    Returns false if the user is dead or banned.

    :param user_id - user's id:
    '''
    is_banned = bool(
        cur.select("is_banned", "userdata").where(
            user_id=user_id).one()
    )
    if is_banned:
        await bot.send_message(
            user_id,
            f'🧛🏻‍♂️ <i>Вы были забанены в боте. Если вы считаете, что эт'
            'о ошибка, обратитесь в <a href="'
            f'{OfficialChats.SUPPORTCHATLINK}">поддержку</a></i>'
        )

    is_dead = cur.select("health", "userdata").where(
        user_id=user_id).one() < 0
    if is_dead:
        await bot.send_message(
            user_id,
            '<i>☠️ Вы умерли. Попросите кого-нибудь вас воскресить</i>'
        )

    in_prison = cur.select("prison_started", "userdata").where(
        user_id=user_id).one() - current_time()
    is_in_prison = in_prison > 0
    if is_in_prison:
        minutes = int(in_prison / 60)
        seconds = int(in_prison % 60)
        await bot.send_message(
            user_id,
            f'👮‍♂️<i> Вы находитесь в тюрьме. До выхода вам осталось {minutes}'
            f' минут {seconds} секунд</i>'
        )
    
    return not (is_dead or is_banned or is_in_prison)


async def check(user_id: int | str, chat_id: int | str) -> None | Message:
    '''
    checks everything
    '''
    try:
        cur.update("userdata").set(lastseen=current_time()).where(user_id=user_id).commit()
        conn.commit()

        xp = cur.select("xp", "userdata").where(user_id=user_id).one()

        rank = cur.select("rank", "userdata").where(user_id=user_id).one()

        if user_id in ADMINS and rank < 2:
            cur.update("userdata").set(rank=3).where(user_id=user_id).commit()
            conn.commit()

        lastgears = current_time() - cur.select("last_gears", "userdata").where(user_id=user_id).one()

        if lastgears > 86400:
            cur.update("userdata").set(gears_today=0).where(user_id=user_id).commit()
            conn.commit()
            cur.update("userdata").set(last_gears=current_time()).where(user_id=user_id).commit()
            conn.commit()

        lvl = cur.select("level", "userdata").where(user_id=user_id).one()

        if lvl >= len(levelrange)-1:
            return
        elif xp >= levelrange[lvl] and xp < levelrange[lvl+1]:
            return
        for index, points in enumerate(levelrange):
            if (
                xp >= points
                and (index == len(levelrange) - 1
                or (xp < levelrange[index+1]
                and index < len(levelrange) - 1))
                and lvl != index
            ):
                cur.update("userdata").set(level=index).where(user_id=user_id).commit()
                conn.commit()
                description = leveldesc[index] if len(leveldesc) > index else ""
                try:
                    return await bot.send_message(
                        user_id,
                        f"<i>&#128305; Теперь ваш уровень в Живополисе: <b>{index}</b>\nПоздравляем!\n{description}</i>")
                except Exception:
                    return await bot.send_message(chat_id, f"<i>&#128305; Теперь ваш уровень в Живополисе: <b>{index}</b>\nПоздравляем!\n{description}</i>")

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
            if item in limited_items
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
    
    if heal == 1000:
        heal = random.randint(-100,10)
    elif heal == 900:
        heal = random.randint(-10,5)
    health = cur.select("health", "userdata").where(user_id=user_id).one()

    if health + heal > 100:
        return await call.answer('🧘 Вы недостаточно голодны для такой пищи', show_alert = True)

    food_amount = cur.select(food, "userdata").where(user_id=user_id).one()

    if food_amount < 1:
        return await call.answer(text="🚫 У вас нет такой еды", show_alert = True)

    cur.update("userdata").add(**{food: -1}).where(user_id=user_id).commit()
    # cur.update("userdata").add(health=heal).where(user_id=user_id).commit()
    cur.execute("UPDATE userdata SET health=health+? WHERE user_id=?", heal, user_id).commit()

    if heal > 0:
        await call.answer(f"❤ +{heal} HP на здоровье!", show_alert = True)
    else:
        await call.answer("🤢 Зачем я это съел? Теперь мне нехорошо", show_alert = True)
        await check_death(user_id, chat_id)


async def poison(message: Message) -> None | Message | bool:
    '''
    to use poison on a user 
    
    :param message = user:
    '''
    user_id = message.from_user.id
    target_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id

    if not cur.select("poison", "userdata").where(user_id=user_id).one():
        return await bot.send_message(chat_id, "<i>😥 У вас нет яда. Возможно, это к лучшему</i>")

    cur.update("userdata").add(poison=-1).where(user_id=user_id).commit()

    if random.choice([True, False]):
        return await bot.send_message(chat_id, "<i>😵‍💫 Неудача. Возможно, это к лучшему.\nЯд потрачен зря</i>")
    cur.update("userdata").add(health=-random.randint(50, 200)).where(user_id=target_id).commit()

    await tglog(f"<i><b>{await get_embedded_link(user_id)}</b> отравил <b>{await get_embedded_link(target_id)}</b></i>", "#user_poison")
    await bot.send_message(chat_id, f"<i>🧪 Вы отравили <b>{await get_embedded_link(target_id)}</b></i>")
    await bot.send_message(target_id, f"<i>🧪 Вас отравил <b>{await get_embedded_link(user_id)}</b></i>")
    await check_death(target_id, target_id)


async def shoot(message: Message) -> None | Message:
    '''
    shoot a person
    
    :param message - message of the user:
    '''
    user_id = message.from_user.id
    target_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    if not cur.select("gun", "userdata").where(user_id=user_id).one():
        return await bot.send_message(chat_id, "<i>🙅‍♂️ У вас нет пистолета. Возможно, это к лучшему</i>")

    cur.update("userdata").add(gun=-1).where(user_id=user_id).commit()

    if random.choice([True, False]):
        cur.update("userdata").add(health=-random.randint(100,200)).where(user_id=target_id).commit()

        await tglog(f"<i><b>{await get_embedded_link(user_id)}</b> застрелил <b>{await get_embedded_link(target_id)}</b></i>", "#user_gunshoot")
        await bot.send_message(chat_id, f"<i>😨 Вы застрелили <b>{await get_embedded_link(target_id)}</b></i>")
        await bot.send_message(target_id, f"<i>😓 Вас застрелил <b>{await get_embedded_link(user_id)}</b></i>")
        await check_death(target_id, target_id)

        if random.choice([True, True, False]):
            return await prison_sentence(message, 20, "убийство огнестрельным оружием")
        await achieve(user_id, chat_id, "shoot_achieve")
    else:
        await bot.send_message(chat_id, f"<i>😥 Вы выстрелили мимо. Возможно, это к лучшему.\nПистолет потрачен зря</i>")


async def prison_sentence(message: Message, term: int, reason: str, caption: str="") -> None:
    """
    put a user in prison

    :param message (Message) - user's message:
    :param term (int) - term of prison sentence (in minutes):
    :param reason (str) - the detention:
    :param caption (str) - text before the sentence description:
    """
    cur.update("userdata").set(prison_started=current_time() + term*60).where(
        user_id=message.from_user.id).commit()
    await message.answer(
        f"<i>{caption}\n\n👮‍♂️ Господин <b>{await get_embedded_link(message.from_user.id)}</b>, "
        f"вы были арестованы за {reason}. Пройдёмте в отделение.\n\nВы были арестованы на "
        f"<b>{term}</b> минут</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="😪 Скрыть сообщение",
                callback_data="cancel_action"
            )
        )
    )


async def achieve(user_id: int | str, chat_id : int | str, achievement: str) -> None:
    """
    achieve a user 
    
    :param user_id (int) - Telegram User ID of user that will be achieved 
    :param chat_id (int) - Telegram Chat ID of chat in which messages will be sent 
    :param achievement (str) - Index of achievement 
    """
    has_ach = cur.select(achievement, "userdata").where(user_id=user_id).one()

    if has_ach != 0:
        return

    achievement_data = ACHIEVEMENTS[achievement]
    name = achievement_data.ru_name
    desc = achievement_data.description
    money = achievement_data.money_reward
    points = achievement_data.xp_reward
    link = await get_embedded_link(user_id)

    if progress := achievement_data.progress:
        cur.select(progress, "userdata").where(user_id=user_id).one()
        cur.update("userdata").add(**{progress: 1}).where(user_id=user_id).commit()
        current_progress = cur.select(progress, "userdata").where(user_id=user_id).one()
        if current_progress < achievement_data.completion_progress:
            return

    cur.select(achievement, "userdata").where(user_id=user_id).one()
    cur.update("userdata").set(**{achievement: 1}).where(user_id=user_id).commit()
    cur.select(achievement, "userdata").where(user_id=user_id).one()

    if money:
        cur.update("userdata").add(balance=money).where(user_id=user_id).commit()
    if points:
        cur.update("userdata").add(xp=points).where(user_id=user_id).commit()

    chat = await bot.get_chat(chat_id)
    mention = "У вас новое достижение" if chat.type == "private" else f"<b>{link}</b>, у вас новое достижение"
    await bot.send_message(chat_id, f"<i>{mention}: <b>{name}</b>\n{desc}. \nВаша награда: <b>${money}</b> и 💡 <b>{points}</b> очков</i>")
    
    if special_reward := achievement_data.special_reward:
        item = ITEMS[special_reward]
        item_name = item.ru_name
        emoji = item.emoji
        cur.update("userdata").add(**{special_reward: 1}).where(user_id=user_id).commit()
        await bot.send_message(chat_id, f"<i>За выполнение достижения вы получаете <b>{emoji} {item_name}</b></i>")
    
    if achievement != "all_achieve":
        for achievement in ACHIEVEMENTS:
            has_ach = cur.select(achievement, "userdata").where(user_id=user_id).one()
            if not has_ach and achievement != "all_achieve":
                return
        await achieve(user_id, chat_id, "all_achieve")



async def cure(user_id: str, target_id: str, chat_id: str) -> None | Message:
    '''
    Cure a player.

    :param user_id - id of the user trying to heal:
    :param target_id - id of the user being healed:
    :param chat_id - id of the chat where the healing is executed:
    '''
    if target_id == user_id:  # executes if the user is trying to heal themselves
        return await bot.send_message(chat_id, "<i>😠 Нельзя вылечить самого себя</i>")

    if cur.select("pill", "userdata").where(user_id=user_id).one() < 1:  # executes if the user has no pills
        return await bot.send_message(chat_id, "<i>😥 У вас нет таблеток :(</i>")

    health = cur.select("health", "userdata").where(user_id=target_id).one()
    target_link = f"<b>{await get_embedded_link(target_id)}</b>"

    if health > 0 and health < 100:  # executes if the target user is injured but alive
        print(cur.select("health", "userdata").where(user_id=target_id).one())  # idk what it is but the code doesn't work without it
        cur.update("userdata").add(health=random.randint(1, 100-health)).where(user_id=target_id).commit()
        print(cur.select("health", "userdata").where(user_id=target_id).one())  # idk what it is but the code doesn't work without it

        await bot.send_message(chat_id, f"<i>🎉 Успех! Вы вылечили {target_link}</i>")
        await bot.send_message(target_id, f"<i>😎 Вас вылечил <b>{await get_embedded_link(user_id)}</b></i>")

    elif health >= 100:  # executes if the target user is already healthy
        return await bot.send_message(chat_id, f"<i>🤨 Пациент полностью здоров, зачем вам тратить лекарства впустую?\nЛекарства <b>не потрачены</b></i>")

    else:  # executes if the target user is dead
        print(cur.select("health", "userdata").where(user_id=target_id).one())  # idk what it is but the code doesn't work without it
        cur.update("userdata").add(health=random.randint(50, 100)).where(user_id=target_id).commit()
        print(cur.select("health", "userdata").where(user_id=target_id).one())  # idk what it is but the code doesn't work without it

        await bot.send_message(chat_id, f"<i>🎉 Успех! Вы воскресили {target_link}</i>")
        await bot.send_message(target_id, f"<i>😎 Вас воскресил <b>{await get_embedded_link(user_id)}</b></i>")

        await achieve(user_id, chat_id, "rescue_achieve")

    print(cur.select("pill", "userdata").where(user_id=user_id).one())  # idk what it is but the code doesn't work without it
    cur.update("userdata").add(pill=-1).where(user_id=user_id).commit()
    print(cur.select("pill", "userdata").where(user_id=user_id).one())  # idk what it is but the code doesn't work without it
    await achieve(user_id, chat_id, "heal_achieve")
    

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
            f"<i><b>{await get_embedded_link(user_id)}</b> {f'[{rank}]' or ''}"
            f"\n🌟<b>{level} 💖 {health} 💡{xp}  💸 {balance}</b>"
            f"\n{random.choice(constants.TIME_EMOJIS)} Был(-а) <b>{lastseen}</b>"
            f"\n🎞 Aккаунт создан: <b>{register_date} {inviter}</b>"
            f"\n\n<i>{description}</i>"
            f"\n\n🛡 Клан: <b>{(HtmlDecoration().link(str(clan_name), str(clan_link)) if clan_type == 'public' else clan_name) if clan_id is not None else 'отсутствует'}</b></i>"
        )
        if photo:
            return await message.reply_photo(photo, PROFILE_TEXT, reply_markup=markup)
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

    cur.update("userdata").add(balance=money).where(user_id=user_id).commit()


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


async def buy_in_oscar_shop(call: CallbackQuery, item: str):
    '''
    Buy an item in Oscar's shop.
    
    :param call (aiogram.types.CallbackQuery) - callback:
    :param item (str) - item that will be bought:
    '''
    user_id = call.from_user.id
    if item not in ITEMS:
        raise ValueError("no such item")
    item_data = ITEMS[item]
    if not item_data.tags[0].startswith("OSCAR_SHOP_"):
        raise ValueError("this item isn't sold in Oscar's shop")
    if cur.select("current_place", "userdata").where(
            user_id=user_id).one() != "Попережье":
        return await call.answer(
                text=(
                    '🦥 Не пытайтесь обмануть Живополис, вы уже уехали из этой '
                    'местности'
                ),
                show_alert=True
            )

    currency = item_data.tags[0].replace("OSCAR_SHOP_", "").lower()
    if cur.select("oscar_purchases", "userdata").where(
            user_id=user_id).one() < oscar_levels[currency]:
        return await call.answer(
            "😑 Вы ещё не достигли такого уровня в ларьке. "
            "Покупайте больше товаров у дяди Оскара!"
        )

    cost = ITEMS[item].cost // RESOURCES[currency].cost
    if not cost or cost < 0:
        return

    balance = cur.select(currency, "userdata").where(user_id=user_id).one()
    if balance < cost:
        return await call.answer('😥 У вас недостаточно ресурсов', show_alert = True)

    cur.update("userdata").add(**{item: 1}).where(user_id=user_id).commit()
    cur.update("userdata").add(**{currency: -cost}).where(user_id=user_id).commit()
    if ITEMS[item].type == 'car':
        await achieve(
            user_id, call.message.chat.id, 'auto_achieve'
        )

    await call.answer(
        f'Покупка прошла успешно. У вас {balance-cost} единиц ресурса',
        show_alert = True
    )
    await increase_oscar_level(call)


async def increase_oscar_level(call: CallbackQuery):
    '''
    Increase Oscar's shop level if needed
    
    :param call (aiogram.types.CallbackQuery) - callback:
    '''
    user_id = call.from_user.id
    cur.update("userdata").add(oscar_purchases=1).where(user_id=user_id).commit()
    purchases = cur.select("oscar_purchases", "userdata").where(
                    user_id=user_id).one()
    for level in oscar_levels:
        if oscar_levels[level] == purchases:
            level_name = RESOURCES[level].ru_name
            if level == 'topaz':
                await achieve(
                    user_id, call.message.chat.id, 'oscar_achieve'
                )
            return await call.message.answer(
                "🥳 <i>Ваши отношения с дядей Оскаром улучшены до уровня "
                f"<b>{level_name}</b></i>",
                reply_markup=InlineKeyboardMarkup().add(
                    cancel_button("👌 Хорошо")
                )
            )


def cancel_button(text: str="◀ Назад", cancel_process: bool=False) -> InlineKeyboardButton:
    '''
    An inline button which deletes the call message.
    '''
    return InlineKeyboardButton(
        text=text,
        callback_data="cancel_process" if cancel_process else "cancel_action"
    )


class Weather(IntEnum):
    SUNNY = 0
    CLOUDY = 1
    RAINING = 2
    SNOWY = 3
    THUNDERSTORM = 4
    HURRICANE = 5


def get_weather(day: int = 0) -> Weather:
    '''
    Get weather depending on given time.

    :param day - day to check the weather:
    '''
    return Weather(int(cur.select("weather", "globaldata").one()[day]))


def str_weather(weather: Weather) -> str:
    match (weather):
        case Weather.SUNNY:
            return "☀ Ясно"
        case Weather.CLOUDY:
            return "⛅ Облачно"
        case Weather.RAINING:
            return "🌧 Дождь"
        case Weather.SNOWY:
            return "🌨 Снег"
        case Weather.THUNDERSTORM:
            return "⛈ Гроза"
        case Weather.HURRICANE:
            return "🌪 Ураган"


def month(month_number: int) -> str:
    match month_number:
        case 1:
            return "января"
        case 2:
            return "февраля"
        case 3:
            return "марта"
        case 4:
            return "апреля"
        case 5:
            return "мая"
        case 6:
            return "июня"
        case 7:
            return "июля"
        case 8:
            return "августа"
        case 9:
            return "сентября"
        case 10:
            return "октября"
        case 11:
            return "ноября"
        case 12:
            return "декабря"
        case _:
            return ""


async def damage_player(user_id: int|str, chat_id: int|str, damage: int,
                        message: Optional[str] = None):
    '''
    Damage a player.

    :param user_id - user to check:
    :param chat_id - chat to send the result:
    :param damage - amount or health points to be substracted:
    :param message - message sent to the chat:
    '''
    cur.update("userdata").add(health=-damage).where(user_id=user_id).commit()
    if message:
        await bot.send_message(
            chat_id,
            f"<i>{message}.\n\n💔 Вам был нанесён урон в <b>{damage}</b> единиц здоровья</i>"
        )
    await check_death(user_id, chat_id)


async def check_death(user_id: int|str, chat_id: int|str):
    '''
    Check whether the player is dead.

    :param user_id - user to check:
    :param chat_id - chat to send the result:
    '''
    if cur.select("health", "userdata").where(user_id=user_id).one() <= 0:
        await bot.send_message(
            chat_id,
            "<i>☠ Вы умерли. Попросите кого-нибудь вас воскресить</i>"
        )


async def weather_damage(user_id: int|str, chat_id: int|str) -> bool | None:
    '''
    Damage a player due to the weather.

    :param user_id - user to check:
    :param chat_id - chat to send the result:
    '''
    match get_weather():
        case Weather.RAINING:
            chance = 1
            message = "💧 Вы поскользнулись на мокрой земле и упали"
            damage = random.randint(1, 10)
        case Weather.SNOWY:
            chance = 3
            message = "❄ Вы поскользнулись на льду и упали"
            damage = random.randint(5, 20)
        case Weather.THUNDERSTORM:
            chance = 7
            message = "⚡ В вас попала молния"
            damage = random.randint(60, 100)
        case Weather.HURRICANE:
            chance = 20
            message = "🌀 Вы пострадали из-за урагана"
            damage = random.randint(40, 100)
        case _:
            return False
    if random.uniform(0, 100) <= chance:
        await damage_player(user_id, chat_id, damage, message)
        return True
    return False


async def update_weather():
    '''
    Update weather for the next 7 days
    '''
    if current_time() - cur.select("last_weather", "globaldata").one() < 86400:
        return

    # get weather for 6 days starting from today
    current_weather = cur.select("weather", "globaldata").one()[1:]

    # check whether the 7th day is in winter
    is_winter = datetime.fromtimestamp(current_time() + 86400*6).month in [1, 2, 12]

    # get weather for the 7th day
    random_index = random.randint(1, 100)
    if random_index <= 2:
        weather_day7 = Weather['HURRICANE']
    elif random_index <= (3 if is_winter else 7):
        weather_day7 = Weather['THUNDERSTORM']
    elif random_index <= 25:
        weather_day7 = Weather['SNOWY' if is_winter else 'RAINING']
    elif random_index <= 60:
        weather_day7 = Weather['SUNNY']
    else:
        weather_day7 = Weather['CLOUDY']
    
    today = datetime.now()
    today_morning = datetime(today.year, today.month, today.day, 0, 0, 0)
    cur.update("globaldata").set(last_weather=time_seconds(today_morning)).commit()
    cur.update("globaldata").set(weather=current_weather + str(weather_day7)).commit()


def time_seconds(time: datetime) -> int:
    '''
    Convert datetime to seconds integer.
    '''
    return (time - datetime.fromtimestamp(0)).total_seconds()
