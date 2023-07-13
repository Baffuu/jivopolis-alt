from datetime import datetime
from .config import intervals

from typing import Union, Tuple, Optional
from math import ceil

from .constants import OfficialChats
from .. import logger, bot
from ..database import cur

from aiogram.types import InlineKeyboardButton, Message
from aiogram.utils.deep_linking import decode_payload


async def get_link(
    user_id: Optional[int | str] = None,
    encoded_id: Optional[str] = None
) -> str:
    '''
    get link to user profile in the bot

    :param user_id:
    :param encoded_id - encoded user id:

    :returns - bot link of the user:

    :raise ValueError if no arguments will be provided.
    '''
    if not user_id and not encoded_id:
        raise ValueError('there is no user id and no encoded user id.')
    if encoded_id and not user_id:
        user_id = decode_payload(encoded_id)
    me = await bot.get_me()

    return f"https://t.me/{me.username}?start={user_id}"


async def get_embedded_link(
    user_id: str | int,
    nick: str | None = None,
    include_mask: bool = True
) -> str:
    if not nick:
        nick = cur.select("nickname", "userdata").where(user_id=user_id).one()
    return (
        f"<a href='{await get_link(user_id)}'>"
        f"{get_mask(user_id) if include_mask else ''}{nick}</a>"
    )


def get_mask(user_id: int | str) -> Union[str, None]:
    '''
    get mask or race of user

    :param user_id:

    :returns - the mask worn by the user or their race:
    '''
    try:
        return (
            cur.execute(
                f"SELECT mask FROM userdata WHERE user_id = {user_id}"
            ).fetchone()[0]
            or cur.execute(
                f"SELECT rase FROM userdata WHERE user_id = {user_id}"
            ).fetchone()[0]
        )
    except TypeError as e:
        logger.exception(e)
        return cur.execute(
            f"SELECT rase FROM userdata WHERE user_id = {user_id}"
        ).fetchone()[0]
    except Exception as e:
        return logger.exception(e)


def current_time() -> float:
    '''returns current Unix time in seconds'''
    return (datetime.now()-datetime.fromtimestamp(0)).total_seconds()


def isinterval(type: str) -> bool:
    '''returns True if boarding given type of transport
    is available; else False'''
    now = current_time()
    interval = intervals[type]
    return now // 1 % interval[0] <= interval[1]


def remaining(type) -> str:
    '''returns time remaining until boarding given type of transport
    becomes available, in minutes and seconds'''
    now = current_time()
    interval = intervals[type][0]
    seconds = int(interval - now // 1 % interval)
    min, sec = divmod(seconds, 60)
    sec = f"{sec} секунд" if sec != 0 else ""
    return f'{f"{min} минут " if min != 0 else ""}{sec}'


def get_time_units(time: float) -> Tuple[int, int, int]:
    '''
    :param time: - enter time in seconds

    :returns (hours, minutes, seconds)'''
    hours = int(24-ceil(time / 3600))
    minutes = int(60-ceil(time % 3600 / 60))
    seconds = int(60-ceil(time % 3600 % 60))

    return hours, minutes, seconds


def get_building(place: str) -> InlineKeyboardButton | None:
    '''
    Get InlineKeyboardButton with special building for every location

    :param place:

    :returns `aiogram.types.InlineKeyboardButton`
    '''
    match (place):
        case "Ботаническая":
            button = InlineKeyboardButton(
                text="🌲 Живополисский ботанический сад",
                callback_data="botan_garden_shop"
            )
        case "Живбанк":
            button = InlineKeyboardButton(
                text="🏦 Живополисский банк",
                callback_data="bank")
        case "Университет":
            button = InlineKeyboardButton(
                text="🏫 Живополисский университет",
                callback_data="university"
            )
        case "Ридипольская гимназия":
            button = InlineKeyboardButton(
                text="🏫 Ридипольская районная гимназия",
                callback_data="university"
            )
        case "Котайский Мединститут":
            button = InlineKeyboardButton(
                text="🏫 Котайский институт медицинских наук",
                callback_data="university"
            )
        case "Автопарк им. Кота":
            button = InlineKeyboardButton(
                text="🚗 Автопарк имени Cat Painted",
                callback_data="car_shop"
            )
        case "ТЦ МиГ":
            button = InlineKeyboardButton(
                text="🏬 Торговый центр МиГ",
                callback_data="mall"
            )
        case "Георгиевская":
            button = InlineKeyboardButton(
                text="🍰 Кондитерская \"СладкоЁжка\"",
                callback_data="candy_shop"
            )
        case "Райбольница":
            button = InlineKeyboardButton(
                text="🏥 Живополисская районная больница",
                callback_data="hospital_shop"
            )
        case "Старокотайский ФАП":
            button = InlineKeyboardButton(
                text="🏥 Старокотайский фельдшерский пункт",
                callback_data="hospital_shop"
            )
        case "Жабинка (больница)":
            button = InlineKeyboardButton(
                text="🏥 Жабинская городская больница",
                callback_data="hospital_shop"
            )
        case "Ридипольская райбольница":
            button = InlineKeyboardButton(
                text="🏥 Ридипольская районная больница",
                callback_data="hospital_shop"
            )
        case "Зоопарк":
            button = InlineKeyboardButton(
                text="🦊 Живополисский зоопаcрк",
                callback_data="zoo_shop"
            )
        case "Аэропорт Ридиполь":
            button = InlineKeyboardButton(
                text="✈ Аэропорт Ридиполь",
                callback_data="airport"
            )
        case "Национальный аэропорт":
            button = InlineKeyboardButton(
                text="✈ Национальный аэропорт Живополис",
                callback_data="airport"
            )
        case "Живополисский музей":
            button = InlineKeyboardButton(
                text="🏛 Исторический музей Живополиса",
                callback_data="museum"
            )
        case "Макеевка":
            button = InlineKeyboardButton(
                text="🍏 \"Натурал\". Фрукты и овощи",
                callback_data="fruit_shop"
            )
        case "Рынок":
            button = InlineKeyboardButton(
                text="🏣 Центральный рынок",
                callback_data="central_market_menu"
            )
        case "Котайский электрозавод":
            button = InlineKeyboardButton(
                text="🏭 Котайский завод электрических деталей",
                callback_data="factory"
            )
        case "Ридипольский завод":
            button = InlineKeyboardButton(
                text="🏭 Завод Transit Ридиполь",
                callback_data="factory"
            )
        case "Стадион":
            button = InlineKeyboardButton(
                text="🏟 Живополис-Арена",
                url="t.me/jivopolistour"
            )
        case "Роща":
            button = InlineKeyboardButton(
                text="🌾 Ферма",
                callback_data="farm"
            )
        case "Посёлок Горный":
            button = InlineKeyboardButton(
                text="🏔 Агзамогорские шахты",
                callback_data="mineshaft"
            )
        case "Агзамогорск":
            button = InlineKeyboardButton(
                text="⛏ Магазин шахтёра",
                callback_data="pickaxe_shop"
            )
        case "Генерала Шелби":
            button = InlineKeyboardButton(
                text="📱 Магазин техники имени Шелби",
                callback_data="phone_shop"
            )
        case "Глинянка":
            button = InlineKeyboardButton(
                text="🏬 Центр сбора полезных ископаемых",
                callback_data="resource_market"
            )
        case 'Максименка':
            button = InlineKeyboardButton(
                text='🧱 Строительный магазин',
                callback_data='building_shop'
            )
        case "Площадь Админов":
            button = InlineKeyboardButton(
                "📊 Биржа",
                callback_data="exchange_center"
            )
        case "Админская улица":
            button = InlineKeyboardButton(
                "☕️ Подать админам на чай",
                callback_data="donate"
            )
        case _:
            return None
    return button


async def log_to_telegram(message: str, tag: str) -> Message:
    return await bot.send_message(
        OfficialChats.LOGCHAT,
        f"{message} | <i>{tag}</i>"
    )


tglog = log_to_telegram  # alias for telegram logger
