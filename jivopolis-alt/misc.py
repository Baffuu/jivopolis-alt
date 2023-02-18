from datetime import datetime
from config import intervals

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

def log_error(error: str) -> None:
    return

def remaining(type) -> str:
    '''remaining time due {something} happends, in minutes and seconds.'''
    now = current_time()
    interval = intervals[type][0]
    seconds = int(interval - now//1%interval)
    min = seconds//60
    sec = seconds%60
    return f'{min if min != 0 else ""}{1}'.format('{0} минут '.format(min) if min != 0 else '', '{0} секунд'.format(sec) if sec != 0 else '')