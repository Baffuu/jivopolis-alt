import random as rand
from typing import Tuple

from . import ITEMS

def money() -> Tuple[int, str]:
    '''returns random number of money in range from 1 to 75'''
    return rand.randint(1, 75), 'money'
def big_money() -> Tuple[int, str]:
    '''returns random number of money in range from 100 to 300'''
    return rand.randint(100, 300), 'big_money'
def money_steal() -> Tuple[int, str]:
    '''returns random number of money that will be stealen, from -1 to -20'''
    return rand.randint(1, 20), 'money_steal'
def robber_item() -> Tuple[str, str]:
    items = [
        item for item in ITEMS
        if ITEMS[item].type == 'robber'
    ]
    return rand.choice(items), 'robber_item'
def common_masks() -> Tuple[str, str]:
    items = [
        'fox', 'wolf', 'hamster'
    ]
    return rand.choice(items), 'common_mask'
def rare_masks() -> Tuple[str, str]:  
    items = rand.randint(1, 100)
    match (rand.choice(items)):
        case x if x in range(1, 70):
            prise = rand.choice(RARE_MASKS)
        case x if x in range(71, 90):
            price = rand.choice(EPIC_MASKS)
        case x if x in range(91, 100):
            price = rand.choice(LEGENDARY_MASKS)
    return price, 'rare_masks'

LOOTBOX = {
    'money': "📤 Вы нашли маленькую пачку денег на дне ящика… <b>Получено ${}</b>",
    'big_money': "🤩 Кажется, сегодня вам повезло! <b>Получено ${}</b>", 
    'money_steal': "💩 Из ящика вылезает 😼 Большой Шлепа и крадет у вас деньги.\
        В следующей раз будьте внимательнее. <b>Потеряно ${}</b>",
    'robber_item': "👿 Кажется, кто-то отправил вам что-то нелегальное. <b>Получено {}</b>",
    'common_mask': "🎭 Вы открываете ящик и находите в ней маску. <b>Получено {}</b>",
    'rare_masks': "‼️ Упс, на коробке написано не ваше имя… \
        Но никто ведь не запрещает вам ее открыть, верно? <b>Получено {}</b>"
}
'''stores all strings for lootboxes'''
RARE_MASKS = ['cactus']
EPIC_MASKS = ['tulip', 'moyai']
LEGENDARY_MASKS = ['fan']

async def lootbox_open() -> None:
    '''
    lootbox chances controller 
    '''
    chances = rand.randint(1, 100)
    
    if chances in range(1, 50):
        price, price_type = money()
    elif chances in range(50, 60):
        price, price_type = big_money()
    elif chances in range(60, 70):
        price, price_type = money_steal()
    elif chances in range(70, 80):
        price, price_type = robber_item()
    elif chances in range(80, 95):
        price, price_type = common_masks()
    elif chances in range(95, 100):
        price, price_type = rare_masks()

    return price, price_type