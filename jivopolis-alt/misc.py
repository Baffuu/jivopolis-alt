from loguru import logger

from datetime import datetime
from .config import intervals, BOT_USER

from typing import Union

from .database.sqlitedb import cur
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
    except TypeError:
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