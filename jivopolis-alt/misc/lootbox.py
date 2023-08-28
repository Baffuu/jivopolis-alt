import random as rand
from typing import Tuple, Any

from . import ITEMS
from .. import bot


class LootboxEvents():
    @staticmethod
    def money() -> Tuple[int, str]:
        '''returns random number of money in range from 1 to 75'''
        return rand.randint(1, 75), 'money'

    @staticmethod
    def big_money() -> Tuple[int, str]:
        '''returns random number of money in range from 100 to 300'''
        return rand.randint(100, 300), 'big_money'

    @staticmethod
    def money_steal() -> Tuple[int, str]:
        '''
        returns random number of money that will be stealen, from -1 to -20
        '''
        return rand.randint(1, 20), 'money_steal'

    @staticmethod
    def robber_item() -> Tuple[str, str]:
        items = [
            item for item in ITEMS
            if ITEMS[item].type == 'robber'
        ]
        return rand.choice(items), 'robber_item'

    @staticmethod
    def common_masks() -> Tuple[str, str]:
        items = [
            'fox', 'wolf', 'hamster'
        ]
        return rand.choice(items), 'common_mask'

    @staticmethod
    def rare_masks() -> Tuple[str, str]:
        items = rand.randint(1, 100)
        match (items):
            case x if x in range(1, 70):
                price = rand.choice(RARE_MASKS)
            case x if x in range(71, 90):
                price = rand.choice(EPIC_MASKS)
            case x if x in range(91, 100):
                price = rand.choice(LEGENDARY_MASKS)
            case _:
                price, _ = LootboxEvents.rare_masks()
        return price, 'rare_masks'

    @staticmethod
    def crypto() -> Tuple[str, str]:
        _crypto = [item for item in ITEMS if ITEMS[item].type == "crypto"]
        return (rand.choice(_crypto), 'crypto')

    @staticmethod
    async def other_event() -> Tuple[Any, str]:
        chances = rand.randint(1, 100)  # todo: chances for several events # noqa
        return LootboxEvents.empty_lootbox, 'event'

    @staticmethod
    async def empty_lootbox(chat_id):
        await bot.send_message(
            chat_id,
            "🧌 Из ящика вылез гном. Поблагодарил за ночлег и продолжил своё "
            "странствие…"
        )
        return


LOOTBOX = {
    'money': (
        "📤 Вы нашли маленькую пачку денег на дне ящика… <b>Получено ${}</b>"
    ),

    'big_money': "🤩 Кажется, сегодня вам повезло! <b>Получено ${}</b>",

    'money_steal': (
        "💩 Из ящика вылезает 😼 Большой Шлёпа и крадёт у вас деньги."
        " В следующей раз будьте внимательнее. <b>Потеряно ${}</b>"
    ),

    'robber_item': (
        "👿 Кажется, кто-то отправил вам что-то нелегальное. <b>Получено {}"
        "</b>"
    ),

    'common_mask': (
        "🎭 Вы открываете ящик и находите в нём маску. <b>Получено {}</b>"
    ),

    'rare_masks': (
        "‼️ Упс, на коробке написано не ваше имя… "
        "Но никто ведь не запрещает вам ее открыть, верно? <b>Получено {}</b>"
    ),

    'crypto': "📼 Вы находите чью-то флешку у себя в ящике… <b>Получено {}</b>"
}
'''stores all strings for lootboxes'''

RARE_MASKS = ['cactus']
EPIC_MASKS = ['tulip', 'moyai', 'penguin']
LEGENDARY_MASKS = ['fan']


async def lootbox_open() -> Tuple[Any, str]:
    '''
    lootbox chances controller
    '''
    chances = rand.randint(1, 100)

    if chances in range(1, 50):
        price, price_type = LootboxEvents.money()
    elif chances in range(50, 60):
        price, price_type = LootboxEvents.big_money()
    elif chances in range(60, 65):
        price, price_type = LootboxEvents.money_steal()
    elif chances in range(65, 70):
        price, price_type = await LootboxEvents.other_event()
    elif chances in range(70, 75):
        price, price_type = LootboxEvents.robber_item()
    elif chances in range(75, 80):
        price, price_type = LootboxEvents.crypto()
    elif chances in range(80, 95):
        price, price_type = LootboxEvents.common_masks()
    elif chances in range(95, 100):
        price, price_type = LootboxEvents.rare_masks()
    else:
        price, price_type = await lootbox_open()

    return price, price_type  # type: ignore
