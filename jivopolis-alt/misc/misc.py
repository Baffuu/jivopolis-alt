from datetime import datetime
from ..config import intervals, BOT_USER

from typing import Union

from .. import logger
from ..database.sqlitedb import cur

from aiogram.types import InlineKeyboardButton
from aiogram.utils.deep_linking import decode_payload

def get_link(user_id: int = None, encoded_id: str = None) -> str:
    '''get link to user profile in bot'''
    if not user_id and not encoded_id:
        raise ValueError('there is no user id and no encoded user id.')
    if encoded_id:
        user_id = decode_payload(encoded_id)
    return f"{BOT_USER}?start={user_id}"

def get_mask(user_id: int) -> Union[str, None]:
    '''get mask or rase of user'''
    try:
        mask = cur.execute(f"SELECT mask FROM userdata WHERE user_id = {user_id}").fetchone()[0]
        if not mask:
            mask = cur.execute(f"SELECT rase FROM userdata WHERE user_id = {user_id}").fetchone()[0]
        return mask
    except TypeError as e:
        logger.exception(e)
        mask = cur.execute(f"SELECT rase FROM userdata WHERE user_id = {user_id}").fetchone()[0]
        return mask
    except Exception as e:
        return logger.exception(e)

def current_time() -> float:
    """returns current time in seconds"""
    return (datetime.now()-datetime.fromtimestamp(0)).total_seconds()

def isinterval(type) -> bool:
    #todo description
    now = current_time()
    interval = intervals[type]
    if now // 1 % interval[0] <= interval[1]:
        return True
    else:
        return False

def remaining(type) -> str:
    '''remaining time due {something} happends, in minutes and seconds.'''
    now = current_time()
    interval = intervals[type][0]
    seconds = int(interval - now//1%interval)
    min = seconds//60
    sec = seconds%60
    return f'{(min) if min != 0 else ""}{1}'.format('{0} секунд'.format(sec) if sec != 0 else '')

def get_building(place) -> InlineKeyboardButton | None:
    '''Get InlineKeyboardButton with special building for every location'''
    match (place):
        case "Ботаническая":
            button = InlineKeyboardButton(text="🌲 Живополисский ботанический сад", callback_data="botan_garden_shop")
        case "Живбанк":
            button = InlineKeyboardButton(text="🏦 Живополисский банк", callback_data="bank")
        case "Университет":
            button = InlineKeyboardButton(text="🏫 Живополисский университет", callback_data="university")
        case "Котайский Мединститут":
            button = InlineKeyboardButton(text="🏫 Котайский институт медицинских наук", callback_data="university")
        case "Автопарк им. Кота":
            button = InlineKeyboardButton(text="🚗 Автопарк имени Cat Painted", callback_data="car_shop")
        case "ТЦ МиГ":
            button = InlineKeyboardButton(text="🏬 Торговый центр МиГ", callback_data="mall")
        case "Георгиевская":
            button = InlineKeyboardButton(text="🍰 Кондитерская \"СладкоЁжка\"", callback_data="candy_shop")
        case "Райбольница":
            button = InlineKeyboardButton(text="🏥 Живополисская районная больница", callback_data="hospital_shop")
        case "Старокотайский ФАП":
            button = InlineKeyboardButton(text="🏥 Старокотайский фельдшерский пункт", callback_data="hospital_shop")
        case "Зоопарк":
            button = InlineKeyboardButton(text="🦊 Живополисский зоопаcрк", callback_data="zoo_shop")
        case "Аэропорт Котай":
            button = InlineKeyboardButton(text="✈ Аэропорт Котай", callback_data="airport")
        case "Национальный аэропорт":
            button = InlineKeyboardButton(text="✈ Национальный аэропорт Живополис", callback_data="airport")
        case "Живополисский музей":
            button = InlineKeyboardButton(text="🏛 Исторический музей Живополиса", callback_data="museum")
        case "Макеевка":
            button = InlineKeyboardButton(text="🍏 \"Натурал\". Фрукты и овощи", callback_data="fruit_shop")
        case "Рынок":
            button = InlineKeyboardButton(text="🏣 Центральный рынок", callback_data="central_market_menu")
        case "Котайский электрозавод":
            button = InlineKeyboardButton(text="🏭 Котайский завод электрических деталей", callback_data="factory")
        case "Стадион":
            button = InlineKeyboardButton(text="🏟 Живополис-Арена", url="t.me/jivopolistour")
        case "Роща":
            button = InlineKeyboardButton(text="🌾 Ферма", callback_data="farm")
        case "Генерала Шелби":
            button = InlineKeyboardButton(text="📱 Магазин техники имени Шелби", callback_data="phone_shop")
        case _:
            return None
    return button