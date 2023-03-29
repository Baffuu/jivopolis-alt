import contextlib
from ...database.functions import cur, conn, Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, buy, bot, get_link, get_mask, buybutton, itemdata
from ...config import METRO, WALK, CITY, trains, villages, walks, ITEMS, lvlcar, limeteds, lvlcab, cabcost, locations, clanitems
import asyncio
import time
from ...misc import get_building
from ... import logger
import random

async def city(message: Message, user_id: str):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={user_id}").fetchone()[0]
    line = cur.execute(f"SELECT line FROM userdata WHERE user_id={user_id}").fetchone()[0]
    car = cur.execute(f"SELECT blue_car+red_car FROM userdata WHERE user_id={user_id}").fetchone()[0] #todo MORE CARS

    markup = InlineKeyboardMarkup(row_width = 6)

    if place not in METRO[line]:
        for thisline in METRO:
            if place in thisline:
                cur.execute(f"UPDATE userdata SET line={METRO.index(thisline)} WHERE user_id={user_id}")
                conn.commit()

                line = METRO.index(thisline)

                break

    if line in [2, 0]:
        metro = InlineKeyboardButton(text="🚉", callback_data="metro")
    else:
        metro = InlineKeyboardButton(text="🚇", callback_data="metro")

    caritem = InlineKeyboardButton(text="🚗", callback_data="car_menu")
    trbusitem = InlineKeyboardButton(text="🚎", callback_data="trolleybus")
    trainitem = InlineKeyboardButton(text="🚆", callback_data="railway_station")
    trlounge = InlineKeyboardButton(text="🚆", callback_data="lounge")
    taxi = InlineKeyboardButton(text="🚕", callback_data="taxi_menu")
    busitem = InlineKeyboardButton(text="🚌", callback_data="bus")
    lounge = InlineKeyboardButton(text="🚌", callback_data="bus_lounge")
    trans = []
    for thisline in METRO:
        if place in thisline:
            trans.append(metro)
            break
    if place in CITY:
        trans.append(trbusitem)
    if place in trains[0]:
        if place in ["Вокзальная", "Александровская", "Станция Котай"]:
            trans.append(trainitem)
        else:
            trans.append(trlounge)
    if place in villages:
        if place in ["Автовокзал Живополис", "АС Александрово"]:
            trans.append(busitem)
        else:
            trans.append(lounge)
    if place in CITY:
        trans.append(taxi)
        if car>=1:
            trans.append(caritem)
    markup.add(*trans)

    location_button = get_building(place)
    if location_button is not None: markup.add(location_button)

    index = -1
    iswalk = next((WALK.index(wlk) for wlk in WALK if place in wlk), -1)
    for wnk in WALK:
        walkindex = WALK.index(wnk)
        if iswalk == -1 or walkindex == iswalk or wnk[WALK[iswalk].index(place)] == "":
            continue
        index = WALK[iswalk].index(place)

        markup.add(InlineKeyboardButton(text=f"🚶 {wnk[index]} - {walks[index]} секунд ходьбы".format(wnk[index], walks[index]), callback_data="walk_{0}".format(wnk[index])))



    '''cur.execute("SELECT * FROM clandata WHERE islocation=1 AND hqplace=? AND type=?", (place, "public",))
    for row in cur:
        markup.add(InlineKeyboardButton(text="🏢 {0}".format(row[1]), url=row[8]))'''

    markup.add(InlineKeyboardButton(text="📡 GPS", callback_data="gps"))
    markup.add(InlineKeyboardButton(text="🏢 Кланы рядом", callback_data="local_clans"), 
    InlineKeyboardButton(text="👤 Кто здесь?", callback_data="local_people"))
    await message.answer("<i>В Живополисе есть много чего интересного!\n&#127963; <b>{0}</b></i>".format(place), parse_mode = "html", reply_markup = markup)
    chid = message.chat.id

async def buycall(call: CallbackQuery):
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
        if ITEMS[item][4][0] == 'car':
            level = cur.execute(f"SELECT level FROM userdata WHERE user_id={user_id}").fetchone()[0]
            if level<lvlcar:
                return await call.answer(text='❌ Данная функция доступна только с уровня {0}'.format(lvlcar), show_alert = True)

            #await achieve(a.id, call.message.chat.id, 'myauto')
        await buy(call, item, user_id, cost=ITEMS[item][3]+tip, amount=amount)
    else:
        raise ValueError("no such item")

async def car_menu(call: CallbackQuery):
    message = call.message
    user_id = call.from_user.id
    car = cur.execute(f"SELECT red_car+blue_car FROM userdata WHERE user_id={user_id}").fetchone()[0] #todo more cars

    if car<1:
        return await call.answer('❌ У вас нет машины', show_alert = True)

    markup = InlineKeyboardMarkup(row_width=2)
    places = [
        InlineKeyboardButton(
            text=f'{place}', callback_data=f'goto_on_car_{place}'
        )
        for place in CITY
    ]
    markup.add(*places)
    await message.answer('<i>👨‍✈️ Выберите место для поездки.</i>', parse_mode='html', reply_markup=markup)

async def goto_on_car(call: CallbackQuery):
    user_id = call.from_user.id
    car = cur.execute(f"SELECT red_car+blue_car FROM userdata WHERE user_id = {user_id}").fetchone()[0]

    if car < 1:
        return await call.message.answer('<i>&#128663; У вас нет машины</i>', parse_mode='html')

    station = call.data[12:]
    await call.message.answer('<i>Скоро приедем!</i>', parse_mode='html')

    with contextlib.suppress(Exception):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    await asyncio.sleep(15)
    cur.execute(f"UPDATE userdata SET current_place=\"{station}\" WHERE user_id={user_id}")
    conn.commit()
    await city(call.message, call.from_user.id)

async def local_people(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id = {call.from_user.id}").fetchone()[0]
    usercount = cur.execute(f"SELECT count(*) FROM userdata WHERE current_place = '{place}'").fetchone()[0]

    if usercount < 1:
        return await call.message.answer('<i>👤 Вы стоите один, оглядываясь по сторонам…</i>\n\
            \n😓 В вашей местности не найдено людей. Помимо вас, само собой.', parse_mode = 'html')

    cur.execute(f"SELECT * FROM userdata WHERE current_place = '{place}'")

    users = ''.join(
        f'\n{index}. <a href="{get_link(row[1])}">{get_mask(row[1])} {row[2]}</a>'
        for index, row in enumerate(cur.fetchall(), start=1)
    )
    await call.message.answer(f'<i>&#128100; Пользователи в местности <b>{place}</b>: <b>{users}</b></i>', parse_mode = 'html')

async def delivery_menu(call: CallbackQuery):
    a = call.from_user.id
    phone = cur.execute(f"SELECT phone FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if phone<1:
        return await call.answer('Вам нужен телефон. Его можно купить в магазине на ул. Генерала Шелби и одноимённой станции метро', show_alert = True)

    markup = InlineKeyboardMarkup(row_width = 1)
    sellitems = ['snegovik', 'snow', 'tree', 'fairy', 'santa_claus', 'mrs_claus', 'firework', 'fireworks', 'confetti', 'clown', 'ghost', 'alien', 'robot', 'shit', 'moyai', 'pasta', 'rice', 'sushi']

    for item in sellitems:
        try:
            sellitems.append(buybutton(item, tip = 15))
        except ValueError:
            logger.error(f'no such item: {item}')
    
    sellitems = list(filter(lambda item: item is not None, sellitems))
    sellitems = list(filter(lambda item: type(item) is InlineKeyboardButton, sellitems))

    markup.add(*sellitems)
    markup.add(InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))

    await call.message.answer('<i>🚚 Здесь вы можете заказать себе любой товар из ТЦ МиГ из любого места, даже из самой глухой деревни. Это обойдётся дороже, чем в ТЦ, зато удобнее :)</i>', parse_mode='html', reply_markup = markup)
            
async def central_market_menu(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place!='Рынок':
        return #todo answer
    
    markup = InlineKeyboardMarkup(row_width=2).\
        add(InlineKeyboardMarkup(text='🍦 Продажа еды', callback_data='central_market_food'), 
        InlineKeyboardMarkup(text='👕 Продажа масок', callback_data='central_market_mask'),
        InlineKeyboardMarkup(text='🚪 Выйти', callback_data='cancel_action'))

    await call.message.answer('<i><b>🏣 Центральный рынок</b> - место, в котором можно продать купленные товары. Дешевле, чем в магазине, но удобно\n\
        \n❗ Здесь вы <b>продаёте</b> товары государству, а не покупаете. Деньги вы получаете автоматически, ваш товар никому не достаётся</i>', reply_markup = markup, parse_mode = 'html')

async def central_market_food(call: CallbackQuery):
    user_id = call.from_user.id
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if place!='Рынок':
        return #todo answer

    markup = InlineKeyboardMarkup(row_width = 3)
    itemlist = []
    coef = 1.5 #todo cur.execute(f"SELECT coef FROM globaldata").fetchone()[0]

    for item in ITEMS:
        if await itemdata(user_id, item) != 'emptyslot' and ITEMS[item][4][0] == 'food' and ITEMS[item][3] > 0:
            cost = ITEMS[item][3]//coef
            itemlist.append(InlineKeyboardButton(text=f'{ITEMS[item][0]} - ${cost}', callback_data=f'sellitem_{item}'))

    if not itemlist:
        desc = '🚫 У вас нет еды для продажи'
    else:
        markup.add(*itemlist)
        desc = '<b>🏣 Центральный рынок</b> - место, в котором можно продать купленные товары. Дешевле, чем в магазине, но удобно\n\n❗ Здесь вы <b>продаёте</b> товары государству, а не покупаете. Деньги вы получаете автоматически, ваш товар никому не достаётся'
    markup.add(InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))
    await call.message.answer(f'<i>{desc}</i>', reply_markup = markup, parse_mode = 'html')

async def central_market_mask(call: CallbackQuery):
    user_id = call.from_user.id
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if place != 'Рынок':
        return #todo answer

    markup = InlineKeyboardMarkup(row_width = 3)

    itemlist = []
    coef = 1.5 #todo cur.execute(f"SELECT coef FROM globaldata").fetchone()[0]

    for item in ITEMS:
        if await itemdata(user_id, item) != 'emptyslot' and ITEMS[item][4][0] == 'mask' and ITEMS[item][3] > 0:
            cost = ITEMS[item][3]//coef
            itemlist.append(InlineKeyboardButton(text=f'{ITEMS[item][0]} - ${cost}', callback_data=f'sellitem_{item}'))

    if not itemlist:
        text = '🚫 У вас нет масок для продажи'

    else:
        markup.add(*itemlist)
        text = '<b>🏣 Центральный рынок</b> - место, в котором можно продать купленные товары. Дешевле, чем в магазине, но удобно\n\n❗ Здесь вы <b>продаёте</b> товары государству, а не покупаете. Деньги вы получаете автоматически, ваш товар никому не достаётся'
    markup.add(InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))
    await call.message.answer(f'<i>{text}</i>', reply_markup = markup, parse_mode = 'html')

async def bank(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place from userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'Живбанк':
        return #todo answer
    markup = InlineKeyboardMarkup(row_width=1).\
        add(InlineKeyboardButton(text='🏦 Государственная казна', callback_data='state_balance'),
        InlineKeyboardButton(text='🤏 Ограбить', callback_data='rob_bank'))

    await call.message.answer('<i>🏦 Добро пожаловать в Банк</i>', reply_markup = markup, parse_mode = 'html')

async def state_balance(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    treasury = cur.execute("SELECT treasury FROM globaldata").fetchone()[0]

    if place != 'Живбанк':
        return #todo answer

    markup = InlineKeyboardMarkup(row_width=1).\
        add(InlineKeyboardButton(text='💰 Пожертвовать $100', callback_data='give_state 100'),
        InlineKeyboardButton(text='💰 Пожертвовать $500', callback_data='give_state 500'), 
        InlineKeyboardButton(text='💰 Пожертвовать $1000', callback_data='give_state 1000'), 
        InlineKeyboardButton(text='💰 Пожертвовать $10,000', callback_data='give_state 10000'))

    await call.message.answer(f'<i>🏦 Добро пожаловать в Казну. Сейчас тут ${treasury}</i>', reply_markup = markup, parse_mode = 'html')

async def taxi_menu(message: Message, user_id: int):
    level = cur.execute(f"SELECT level FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if level < lvlcab:
        return await message.answer(f'🚫 Данная функция доступна только с уровня {lvlcab}')

    markup = InlineKeyboardMarkup(row_width=2)
    places = [
        InlineKeyboardButton(place, callback_data=f'taxicost_{place}')
        for place in CITY
    ]
    markup.add(*places)

    await message.answer('<i>&#128661; Куда поедем?</i>', parse_mode='html', reply_markup=markup)
    return await message.answer('<i>Стоимость поездки зависит от отдалённости места, в которое вы едете.\
    Чтобы посмотреть цену поездки до определённого места, нажмите на него в списке локаций в предыдущем сообщении</i>', parse_mode='html')

async def taxicost(call: CallbackQuery, place: str):
    current_place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if place not in CITY:
        raise ValueError('no such place')

    cost = (cabcost*abs(CITY.index(place)-CITY.index(current_place)))//1
    markup = InlineKeyboardMarkup(row_width=2).\
    add(InlineKeyboardButton('🚕 Ехать', callback_data=f'taxi_goto_{place}'),
    InlineKeyboardButton('🚫 Отмена', callback_data='cancel_action'))
    return await call.message.answer(f'<i>Стоимость поездки до локации <b>{place}</b> - <b>${cost}</b></i>', parse_mode='html', reply_markup = markup)

async def taxi_goto_(call: CallbackQuery, place: str):
    user_id = call.from_user.id

    balance = cur.execute(f"SELECT balance FROM userdata WHERE user_id={user_id}").fetchone()[0]
    current_place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if place not in CITY:
        raise ValueError('no such place')

    cost = (cabcost*abs(CITY.index(place)-CITY.index(current_place)))//1

    if balance < cost:
        return await call.answer('🚫 У вас недостаточно средств для поездки', show_alert = True)

    await call.message.answer('<i>Скоро приедем!</i>', parse_mode='html')

    with contextlib.suppress(Exception):
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    await asyncio.sleep(15)

    cur.execute(f"UPDATE userdata SET current_place=\"{place}\" WHERE user_id={user_id}")
    conn.commit()
    cur.execute(f"UPDATE userdata SET balance=balance-{cost} WHERE user_id={user_id}")
    conn.commit()

    return await city(call.message, call.from_user.id)

async def gps_menu(call: CallbackQuery):
    user_id = call.from_user.id
    phone = cur.execute(f"SELECT phone FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if phone < 1:
        return await call.answer('Чтобы пользоваться GPS, вам нужен телефон. Его можно купить в магазине на ул. Генерала Шелби и одноимённой станции метро', show_alert = True)

    categorylist = []
    markup = InlineKeyboardMarkup()

    for category in locations[3]:
        if category not in categorylist:
            categorylist.append(category)
            count = sum(
                locations[3][locations[0].index(location)] == category
                for location in locations[0]
            )
            markup.add(InlineKeyboardButton(text='{0} ({1})'.format(category, count), callback_data='gpsloc_{0}'.format(category)))

    markup.add(InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))
    await call.message.answer('<i>Выберите категорию</i>', reply_markup = markup, parse_mode = 'html')

async def buy24_(call: CallbackQuery, item: str):    
    if item not in ITEMS or item not in limeteds:
        raise ValueError("no such item")
    items_left = cur.execute(f"SELECT {item} FROM globaldata").fetchone()[0]

    if items_left < 1:
        return await call.answer(text='К сожалению, этого товара сейчас нет в магазине ввиду дефицита :(\nПриходите завтра или посетите любой продуктовый магазин в Городе', show_alert = True)

    cur.execute(f"UPDATE globaldata SET {item}={item}-1")
    conn.commit()

    await buy(call, item, call.from_user.id, ITEMS[item][3])

async def buyclan_(call: CallbackQuery, item: str):
    
    if item not in clanitems:
        raise ValueError("no such item in clanitems")

    cost = clanitems[1][clanitems[0].index(item)]
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    count = cur.execute(f"SELECT count(*) FROM clandata WHERE clan_id = {chat_id}").fetchone()[0]

    if count < 1:
        raise ValueError("clan not found")

    balance = cur.execute(f"SELECT balance FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if balance<cost:
        return await call.answer('❌ У вас недостаточно средств', show_alert = True)

    cur.execute(f"UPDATE userdata SET balance=balance-{cost} WHERE user_id={user_id}")
    conn.commit()
    cur.execute(f"UPDATE userdata SET {item}={item}+1 WHERE user_id={user_id}")
    conn.commit()

    clan_bonus_devider = random.randint(1, 5)

    cur.execute(f"UPDATE clandata SET balance=balance+{cost//clan_bonus_devider} WHERE clan_id={chat_id}")
    conn.commit()
    await call.answer(f'Покупка совершена успешно. Ваш баланс: ${balance-cost}. Баланс клана пополнен на ${cost//clan_bonus_devider}', show_alert = True)

async def railway_station(call: CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1).\
        add(InlineKeyboardButton(text='💺 Зал ожидания', callback_data='lounge'),
            InlineKeyboardButton(text='🎫 Билетные кассы', callback_data='tickets'),
            InlineKeyboardButton(text='🍔 Кафетерий "Енот Кебаб"', callback_data='enot_kebab_shop'))

    await call.message.answer('<i>Пора уже валить отсюда...</i>', parse_mode='html', reply_markup=markup)

async def bus(call: CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1).\
        add(InlineKeyboardButton(text='🚌 К платформам', callback_data='bus_lounge'),
            InlineKeyboardButton(text='🎫 Билетные кассы', callback_data='tickets'),
            InlineKeyboardButton(text='🍔 Кафетерий "Енот Кебаб"', callback_data='enot_kebab'))

    await call.message.answer('<i>Пора уже валить отсюда...</i>', parse_mode='html', reply_markup=markup)
