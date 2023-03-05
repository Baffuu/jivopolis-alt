from ...database.functions import cur, conn, Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, buy
from ...config import METRO, WALK, CITY, trains, villages, walks, ITEMS, lvlcar

async def city(message: Message, user_id: str):
    place = cur.execute(f"SELECT place FROM userdata WHERE user_id={user_id}").fetchone()[0]
    line = cur.execute(f"SELECT line FROM userdata WHERE user_id={user_id}").fetchone()[0]
    car = cur.execute(f"SELECT car+bluecar FROM userdata WHERE user_id={user_id}").fetchone()[0] #todo MORE CARS
    
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

    caritem = InlineKeyboardButton(text="🚗", callback_data="cardrive")
    trbusitem = InlineKeyboardButton(text="🚎", callback_data="trolleybus")
    trainitem = InlineKeyboardButton(text="🚆", callback_data="railway_station")
    trlounge = InlineKeyboardButton(text="🚆", callback_data="lounge")
    taxi = InlineKeyboardButton(text="🚕", callback_data="cab")
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
        markup.add(InlineKeyboardButton(text="🚶 {0} - {1} секунд ходьбы".format(wnk[index], walks[index]), callback_data="walk_{0}".format(wnk[index])))
    if place=="Ботаническая":
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
        markup.add(InlineKeyboardButton(text="🏣 Центральный рынок", callback_data="central_market"))
    elif place=="Котайский электрозавод":
        markup.add(InlineKeyboardButton(text="🏭 Котайский завод электрических деталей", callback_data="factory"))
    elif place=="Стадион":
        markup.add(InlineKeyboardButton(text="🏟 Живополис-Арена", url="t.me/jivopolistour"))
    elif place=="Роща":
        markup.add(InlineKeyboardButton(text="🌾 Ферма", callback_data="farm"))
    elif place=="Генерала Шелби":
        markup.add(InlineKeyboardButton(text="📱 Магазин техники имени Шелби", callback_data="phone_shop"))
    cur.execute("SELECT * FROM clandata WHERE islocation=1 AND hqplace=? AND type=?", (place, "public",))
    for row in cur:
        markup.add(InlineKeyboardButton(text="🏢 {0}".format(row[1]), url=row[8]))
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