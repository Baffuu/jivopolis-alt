from ...database.functions import cur, conn, Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, buy, bot, get_link, get_mask, buybutton, itemdata
from ...config import METRO, WALK, CITY, trains, villages, walks, ITEMS, lvlcar, limeteds, lvlcab
import asyncio
import time

async def city(message: Message, user_id: str):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={user_id}").fetchone()[0]
    line = cur.execute(f"SELECT line FROM userdata WHERE user_id={user_id}").fetchone()[0]
    car = cur.execute(f"SELECT blue_car+red_car FROM userdata WHERE user_id={user_id}").fetchone()[0] #todo MORE CARS
    
    markup = InlineKeyboardMarkup(row_width = 6)
    
    if not place in METRO[line]:
        for thisline in METRO:
            if place in thisline:
                cur.execute(f"UPDATE userdata SET line={METRO.index(thisline)} WHERE user_id={user_id}")
                conn.commit()
                
                line = METRO.index(thisline)

                break

    if line==2 or line==0:
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
    iswalk = -1
    index = -1
    for wlk in WALK:
        if place in wlk:
            iswalk = WALK.index(wlk)
            break
    for wnk in WALK:
        walkindex = WALK.index(wnk)
        if iswalk == -1 or walkindex == iswalk or wnk[WALK[iswalk].index(place)] == "":
            continue
        index = WALK[iswalk].index(place)
        markup.add(InlineKeyboardButton(text=f"🚶 {wnk[index]} - {walks[index]} секунд ходьбы".format(wnk[index], walks[index]), callback_data="walk_{0}".format(wnk[index])))
    print(time.time())
    if place=="Ботаническая": #todo match (place):
        markup.add(InlineKeyboardButton(text="🌲 Живополисский ботанический сад", callback_data="botan_garden"))
    elif place=="Живбанк":
        markup.add(InlineKeyboardButton(text="🏦 Живополисский банк", callback_data="bank"))
    elif place=="Университет":
        markup.add(InlineKeyboardButton(text="🏫 Живополисский университет", callback_data="university"))
    elif place=="Котайский Мединститут":
        markup.add(InlineKeyboardButton(text="🏫 Котайский институт медицинских наук", callback_data="university"))
    elif place=="Автопарк им. Кота":
        markup.add(InlineKeyboardButton(text="🚗 Автопарк имени Cat Painted", callback_data="car_park"))
    elif place=="ТЦ МиГ":
        markup.add(InlineKeyboardButton(text="🏬 Торговый центр МиГ", callback_data="mall"))
    elif place=="Георгиевская":
        markup.add(InlineKeyboardButton(text="🍰 Кондитерская \"СладкоЁжка\"", callback_data="candy_shop"))
    elif place=="Райбольница":
        markup.add(InlineKeyboardButton(text="🏥 Живополисская районная больница", callback_data="hospital"))
    elif place=="Старокотайский ФАП":
        markup.add(InlineKeyboardButton(text="🏥 Старокотайский фельдшерский пункт", callback_data="hospital"))
    elif place=="Зоопарк":
        markup.add(InlineKeyboardButton(text="🦊 Живополисский зоопарк", callback_data="zoo"))
    elif place=="Аэропорт Котай":
        markup.add(InlineKeyboardButton(text="✈ Аэропорт Котай", callback_data="airport"))
    elif place=="Национальный аэропорт":
        markup.add(InlineKeyboardButton(text="✈ Национальный аэропорт Живополис", callback_data="airport"))
    elif place=="Живополисский музей":
        markup.add(InlineKeyboardButton(text="🏛 Исторический музей Живополиса", callback_data="museum"))
    elif place=="Макеевка":
        markup.add(InlineKeyboardButton(text="🍏 \"Натурал\". Фрукты и овощи", callback_data="fruit_shop"))
    elif place=="Рынок":
        markup.add(InlineKeyboardButton(text="🏣 Центральный рынок", callback_data="central_market_menu"))
    elif place=="Котайский электрозавод":
        markup.add(InlineKeyboardButton(text="🏭 Котайский завод электрических деталей", callback_data="factory"))
    elif place=="Стадион":
        markup.add(InlineKeyboardButton(text="🏟 Живополис-Арена", url="t.me/jivopolistour"))
    elif place=="Роща":
        markup.add(InlineKeyboardButton(text="🌾 Ферма", callback_data="farm"))
    elif place=="Генерала Шелби":
        markup.add(InlineKeyboardButton(text="📱 Магазин техники имени Шелби", callback_data="phone_shop"))
    print(time.time())
    '''cur.execute("SELECT * FROM clandata WHERE islocation=1 AND hqplace=? AND type=?", (place, "public",))
    for row in cur:
        markup.add(InlineKeyboardButton(text="🏢 {0}".format(row[1]), url=row[8]))'''
    markup.add(InlineKeyboardButton(text="📡 GPS", callback_data="gps"))
    markup.add(InlineKeyboardButton(text="🏢 Кланы рядом", callback_data="local_clans"), InlineKeyboardButton(text="👤 Кто здесь?", callback_data="local_people"))
    await message.answer("<i>В Живополисе есть много чего интересного!\n&#127963; <b>{0}</b></i>".format(place), parse_mode = "html", reply_markup = markup)
    chid = message.chat.id

async def buycall(call: CallbackQuery):
    user_id = call.from_user.id
    item = call.data.split(':')[0][4:]
    try:
        tip = int(call.data.split(':')[1])
    except:
        tip = 0
    if item in ITEMS:
        if ITEMS[item][4][0] == 'car':
            level = cur.execute(f"SELECT level FROM userdata WHERE user_id={user_id}").fetchone()[0]
            if level<lvlcar:
                return await call.answer(text='❌ Данная функция доступна только с уровня {0}'.format(lvlcar), show_alert = True)
                
            #await achieve(a.id, call.message.chat.id, 'myauto')
        await buy(call, item, user_id, cost=ITEMS[item][3]+tip)
    else:
        raise ValueError("no such item")

async def car_menu(call: CallbackQuery):
    message = call.message
    user_id = call.from_user.id
    car = cur.execute(f"SELECT red_car+blue_car FROM userdata WHERE user_id={user_id}").fetchone()[0] #todo more cars

    if car<1:
        return await call.answer('❌ У вас нет машины', show_alert = True)
        
    markup = InlineKeyboardMarkup(row_width=2)
    places = []
    
    for place in CITY:
        places.append(InlineKeyboardButton(text=f'{place}', callback_data=f'goto_on_car_{place}'))
    markup.add(*places)
    await message.answer('<i>👨‍✈️ Выберите место для поездки.</i>', parse_mode='html', reply_markup=markup)

async def goto_on_car(call: CallbackQuery):
    user_id = call.from_user.id
    car = cur.execute(f"SELECT red_car+blue_car FROM userdata WHERE user_id = {user_id}").fetchone()[0]

    if car < 1:
        return await call.message.answer('<i>&#128663; У вас нет машины</i>', parse_mode='html')
        
    station = call.data[12:]
    await call.message.answer('<i>Скоро приедем!</i>', parse_mode='html')

    try:
        await bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    await asyncio.sleep(15)
    cur.execute(f"UPDATE userdata SET current_place=\"{station}\" WHERE user_id={user_id}"); conn.commit()
    await city(call.message, call.from_user.id)

async def local_people(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id = {call.from_user.id}").fetchone()[0]
    usercount = cur.execute(f"SELECT count(*) FROM userdata WHERE current_place = '{place}'").fetchone()[0]
    
    if usercount < 1:
        return await call.message.answer('<i>👤 Вы стоите один, оглядываясь по сторонам…</i>\n\
            \n😓 В вашей местности не найдено людей. Помимо вас, само собой.', parse_mode = 'html')
        
    index = 0
    users = ''

    cur.execute(f"SELECT * FROM userdata WHERE current_place = '{place}'")

    for row in cur.fetchall():
        index += 1
        users += f'\n{index}. <a href="{get_link(row[1])}">{get_mask(row[1])} {row[2]}</a>'

    await call.message.answer(f'<i>&#128100; Пользователи в местности <b>{place}</b>: <b>{users}</b></i>', parse_mode = 'html')

async def phone_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'Генерала Шелби':
        return #todo callback answer

    await call.message.answer('<i>📱 Добро пожаловать в магазин техники имени Шелби</i>', reply_markup = InlineKeyboardMarkup().\
        add(buybutton('phone')), parse_mode = 'html') 

async def candy_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    if place != 'Георгиевская':
        return #todo callback answer
    markup = InlineKeyboardMarkup(row_width=1)
    buttons = [buybutton('donut'), buybutton('cake'), buybutton('cookie'),
               #buybutton('yogurt'),
               buybutton('chocolate'), buybutton('ice_cream'),
               buybutton('shaved_ice')]

    sellitems = list(filter(lambda item: item is not None, sellitems))

    markup.add(*buttons)

    return await call.message.answer('<i>&#127856; Добро пожаловать в нашу кондитерскую!</i>', reply_markup = markup, parse_mode = 'html')

async def japan_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if place != 'ТЦ МиГ':
        return #todo callback answer

    markup = InlineKeyboardMarkup(row_width=1)
    buttons = [buybutton('bento'), buybutton('pasta'), buybutton('rice')]

    sellitems = list(filter(lambda item: item is not None, sellitems))

    markup.add(*buttons)

    return await call.message.answer('<i>&#127857; Добро пожаловать в ресторан восточной кухни "Япон Енот"!</i>', reply_markup = markup, parse_mode = 'html')

async def mall(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'ТЦ МиГ':
        return #todo callback answer

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='👚 ModaShop', callback_data='moda_shop'), 
               InlineKeyboardButton(text='🍔 Енот Кебаб', callback_data='enot_kebab'),
               InlineKeyboardButton(text='🍚 Ресторан Япон Енот', callback_data='japan_shop'))

    return await call.message.answer('<i>&#127978; Добро пожаловать в торговый центр!</i>', reply_markup = markup, parse_mode = 'html')

async def moda_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if place != 'ТЦ МиГ':
        return #todo answer

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='❄️ Новогодний отдел', callback_data='xmas_shop'),
                InlineKeyboardButton(text='👺 Маскарадный отдел', callback_data='mask_clothes'))

    return await call.message.answer('<i>&#128090; Добро пожаловать в <b>ModaShop</b>! Здесь вы можете купить любую одежду!</i>', reply_markup = markup, parse_mode = 'html')
    
async def xmas_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if place != 'ТЦ МиГ':
        return #todo

    markup = InlineKeyboardMarkup(row_width=1)
    
    buttons = [buybutton('snowman'), buybutton('snowflake'), buybutton('xmastree'), buybutton('fairy'), buybutton('santa_claus'),
    buybutton('mrs_claus'), buybutton('firework'),
    buybutton('fireworks'), buybutton('confetti')]

    markup.add(*list(filter(lambda item: item is not None, buttons)))

    return await call.message.answer('<i>Что хотите купить?</i>', reply_markup = markup, parse_mode = 'html')

async def delivery_menu(call: CallbackQuery):
    a = call.from_user.id
    phone = cur.execute(f"SELECT phone FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if phone<1:
        return await call.answer('Вам нужен телефон. Его можно купить в магазине на ул. Генерала Шелби и одноимённой станции метро', show_alert = True)

    markup = InlineKeyboardMarkup(row_width = 1)
    sellitems = ['snegovik', 'snow', 'tree', 'fairy', 'santa_claus', 'mrs_claus', 'firework', 'fireworks', 'confetti', 'clown', 'ghost', 'alien', 'robot', 'shit', 'moyai', 'pasta', 'rice', 'sushi']

    for item in sellitems:
        sellitems.append(buybutton(item, tip = 15))
        sellitems.remove(item)
    
    sellitems = list(filter(lambda item: item is not None, sellitems))
    sellitems = list(filter(lambda item: type(item) is InlineKeyboardButton, sellitems))

    markup.add(*sellitems)
    markup.add(InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))

    await call.message.answer('<i>🚚 Здесь вы можете заказать себе любой товар из ТЦ МиГ из любого места, даже из самой глухой деревни. Это обойдётся дороже, чем в ТЦ, зато удобнее :)</i>', parse_mode='html', reply_markup = markup)
            
async def fruit_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'Макеевка':
        return

    markup = InlineKeyboardMarkup(row_width=1)
    
    buttons = [buybutton('apple'), buybutton('cucumber'),
    buybutton('tomato'), buybutton('kiwi'), buybutton('cocoa')]

    markup.add(*list(filter(lambda item: item is not None, buttons)))

    await call.message.answer('<i>&#127823; Добро пожаловать в мини-магазин "Натурал"!</i>', reply_markup = markup, parse_mode = 'html')

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
    
    if itemlist == []:
        desc = '🚫 У вас нет еды для продажи'
    else:
        markup.add(*itemlist)
        desc = '<b>🏣 Центральный рынок</b> - место, в котором можно продать купленные товары. Дешевле, чем в магазине, но удобно\n\n❗ Здесь вы <b>продаёте</b> товары государству, а не покупаете. Деньги вы получаете автоматически, ваш товар никому не достаётся'
    markup.add(InlineKeyboardMarkup(text='◀ Назад', callback_data='cancel_action'))
    await call.message.answer(f'<i>{desc}</i>', reply_markup = markup, parse_mode = 'html')

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
    treasury = cur.execute(f"SELECT treasury FROM globaldata").fetchone()[0]
    
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
    places = []
    
    for place in CITY:
        places.append(InlineKeyboardButton(place, callback_data=f'taxicost_{place}'))
    
    markup.add(*places)

    await message.answer('<i>&#128661; Куда поедем?</i>', parse_mode='html', reply_markup=markup)
    return await message.answer('<i>Стоимость поездки зависит от отдалённости места, в которое вы едете.\
    Чтобы посмотреть цену поездки до определённого места, нажмите на него в списке локаций в предыдущем сообщении</i>', parse_mode='html')