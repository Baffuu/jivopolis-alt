import contextlib
import random
import asyncio

from ... import logger, bot
from ...misc import get_building, get_embedded_link, ITEMS
from ...misc.misc import remaining, isinterval
from ...misc.constants import (MINIMUM_CAR_LEVEL, MAXIMUM_DRIVE_MENU_SLOTS,
                               MAP, REGIONAL_MAP)
from ...database import cur
from ...database.functions import buy, buybutton, itemdata

from ...misc.config import (
    METRO, WALK, CITY,
    trains, villages, walks,
    limeteds,
    lvlcab, cabcost, locations, REGTRAIN,
    clanitems, LINES, LINES_GENITIVE, ticket_time, aircost
)

from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
)
from aiogram.utils.exceptions import (
    MessageCantBeDeleted,
    MessageToDeleteNotFound
)

# time required for specific type of transport to reach the next station
# the arrays contain minimum and maximum time
METRO_TIME = [15, 30]
AIRPLANE_TIME = [90, 120]
REGTRAIN_TIME = [30, 45]


async def city(message: Message, user_id: str | int):
    # sourcery skip: low-code-quality
    '''
    Callback for city

    :param message:
    :param user_id:
    '''
    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    line = cur.select("line", "userdata").where(user_id=user_id).one()
    car = cur.select("blue_car+red_car", "userdata").where(
        user_id=user_id).one()  # todo MORE CARS

    markup = InlineKeyboardMarkup(row_width=6)

    if place not in METRO[line]:
        for metro_line in METRO:
            if place not in metro_line:
                continue

            cur.update("userdata").set(line=METRO.index(metro_line)).where(
                user_id=user_id).commit()

            line = METRO.index(metro_line)

            break

    if line in [2, 0]:
        metro = InlineKeyboardButton(text="🚉", callback_data="metro")
    else:
        metro = InlineKeyboardButton(text="🚇", callback_data="metro")

    caritem = InlineKeyboardButton(text="🚗", callback_data="car_menu")
    trolleybus = InlineKeyboardButton(text="🚎", callback_data="trolleybus")
    train_station = InlineKeyboardButton(text="🚆",
                                         callback_data="railway_station")
    train_lounge = InlineKeyboardButton(text="🚆", callback_data="lounge")
    taxi = InlineKeyboardButton(text="🚕", callback_data="taxi_menu")
    bus_station = InlineKeyboardButton(text="🚌", callback_data="bus")
    bus_lounge = InlineKeyboardButton(text="🚌", callback_data="bus_lounge")
    trans = []
    for metro_line in METRO:
        if place in metro_line:
            trans.append(metro)
            break
    if place in CITY:
        trans.append(trolleybus)
    if place in REGTRAIN[1]:
        if place in trains[0]:
            trans.append(train_station)
        else:
            trans.append(train_lounge)
    if place in villages:
        if place in ["Автовокзал Живополис", "АС Александрово"]:
            trans.append(bus_station)
        else:
            trans.append(bus_lounge)
    if place in CITY:
        trans.append(taxi)
        if car >= 1:
            trans.append(caritem)
    markup.add(*trans)

    location_button = get_building(place)

    if location_button is not None:
        markup.add(location_button)

    index = -1
    iswalk = next((WALK.index(walk_line) for walk_line in WALK
                   if place in walk_line), -1)
    for walkline in WALK:
        walkindex = WALK.index(walkline)
        if (
            iswalk == -1
            or walkindex == iswalk
            or walkline[WALK[iswalk].index(place)] == ""
        ):
            continue

        index = WALK[iswalk].index(place)

        markup.add(
            InlineKeyboardButton(
                text=f"🚶 {walkline[index]} - {walks[index]} секунд ходьбы",
                callback_data=f"walk_{walkline[index]}"
            )
        )

    '''
    cur.execute("SELECT * FROM clandata WHERE islocation=1 AND hqplace=? AND type=?", (place, "public",)) # noqa
    for row in cur:
        markup.add(InlineKeyboardButton(text="🏢 {0}".format(row[1]), url=row[8]))''' # noqa

    markup.add(
        InlineKeyboardButton(
            text="📡 GPS",
            callback_data="gps"
        ),
        InlineKeyboardButton(
            text="🏢 Кланы рядом",
            callback_data="local_clans"
        ),
        InlineKeyboardButton(
            text="👤 Кто здесь?",
            callback_data="local_people"
        )
    )
    await message.answer(
        "<i>В Живополисе есть много чего интересного!\n"
        f"&#127963; <b>{place}</b></i>",
        reply_markup=markup
    )


async def buycall(call: CallbackQuery):
    # sourcery skip: remove-unnecessary-cast
    '''
    Callback for buying an item

    :param call - callback:
    '''
    user_id = call.from_user.id
    item = call.data.split(':')[0][4:]
    try:
        tip = int(call.data.split(':')[1])
    except Exception:
        tip = 0

    try:
        amount = call.data.split(':')[2]
    except IndexError:
        amount = 1

    if item in ITEMS:
        if ITEMS[item].type == 'car':
            level = cur.select("level", "userdata").where(
                user_id=user_id).one()
            if level < MINIMUM_CAR_LEVEL:
                return await call.answer(
                    text=(
                        '❌ Данная функция доступна только с уровня'
                        f' {MINIMUM_CAR_LEVEL}'
                    ),
                    show_alert=True
                )

            # await achieve(a.id, call.message.chat.id, 'myauto')
        cost = ITEMS[item].cost
        assert cost is not None

        await buy(
            call,
            item,
            user_id,
            cost=cost+tip,
            amount=int(amount)
        )
    else:
        raise ValueError("no such item")


async def car_menu(call: CallbackQuery) -> None:
    '''
    Callback for car menu

    :param call - callback:
    '''
    message = call.message
    user_id = call.from_user.id
    car = cur.select("red_car+blue_car", "userdata").where(
        user_id=user_id).one()  # todo more cars

    if car < 1:
        return await call.answer('❌ У вас нет машины', show_alert=True)

    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    places = []

    for place in CITY:
        if place == current_place:
            places.append(
                InlineKeyboardButton(
                    f"📍 {place}",
                    callback_data=f'goto_on_car_{place}'
                    )
                )
            continue

        places.append(
            InlineKeyboardButton(
                f"🏘️ {place}",
                callback_data=f'goto_on_car_{place}'
            )
        )

    markup = InlineKeyboardMarkup(row_width=2)

    for index, place in enumerate(places):
        if index < MAXIMUM_DRIVE_MENU_SLOTS:
            markup.add(place)
        else:
            break

    if markup.values["inline_keyboard"] == []:
        return await call.answer("dead end", True)

    markup.add(
        InlineKeyboardButton("⬅️", callback_data="car_menu_previous:1"),
        InlineKeyboardButton(text="➡️", callback_data="car_menu_next:1"),
    )

    await message.answer(
        '<i>👨‍✈️ Выберите место для поездки.</i>',
        reply_markup=markup
    )


async def car_menu_next(call: CallbackQuery, menu: int):
    user_id = call.from_user.id
    message = call.message
    car = cur.select("red_car", "userdata").where(
        user_id=user_id).one()
    car = 0 if car is None else car

    if car < 1:
        return await call.answer('❌ У вас нет машины', show_alert=True)

    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    markup = InlineKeyboardMarkup(row_width=2)
    places = []
    for place in CITY:
        if place == current_place:
            places.append(
                InlineKeyboardButton(
                    f"📍 {place}",
                    callback_data=f'goto_on_car_{place}'
                )
            )
        places.append(
            InlineKeyboardButton(
                f"🏘️ {place}",
                callback_data=f'goto_on_car_{place}'
            )
        )

    for index, place in enumerate(places):
        if index < MAXIMUM_DRIVE_MENU_SLOTS * menu:
            continue
        elif index < MAXIMUM_DRIVE_MENU_SLOTS * (menu+1):
            markup.add(place)
        else:
            break

    if markup.values["inline_keyboard"] == []:
        return await call.answer("dead end", True)

    markup.add(
        InlineKeyboardButton(
            "⬅️",
            callback_data=f"car_menu_previous:{menu+1}"
        ),
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"car_menu_next:{menu+1}"
        )
    )
    await message.answer(
        '<i>👨‍✈️ Выберите место для поездки.</i>',
        reply_markup=markup
    )
    with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
        await message.delete()


async def car_menu_previous(call: CallbackQuery, menu: int):
    user_id = call.from_user.id
    message = call.message
    car = cur.select("red_car+blue_car", 'userdata').where(
        user_id=user_id).one()  # todo more cars

    if car < 1:
        return await call.answer('❌ У вас нет машины', show_alert=True)

    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    markup = InlineKeyboardMarkup(row_width=2)
    places = []

    for place in CITY:
        if place == current_place:
            places.append(
                InlineKeyboardButton(
                    f"📍 {place}",
                    callback_data=f'goto_on_car_{place}'
                )
            )
            continue
        places.append(
            InlineKeyboardButton(
                f"🏘️ {place}",
                callback_data=f'goto_on_car_{place}'
            )
        )

    for index, place in enumerate(places):
        if (
            index > MAXIMUM_DRIVE_MENU_SLOTS * (menu-1)
            and index < MAXIMUM_DRIVE_MENU_SLOTS * menu
        ):
            markup.add(place)
        else:
            continue

    if markup.values["inline_keyboard"] == []:
        await call.answer("dead end", True)
        with contextlib.suppress(
            MessageToDeleteNotFound,
            MessageCantBeDeleted
        ):
            return await message.delete()

    markup.add(
        InlineKeyboardButton(
            "⬅️",
            callback_data=f"car_menu_previous:{menu-1}"
        ),
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"car_menu_next:{menu-1}"
        )
    )

    await message.answer(
        '<i>👨‍✈️ Выберите место для поездки</i>',
        reply_markup=markup
    )
    with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
        await message.delete()


async def goto_on_car(call: CallbackQuery):
    user_id = call.from_user.id
    car = cur.select("red_car+blue_car", "userdata").where(
        user_id=user_id).one()

    if car < 1:
        return await call.message.answer('<i>🚗 У вас нет машины</i>')

    station = call.data[12:]
    await call.message.answer('<i>Скоро приедем!</i>')

    with contextlib.suppress(Exception):
        await call.message.delete()

    await asyncio.sleep(15)

    cur.update("userdata").set(current_place=station).where(
        user_id=user_id).commit()
    await city(call.message, call.from_user.id)  # type: ignore


async def local_people(call: CallbackQuery):
    '''
    Callback for seeing people that are in the same place as you

    :param call - callback:
    '''
    place = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()
    usercount = cur.select("count(*)", "userdata").where(
        current_place=place).one()

    if usercount <= 1:
        return await call.message.answer(
            "<i>👤 Вы стоите один, оглядываясь по сторонам…\n"
            "\n😓 В вашей местности не найдено людей. Помимо вас, "
            "само собой</i>"
        )

    cur.execute(f"SELECT * FROM userdata WHERE current_place = '{place}'")

    users = ''.join(
        [
            f'\n{index}. {await get_embedded_link(row[1])}'
            for index, row in enumerate(cur.fetchall(), start=1)
        ]
    )
    await call.message.answer(
        f'<i>👤 Пользователи в местности <b>{place}</b>: <b>{users}</b></i>')


async def delivery_menu(call: CallbackQuery) -> None:
    '''
    Callback for delivery phone app

    :param user_id:
    '''
    phone = cur.select("phone", "userdata").where(
        user_id=call.from_user.id).one()

    if phone < 1:
        return await call.answer(
            'Вам нужен телефон. Его можно купить в магазине на ул. Генерала '
            'Шелби и одноимённой станции метро',
            show_alert=True
        )

    markup = InlineKeyboardMarkup(row_width=1)
    sellitems = [
        'snegovik', 'snow', 'tree', 'fairy', 'santa_claus', 'mrs_claus',
        'firework', 'fireworks', 'confetti', 'clown', 'ghost', 'alien',
        'robot', 'shit', 'moyai', 'pasta', 'rice', 'sushi'
    ]
    _sellitems = []
    for item in sellitems:
        try:
            _sellitems.append(buybutton(item, tip=15))
        except ValueError:
            logger.error(f'no such item: {item}')

    sellitems = list(filter(lambda item: item is not None, _sellitems))
    sellitems = list(
        filter(lambda item: type(item) is InlineKeyboardButton, _sellitems))

    markup.add(*sellitems)
    markup.add(
        InlineKeyboardMarkup(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>🚚 Здесь вы можете заказать себе любой товар из ТЦ МиГ из любого '
        'места, даже из самой глухой деревни. Это обойдётся дороже, чем в ТЦ,'
        ' зато удобнее :)</i>'
    )


async def central_market_menu(call: CallbackQuery) -> None:
    '''
    Callback for central market menu

    :param call - callback:
    '''
    place = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()

    if place != 'Рынок':
        return  # todo answer

    markup = InlineKeyboardMarkup(row_width=2).\
        add(
            InlineKeyboardMarkup(
                text='🍦 Продажа еды',
                callback_data='central_market_food'
            ),
            InlineKeyboardMarkup(
                text='👕 Продажа масок',
                callback_data='central_market_mask'
            ),
            InlineKeyboardMarkup(text='🚪 Выйти', callback_data='cancel_action')
        )

    await call.message.answer(
        (
            "<i><b>🏣 Центральный рынок</b> - место, в котором можно продать "
            "купленные товары. Дешевле, чем в магазине, но удобно\n"
            "\n❗ Здесь вы <b>продаёте</b> товары государству, а не покупаете."
            " Деньги вы получаете автоматически, ваш товар никому не достаётся"
            "</i>"
        ),
        reply_markup=markup
    )


async def central_market_food(call: CallbackQuery) -> None:
    '''
    Callback for food section of the central market

    :param call - callback:
    '''
    user_id = call.from_user.id
    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if place != 'Рынок':
        return  # todo answer

    markup = InlineKeyboardMarkup(row_width=3)
    itemlist = []
    coef = 1.5  # todo cur.execute(f"SELECT coef FROM globaldata").fetchone()[0] # noqa

    for item in ITEMS:
        if (
            await itemdata(user_id, item) != 'emptyslot'
            and ITEMS[item].type == 'food'
            and isinstance(ITEMS[item].price, int)
        ):
            cost = ITEMS[item].price
            assert isinstance(cost, int)
            cost //= coef
            itemlist.append(
                InlineKeyboardButton(
                    text=f'{ITEMS[item].emoji} - ${cost}',
                    callback_data=f'sellitem_{item}'
                )
            )

    if not itemlist:
        desc = '🚫 У вас нет еды для продажи'
    else:
        markup.add(*itemlist)
        desc = (
            '<b>🏣 Центральный рынок</b> - место, в котором можно продать '
            'купленные товары. Дешевле, чем в магазине, но удобно\n\n❗ Зд'
            'есь вы <b>продаёте</b> товары государству, а не покупаете. Де'
            'ньги вы получаете автоматически, ваш товар никому не достаётся'
        )
    markup.add(
        InlineKeyboardMarkup(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )
    await call.message.answer(f'<i>{desc}</i>', reply_markup=markup)


async def central_market_mask(call: CallbackQuery) -> None:
    '''
    Callback for mask section of the central market

    :param call - callback:
    '''
    user_id = call.from_user.id
    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if place != 'Рынок':
        return  # todo answer

    markup = InlineKeyboardMarkup(row_width=3)

    itemlist = []
    coef = 1.5  # todo cur.select("coef", "globaldata").one()

    for item in ITEMS:
        if (
            await itemdata(user_id, item) != 'emptyslot'
            and ITEMS[item].type == 'mask'
            and isinstance(ITEMS[item].price, int)
        ):
            cost = ITEMS[item].price
            assert isinstance(cost, int)

            cost //= coef
            itemlist.append(
                InlineKeyboardButton(
                    text=f'{ITEMS[item].emoji} - ${cost}',
                    callback_data=f'sellitem_{item}'
                )
            )

    if not itemlist:
        text = '🚫 У вас нет масок для продажи'

    else:
        markup.add(*itemlist)
        text = (
            '<b>🏣 Центральный рынок</b> - место, в котором можно продать купл'
            'енные товары. Дешевле, чем в магазине, но удобно\n\n❗ Здесь вы <b'
            '>продаёте</b> товары государству, а не покупаете. Деньги вы получ'
            'аете автоматически, ваш товар никому не достаётся'
        )
    markup.add(
        InlineKeyboardMarkup(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )
    await call.message.answer(
        f'<i>{text}</i>',
        reply_markup=markup
    )


async def bank(call: CallbackQuery) -> None:
    '''
    Callback for bank

    :param call - callback:
    '''
    place = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()

    if place != 'Живбанк':
        return  # todo answer

    markup = InlineKeyboardMarkup(row_width=1).\
        add(
            InlineKeyboardButton(
                text='🏦 Государственная казна',
                callback_data='state_balance'
            ),
            InlineKeyboardButton(
                text='🤏 Ограбить',
                callback_data='rob_bank'
            )
        )

    await call.message.answer(
        '<i>🏦 Добро пожаловать в Банк</i>',
        reply_markup=markup
    )


async def state_balance(call: CallbackQuery) -> None:
    '''
    Callback for state treasury

    :param call - callback:
    '''
    place = cur.select("current_place", 'userdata').where(
        user_id=call.from_user.id).one()
    treasury = cur.select("treasury", "globaldata").one()

    if place != 'Живбанк':
        return  # todo answer

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='💰 Пожертвовать $100',
            callback_data='give_state 100'
        ),
        InlineKeyboardButton(
            text='💰 Пожертвовать $500',
            callback_data='give_state 500'
        ),
        InlineKeyboardButton(
            text='💰 Пожертвовать $1000',
            callback_data='give_state 1000'
        ),
        InlineKeyboardButton(
            text='💰 Пожертвовать $10,000',
            callback_data='give_state 10000'
        )
    )

    await call.message.answer(
        f'<i>🏦 Добро пожаловать в Казну. Сейчас тут ${treasury}</i>',
        reply_markup=markup)


async def taxi_menu(message: Message, user_id: int):
    '''
    Callback for taxi menu

    :param message:
    :param user_id:
    '''
    level = cur.select("level", "userdata").where(
        user_id=user_id).one()

    if level < lvlcab:
        return await message.answer(
            f'🚫 Данная функция доступна только с уровня {lvlcab}'
        )

    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    markup = InlineKeyboardMarkup(row_width=2)
    places = []
    for place in CITY:
        if place == current_place:
            places.append(
                InlineKeyboardButton(
                    f"📍 {place}",
                    callback_data=f'taxicost_{place}'
                )
            )
            continue
        places.append(
            InlineKeyboardButton(
                f"🏘️ {place}",
                callback_data=f'taxicost_{place}'
            )
        )

    for index, place in enumerate(places):
        if index < MAXIMUM_DRIVE_MENU_SLOTS:
            markup.add(place)
        else:
            break
    markup.add(
        InlineKeyboardButton("⬅️", callback_data="taxi_previous:1"),
        InlineKeyboardButton(text="➡️", callback_data="taxi_next:1")
    )

    await message.answer('<i>🚕 Куда поедем?</i>', reply_markup=markup)
    return await message.answer(
        '<i>Стоимость поездки зависит от отдалённости места, в которое вы'
        ' едете.Чтобы посмотреть цену поездки до определённого места, наж'
        'мите на него в списке локаций в предыдущем сообщении</i>'
    )


async def taxi_next(call: CallbackQuery, menu: int):
    user_id = call.from_user.id
    level = cur.select("level", "userdata").where(user_id=user_id).one()
    message = call.message

    if level < lvlcab:
        return await message.answer(
            f'🚫 Данная функция доступна только с уровня {lvlcab}'
        )

    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    markup = InlineKeyboardMarkup(row_width=2)

    places = []

    for place in CITY:
        if place == current_place:
            places.append(
                InlineKeyboardButton(
                    f"📍 {place}",
                    callback_data=f'taxicost_{place}'
                )
            )
            continue
        places.append(
            InlineKeyboardButton(
                f"🏘️ {place}",
                callback_data=f'taxicost_{place}'
            )
        )

    for index, place in enumerate(places):
        if index < MAXIMUM_DRIVE_MENU_SLOTS * menu:
            continue
        elif index < MAXIMUM_DRIVE_MENU_SLOTS * (menu+1):
            markup.add(place)
        else:
            break

    if markup.values["inline_keyboard"] == []:
        await call.answer("dead end", True)
        with contextlib.suppress(
            MessageToDeleteNotFound,
            MessageCantBeDeleted
        ):
            return await message.delete()

    markup.add(
        InlineKeyboardButton(
            "⬅️",
            callback_data=f"taxi_previous:{menu+1}"
        ),
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"taxi_next:{menu+1}"
        )
    )
    await message.answer('<i>🚕 Куда поедем?</i>', reply_markup=markup)
    with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
        await message.delete()


async def taxi_previous(call: CallbackQuery, menu: int):
    user_id = call.from_user.id
    level = cur.select("level", "userdata").where(
        user_id=user_id).one()
    message = call.message

    if level < lvlcab:
        return await message.answer(
            f'🚫 Данная функция доступна только с уровня {lvlcab}'
        )

    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    markup = InlineKeyboardMarkup(row_width=2)
    places = []
    for place in CITY:
        if place == current_place:
            places.append(
                InlineKeyboardButton(
                    f"📍 {place}",
                    callback_data=f'taxicost_{place}'
                )
            )
            continue
        places.append(
            InlineKeyboardButton(
                f"🏘️ {place}",
                callback_data=f'taxicost_{place}'
            )
        )

    for index, place in enumerate(places):
        if index > MAXIMUM_DRIVE_MENU_SLOTS * menu:
            continue
        elif index > MAXIMUM_DRIVE_MENU_SLOTS * (menu-1):
            markup.add(place)
        else:
            break

    if markup.values is None:
        await call.answer("dead end", True)
        with contextlib.suppress(
            MessageToDeleteNotFound,
            MessageCantBeDeleted
        ):
            return await message.delete()

    markup.add(
        InlineKeyboardButton(
            "⬅️",
            callback_data=f"taxi_previous:{menu-1}"
        ),
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"taxi_next:{menu-1}"
        )
    )
    await message.answer('<i>🚕 Куда поедем?</i>', reply_markup=markup)
    with contextlib.suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
        await message.delete()


async def taxicost(call: CallbackQuery, place: str) -> None:
    '''
    Callback for taxi cost & approval

    :param call - callback:
    :param place:
    '''
    current_place = cur.select("current_place", "userdata").where(
        user_id=call.from_user.id).one()

    if place not in CITY:
        raise ValueError('no such place')
    if place == current_place:
        return await call.answer(
            "⛔️ Вы и так в этой местности.",
            show_alert=True
        )
    cost = (cabcost*abs(CITY.index(place)-CITY.index(current_place)))//1

    markup = InlineKeyboardMarkup(row_width=2).\
        add(
            InlineKeyboardButton(
                '🚕 Ехать', callback_data=f'taxi_goto_{place}'),
            InlineKeyboardButton('🚫 Отмена', callback_data='cancel_action')
        )

    await call.message.answer(
        f'<i>Стоимость поездки до локации <b>{place}</b> - <b>${cost}</b></i>',
        reply_markup=markup
    )


async def taxi_goto_(call: CallbackQuery, place: str) -> None:
    '''
    Callback for going to {place} on taxi

    :param call - callback:
    :param place:
    '''
    user_id = call.from_user.id

    balance = cur.select("balance", "userdata").where(user_id=user_id).one()
    current_place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()

    if place not in CITY:
        raise ValueError('no such place')

    cost = (cabcost*abs(CITY.index(place)-CITY.index(current_place)))//1

    if balance < cost:
        return await call.answer(
            '🚫 У вас недостаточно средств для поездки',
            show_alert=True
        )

    await call.message.answer('<i>Скоро приедем!</i>')

    with contextlib.suppress(Exception):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    await asyncio.sleep(15)

    cur.update('userdata').set(current_place=place).where(
        user_id=user_id).commit()
    cur.update("userdata").add(balance=-cost).where(
        user_id=user_id).commit()

    await city(call.message, call.from_user.id)


async def gps_menu(call: CallbackQuery) -> None:
    '''
    Callback for GPS app menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    phone = cur.select("phone", "userdata").where(user_id=user_id).one()

    if phone < 1:
        return await call.answer(
            'Чтобы пользоваться GPS, вам нужен телефон. Его можно купить в маг'
            'азине на ул. Генерала Шелби и одноимённой станции метро',
            show_alert=True
        )

    categorylist = []
    markup = InlineKeyboardMarkup()

    for category in locations[3]:
        if category not in categorylist:
            categorylist.append(category)
            count = sum(
                locations[3][locations[0].index(location)] == category
                for location in locations[0]
            )
            markup.add(
                InlineKeyboardButton(
                    text=f'{category} ({count})',
                    callback_data=f'gpsloc_{category}'
                )
            )

    markup.add(
        InlineKeyboardMarkup(
            text='◀ Назад',
            callback_data='cancel_action'
        )
    )
    await call.message.answer('<i>Выберите категорию</i>', reply_markup=markup)


async def buy24_(call: CallbackQuery, item: str) -> None:
    '''
    Callback for buying {item} in 24-hour shop

    :param call - callback:
    :param item:

    :raises ValueError if item doesn't seem to exists
    '''
    if item not in ITEMS or item not in limeteds:
        raise ValueError("no such item")
    items_left = cur.select(item, "globaldata").one()

    if items_left < 1:
        return await call.answer(
            text='К сожалению, этого товара сейчас нет в магазине ввиду дефи'
            'цита :(\nПриходите завтра или посетите любой продуктовый магази'
            'н в Городе',
            show_alert=True
        )

    cur.update("globaldata").add(item=1).commit()
    cost = ITEMS[item].price
    assert isinstance(cost, int)
    await buy(call, item, call.from_user.id, cost)


async def buyclan_(call: CallbackQuery, item: str) -> None:
    '''
    Callback for buying item in a clan using clan buildings

    :param call - callback:
    :param item:

    :raises ValueError if item does not exist or is not in clan-items
    '''
    if item not in clanitems:
        raise ValueError("no such item in clanitems")

    cost = clanitems[1][clanitems[0].index(item)]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    count = cur.select("count(*)", "clandata").where(clan_id=chat_id).one()

    if count < 1:
        raise ValueError("clan not found")

    balance = cur.select("balance", 'userdata').where(user_id=user_id).one()

    if balance < cost:
        return await call.answer(
            '❌ У вас недостаточно средств',
            show_alert=True)

    cur.update("userdata").add(balance=-cost).where(user_id=user_id).commit()
    cur.update("userdata").add(item=1).where(user_id=user_id).commit()

    clan_bonus_devider = random.randint(1, 5)

    cur.update("clandata").add(balance=cost//clan_bonus_devider).where(
        clan_id=chat_id).commit()
    await call.answer(
        f'Покупка совершена успешно. Ваш баланс: ${balance-cost}. Баланс клана'
        f' пополнен на ${cost//clan_bonus_devider}',
        show_alert=True
    )


async def railway_station(call: CallbackQuery) -> None:
    '''
    Callback for railway station callback

    :param call - callback:
    '''
    markup = InlineKeyboardMarkup(row_width=1).\
        add(
            InlineKeyboardButton(
                text='💺 Зал ожидания',
                callback_data='lounge'
            ),
            InlineKeyboardButton(
                text='🎫 Билетные кассы',
                callback_data='tickets'
            ),
            InlineKeyboardButton(
                text='🍔 Кафетерий "Енот Кебаб"',
                callback_data='enot_kebab_shop'
            )
        )

    await call.message.answer(
        '<i>Пора уже валить отсюда...</i>',
        reply_markup=markup
    )


async def bus(call: CallbackQuery) -> None:
    '''
    Callback for bus menu

    :param call - callback:
    :param user_id:
    '''
    markup = InlineKeyboardMarkup(row_width=1).\
        add(
            InlineKeyboardButton(
                text='🚌 К платформам',
                callback_data='bus_lounge'
            ),
            InlineKeyboardButton(
                text='🎫 Билетные кассы',
                callback_data='tickets'
            ),
            InlineKeyboardButton(
                text='🍔 Кафетерий "Енот Кебаб"',
                callback_data='enot_kebab'
            )
        )

    await call.message.answer(
        '<i>Пора уже валить отсюда...</i>',
        reply_markup=markup
    )


async def metro(call: CallbackQuery):
    '''
    Callback for subway station vestibule menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    token = cur.select("metrotoken", "userdata").where(user_id=user_id).one()
    line = cur.select("line", "userdata").where(user_id=user_id).one()

    markup = InlineKeyboardMarkup()
    if line not in [1, 2]:
        markup.add(
            InlineKeyboardButton(
                text='🚇 Пройти на станцию',
                callback_data='proceed_metro'
            )
        )
    else:
        markup.add(
            InlineKeyboardButton(
                text='🚉 Пройти на платформу',
                callback_data='proceed_metro'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='🎫 Покупка жетонов',
            callback_data='metro_tickets'
        )
    )
    await call.message.answer(
        f'<i>У вас <b>{token}</b> жетонов</i>',
        reply_markup=markup
    )


async def proceed_metro(call: CallbackQuery):
    '''
    Callback for entering a subway station

    :param call - callback:
    '''
    user_id = call.from_user.id
    token = cur.select("metrotoken", "userdata").where(user_id=user_id).one()

    if token < 1:
        markup = InlineKeyboardMarkup()
        markup.add()
        return await call.message.answer(
            '<i>🚫 У вас недостаточно жетонов</i>',
            reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(
                        text='🎫 Покупка жетонов',
                        callback_data='metro_tickets'
                    )
                )
            )

    cur.update("userdata").add(metrotoken=-1).where(
        user_id=user_id).commit()
    await metrocall(call)


def _transfer(user_id) -> None | str | int:
    line = cur.select("line", "userdata").where(user_id=user_id).one()
    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    for i in range(4):
        if i != line and place in METRO[i]:
            return i
    return


async def metrocall(call: CallbackQuery):
    '''
    Callback for subway station

    :param call - callback:
    '''
    user_id = call.from_user.id
    line = cur.select("line", "userdata").where(user_id=user_id).one()
    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    index = METRO[line].index(place)
    markup = InlineKeyboardMarkup()
    desc = str()

    if trans := _transfer(user_id):
        desc += f'Переход к поездам {LINES_GENITIVE[trans]}\n'  # type: ignore

        markup.add(
            InlineKeyboardButton(
                f'🔄 {LINES[trans]}',  # type: ignore
                callback_data='transfer'
            )
        )

    if (
        place in ['Котайский Мединститут', 'Крайний Север', 'Северо-Восток']
        or
        (
            place in ['Площадь Админов', 'Историческая']
            and line == 0
        )
    ):
        desc += (
            '<b>Конечная.</b> Поезд дальше не идёт, просьба пассажиров'
            ' выйти из вагонов'
        )
    if index > 0:
        previous_station = METRO[line][index-1]
        markup.add(
            InlineKeyboardButton(
                text=f'⬅ {previous_station}',
                callback_data='metro_back'
            )
        )
    if index < len(METRO[line])-1:
        next_station = METRO[line][index+1]
        markup.add(
            InlineKeyboardButton(
                text=f'➡ {next_station}',
                callback_data='metro_forward'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='🏛 Выйти в город',
            callback_data='city'
        )
    )

    if line in [2, 0]:
        message = await call.message.answer_photo(
            MAP,
            caption=f'<i>Остановочный пункт <b>{place}</b>\n{desc}</i>',
            reply_markup=markup
        )
    else:
        message = await call.message.answer_photo(
            MAP,
            caption=f'<i>Станция <b>{place}</b>\n{desc}</i>',
            reply_markup=markup
        )
    await asyncio.sleep(ticket_time)

    with contextlib.suppress(Exception):
        await message.delete()


async def tostation(user_id: int | str, station: str, line: int | None = None):
    '''
    Callback for a user to instantly go to some place

    :param user_id - ID of the user to go to the place:
    :param station - the place for the user to go:
    :param line - the line where the place is located:
    '''
    lines = (
        line
        or cur.select("line", "userdata").where(user_id=user_id).one()
    )
    cur.update("userdata").set(current_place=station).where(
        user_id=user_id).commit()
    cur.update("userdata").set(line=lines).where(user_id=user_id).commit()


async def metro_forward(call: CallbackQuery):
    user_id = call.from_user.id
    line = cur.select("line", "userdata").where(user_id=user_id).one()

    if line in [0, 2]:
        if not isinterval('citylines'):
            return await call.answer(
                (
                    "Посадка ещё не началась. Поезд приедет через "
                    f"{remaining('citylines')}"
                ),
                show_alert=True
            )

    elif not isinterval('metro'):
        return await call.answer(
            "Посадка ещё не началась. Поезд приедет через "
            f"{remaining('metro')}",
            show_alert=True
        )

    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    index = METRO[line].index(place)

    if line not in [0, 2]:
        await call.message.answer_photo(
            'https://te.legra.ph/file/5104458f4a5bab9259a18.jpg',
            f'<i>Следующая станция: <b>{METRO[line][index+1]}</b>. Осторожно,'
            ' двери закрываются!</i>'
        )

    else:
        await call.message.answer_photo(
            'https://telegra.ph/file/06103228e0d120bacf852.jpg',
            '<i>Посадка завершена. Следующий остановочный пункт: <b>'
            f'{METRO[line][index+1]}</b></i>'
        )

    with contextlib.suppress(Exception):
        await call.message.delete()
    await asyncio.sleep(random.randint(METRO_TIME[0], METRO_TIME[1]))
    await tostation(user_id, station=METRO[line][index+1])
    await metrocall(call)


async def metro_back(call: CallbackQuery):
    user_id = call.from_user.id
    line = cur.select("line", "userdata").where(user_id=user_id).one()

    if line in [0, 2] and not isinterval('citylines'):
        return await call.answer(
            "Посадка ещё не началась. Поезд приедет через "
            f"{remaining('citylines')}",
            show_alert=True
        )

    elif not isinterval('metro'):
        return await call.answer(
            "Посадка ещё не началась. Поезд приедет через"
            f" {remaining('metro')}",
            show_alert=True
        )

    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    index = METRO[line].index(place)

    if line not in [2, 0]:
        await call.message.answer_photo(
            'https://te.legra.ph/file/5104458f4a5bab9259a18.jpg',
            caption=f'<i>Следующая станция: <b>{METRO[line][index-1]}</b>.'
            ' Осторожно, двери закрываются!</i>'
        )
    else:
        await call.message.answer_photo(
            'https://telegra.ph/file/06103228e0d120bacf852.jpg',
            caption=f'<i>Посадка завершена. Следующий остановочный пункт: '
            f'<b>{METRO[line][index-1]}</b></i>'
        )

    await call.message.delete()
    await asyncio.sleep(random.randint(METRO_TIME[0], METRO_TIME[1]))
    await tostation(user_id, station=METRO[line][index-1])
    await metrocall(call)


async def transfer_metro(call: CallbackQuery):
    '''
    Callback for a user to transfer to another line

    :param call - callback:
    '''
    user_id = call.from_user.id

    cur.update("userdata").set(line=_transfer(user_id)).where(
        user_id=user_id).commit()

    await metrocall(call)

    with contextlib.suppress(Exception):
        await call.message.delete()


async def airport(call: CallbackQuery):
    '''
    Callback for airport menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    markup = InlineKeyboardMarkup()

    match (place):
        case 'Аэропорт Котай':
            airport = 'Котай'
            markup.add(
                InlineKeyboardButton(
                    text='🛫 До Национального аэропорта',
                    callback_data='flight'
                )
            )
        case 'Национальный аэропорт':
            airport = 'Национальный аэропорт Живополис'
            markup.add(
                InlineKeyboardButton(
                    text='🛫 До Котая',
                    callback_data='flight'
                )
            )
        case _:
            return

    markup.add(
        InlineKeyboardButton(
            text='🏛 Выйти в город',
            callback_data='city'
        )
    )
    await call.message.answer(
        f'✈ <i>Вы находитесь в аэропорту <b>{airport}</b></i>',
        reply_markup=markup
    )


async def flight(call: CallbackQuery):
    '''
    Callback for an airplane flight

    :param call - callback:
    '''
    if not isinterval('plane'):
        return await call.answer(
            'Посадка ещё не началась. Самолёт прилетит через'
            f' {remaining("plane")}',
            show_alert=True
        )

    if call.data == "flight_confirm":
        user_id = call.from_user.id
        balance = cur.select("balance", "userdata").where(
            user_id=user_id).one()

        if balance <= aircost:
            return await call.message.answer(
                '<i>У вас недостаточно средств :(</i>'
            )

        place = cur.select("current_place", "userdata").where(
            user_id=user_id).one()
        cur.update("userdata").add(balance=-aircost).where(
            user_id=user_id).commit()

        sleep_time = random.randint(AIRPLANE_TIME[0], AIRPLANE_TIME[1])

        if place == 'Аэропорт Котай':
            await bot.send_photo(
                call.message.chat.id,
                'https://telegra.ph/file/d34459cedf14cb4b4a19a.jpg',
                '<i>Наш самолёт направляется к <b>Национальному аэропорту '
                'Живополис</b>. Путешествие займёт не более 2 минут. Удачного '
                'полёта!</i>'
            )
            destination = 'Национальный аэропорт'
            destline = 2

        elif place == 'Национальный аэропорт':
            await bot.send_photo(
                call.message.chat.id,
                'https://telegra.ph/file/d34459cedf14cb4b4a19a.jpg',
                '<i>Наш самолёт направляется к <b>Аэропорту Котай</b>. Путешес'
                'твие займёт не более 2 минут. Удачного полёта!</i>'
            )
            destination = 'Аэропорт Котай'
            destline = 1
        else:
            return

        # await achieve(a, call.message.chat.id, 'flightach')
        await asyncio.sleep(sleep_time)
        await tostation(user_id, station=destination, line=destline)

        return await airport(call)

    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text='🛫 Лететь', callback_data='flight_confirm'),
        InlineKeyboardButton(text='🚫 Отмена', callback_data='cancel_action')
    )
    await call.message.answer(
        f'<i>🛩 Полёт на самолёте стоит <b>${aircost}</b>. Вы уверены, что '
        'хотите продолжить?</i>',
        reply_markup=markup
    )


async def regtrain_lounge(call: CallbackQuery):
    '''
    Callback for railway platform vestibule menu

    :param call - callback:
    '''
    user_id = call.from_user.id
    token = cur.select("regtraintoken", "userdata").where(
        user_id=user_id).one()

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text='🚆 Пройти на платформу',
            callback_data='proceed_regtrain'
        )
    )
    markup.add(
        InlineKeyboardButton(
            text='🎫 Покупка билетов',
            callback_data='regtrain_tickets'
        )
    )
    await call.message.answer(
        f'<i>У вас <b>{token}</b> билетов</i>',
        reply_markup=markup
    )


async def proceed_regtrain(call: CallbackQuery):
    '''
    Callback for entering a railway stop

    :param call - callback:
    '''
    user_id = call.from_user.id
    token = cur.select("metrotoken", "userdata").where(user_id=user_id).one()

    if token < 1:
        markup = InlineKeyboardMarkup()
        markup.add()
        return await call.message.answer(
            '<i>🚫 У вас недостаточно билетов</i>',
            reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(
                        text='🎫 Покупка билетов',
                        callback_data='regtrain_tickets'
                    )
                )
            )

    cur.update("userdata").add(regtraintoken=-1).where(
        user_id=user_id).commit()
    await regtraincall(call)


async def regtraincall(call: CallbackQuery):
    '''
    Callback for regional economy class station

    :param call - callback:
    '''
    user_id = call.from_user.id
    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    index = REGTRAIN[1].index(place)
    markup = InlineKeyboardMarkup()
    desc = str()
    if index in [0, len(REGTRAIN[1] - 1)]:
        desc += (
            '<b>Конечная.</b> Поезд дальше не идёт, просьба пассажиров'
            ' выйти из вагонов'
        )
    if index > 0:
        markup.add(
            InlineKeyboardButton(
                text=f'⬅ До ст. {REGTRAIN[0][0]}',
                callback_data='regtrain_back'
            )
        )
    if index < len(REGTRAIN[1])-1:
        markup.add(
            InlineKeyboardButton(
                text=f'➡ До ст. {REGTRAIN[0][len(REGTRAIN[0])-1]}',
                callback_data='regtrain_forward'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='🏛 Выйти в город',
            callback_data='city'
        )
    )
    message = await call.message.answer_photo(
        REGIONAL_MAP,
        caption=f'<i>Остановочный пункт <b>{place}</b>\n{desc}</i>',
        reply_markup=markup
    )
    await asyncio.sleep(ticket_time)

    with contextlib.suppress(Exception):
        await message.delete()


async def regtrain_forward(call: CallbackQuery):
    user_id = call.from_user.id

    if not isinterval('regtrain'):
        return await call.answer(
            "Посадка ещё не началась. Поезд приедет через "
            f"{remaining('regtrain')}",
            show_alert=True
        )

    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    index = REGTRAIN[1].index(place)

    await call.message.answer_photo(
        'https://telegra.ph/file/71edfc6f9d47e6ea68b3f.jpg',
        f'<i>Следующая остановка: <b>{REGTRAIN[0][index+1]}</b>. Осторожно,'
        ' двери закрываются!</i>'
    )

    with contextlib.suppress(Exception):
        await call.message.delete()
    await asyncio.sleep(random.randint(REGTRAIN_TIME[0], REGTRAIN_TIME[1]))
    await tostation(user_id, station=REGTRAIN[1][index+1])
    await regtraincall(call)


async def regtrain_back(call: CallbackQuery):
    user_id = call.from_user.id

    if not isinterval('regtrain'):
        return await call.answer(
            "Посадка ещё не началась. Поезд приедет через "
            f"{remaining('regtrain')}",
            show_alert=True
        )

    place = cur.select("current_place", "userdata").where(
        user_id=user_id).one()
    index = REGTRAIN[1].index(place)

    await call.message.answer_photo(
        'https://telegra.ph/file/71edfc6f9d47e6ea68b3f.jpg',
        f'<i>Следующая остановка: <b>{REGTRAIN[0][index-1]}</b>. Осторожно,'
        ' двери закрываются!</i>'
    )

    with contextlib.suppress(Exception):
        await call.message.delete()
    await asyncio.sleep(random.randint(REGTRAIN_TIME[0], REGTRAIN_TIME[1]))
    await tostation(user_id, station=REGTRAIN[1][index-1])
    await regtraincall(call)
