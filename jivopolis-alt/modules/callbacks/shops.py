from ...database.sqlitedb import cur, conn
from ...database.functions import buybutton

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ...config import villages, trains

async def phone_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'Генерала Шелби':
        return #todo callback answer

    await call.message.answer('<i>📱 Добро пожаловать в магазин техники имени Шелби</i>', reply_markup = InlineKeyboardMarkup().\
        add(buybutton('phone')), parse_mode = 'html') 

async def candy_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'Георгиевская':
        return
    
    buttons = [buybutton('donut'), buybutton('cake'), 
               buybutton('cookie'), buybutton('yogurt'), 
               buybutton('chocolate'), buybutton('ice_cream'),
               buybutton('shaved_ice')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    return await call.message.answer('<i>&#127856; Добро пожаловать в нашу кондитерскую!</i>', reply_markup = markup, parse_mode = 'html')

async def japan_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if place != 'ТЦ МиГ':
        return

    buttons = [buybutton('bento'), buybutton('pasta'), 
               buybutton('rice')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    return await call.message.answer('<i>&#127857; Добро пожаловать в ресторан восточной кухни "Япон Енот"!</i>', reply_markup = markup, parse_mode = 'html')

async def moda_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if place != 'ТЦ МиГ':
        return

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='❄️ Новогодний отдел', callback_data='xmas_shop'),
                InlineKeyboardButton(text='👺 Маскарадный отдел', callback_data='mask_clothes'))

    return await call.message.answer('<i>&#128090; Добро пожаловать в <b>ModaShop</b>! Здесь вы можете купить любую одежду!</i>', reply_markup = markup, parse_mode = 'html')
    
async def xmas_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if place != 'ТЦ МиГ':
        return
    
    buttons = [buybutton('snowman'), buybutton('snowflake'), 
               buybutton('xmastree'), buybutton('fairy'), 
               buybutton('santa_claus'), buybutton('mrs_claus'), 
               buybutton('firework'), buybutton('fireworks'),
               buybutton('confetti')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    return await call.message.answer('<i>Что хотите купить?</i>', reply_markup = markup, parse_mode = 'html') 

async def mall(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'ТЦ МиГ':
        return

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='👚 ModaShop', callback_data='moda_shop'), 
               InlineKeyboardButton(text='🍔 Енот Кебаб', callback_data='enot_kebab'),
               InlineKeyboardButton(text='🍚 Ресторан Япон Енот', callback_data='japan_shop'))

    return await call.message.answer('<i>&#127978; Добро пожаловать в торговый центр!</i>', reply_markup = markup, parse_mode = 'html')

async def fruit_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'Макеевка':
        return
    
    buttons = [buybutton('apple'), buybutton('cucumber'),
    buybutton('tomato'), buybutton('kiwi'), buybutton('cocoa')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    return await call.message.answer('<i>&#127823; Добро пожаловать в мини-магазин "Натурал"!</i>', reply_markup = markup, parse_mode = 'html')

async def zoo_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'Зоопарк':
        return
    
    buttons = [buybutton('morj'), buybutton('cow'),
    buybutton('yozh'), buybutton('wolf'), buybutton('fox'),
    buybutton('hamster')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))
    await call.message.answer('<i>Что хотите купить?</i>', reply_markup=markup, parse_mode = 'html')

async def enot_kebab_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}")

    if place not in villages and place not in trains[0]:
        return

    buttons = [buybutton('burger'), buybutton('shaurma'),
               buybutton('fries'), buybutton('cheburek'),
               buybutton('beer')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    await call.message.answer('<i>Что хотите купить?</i>', reply_markup = markup, parse_mode = 'html')

async def shop_24(call: CallbackQuery):
    buttons = [buybutton('bread', 'limited'), 
               buybutton('pelmeni', 'limited'),
               buybutton('soup', 'limited'), 
               buybutton('meat', 'limited'), 
               buybutton('meatcake', 'limited'), 
               buybutton('tea', 'limited')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    await call.message.answer('<i>Что хотите купить?</i>', reply_markup = markup, parse_mode = 'html')

async def botan_garden_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'Ботаническая':
        return

    buttons = [buybutton('clover'), buybutton('palm'),
              buybutton('rose'), buybutton('tulip'),
              buybutton('houseplant'), buybutton('cactus')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    await call.message.answer('<i>Что хотите купить?</i>', reply_markup=markup, parse_mode = 'html')

async def car_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]
    
    if place != 'Автопарк им. Кота':
        return

    buttons = [buybutton('red_car'),
               buybutton('blue_car')]

    markup = InlineKeyboardMarkup(row_width=1).\
        add(*list(filter(lambda item: item is not None, buttons)))

    await call.message.answer('<i>Какую машину хотите купить?</i>', reply_markup = markup, parse_mode = 'html')

async def hospital_shop(call: CallbackQuery):
    place = cur.execute(f"SELECT current_place FROM userdata WHERE user_id={call.from_user.id}").fetchone()[0]

    if place not in ['Райбольница', 'Старокотайский ФАП']:
        return

    markup = InlineKeyboardMarkup(row_width=1).\
        add(InlineKeyboardButton(text='💊 Таблетка Котробене - $500', callback_data='buy:pill:1:1'),
            InlineKeyboardButton(text='💊 Маленькая пачка (5 шт.) - $2500', callback_data='buy:pill:5:5'),
            InlineKeyboardButton(text='💊 Баночка (10 шт.) - $5000', callback_data='buy:pill:10:10'))

    await call.message.answer('<i>Что хотите приобрести?</i>', reply_markup = markup, parse_mode = 'html')