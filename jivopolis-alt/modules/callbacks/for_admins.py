from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from ...database.sqlitedb import cur
from ...config import ITEMS

async def adminpanel(call: CallbackQuery, user_id: int):
    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if rank < 2:
        return await call.answer("❌ Эта команда доступна только администраторам Живополиса", show_alert = True)
        
    markup = InlineKeyboardMarkup(row_width = 1)
    markup.add(InlineKeyboardButton(text = '❓ Помощь', callback_data='adminhelp'), 
               InlineKeyboardButton(text = '💼 Информация по предметам', callback_data='itemsinfo_table'), 
               InlineKeyboardButton(text = '📁 Файлы Живополиса', callback_data='backup'), 
               InlineKeyboardButton(text = '💬 Админские чаты', callback_data='adminchats'))
    await call.message.answer("<i>Эти функции доступны админам. Только тсс</i>", parse_mode='html', reply_markup=markup)
            
async def itemsinfo_table(call: CallbackQuery, user_id: int):
    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if rank < 2:
        return await call.answer("❌ Эта команда доступна только администраторам Живополиса", show_alert = True)
        
    markup = InlineKeyboardMarkup(row_width = 10)
    items = []

    for item in ITEMS:
        items.append(InlineKeyboardButton(text = ITEMS[item][0], callback_data = 'iteminfo_'+ item))

    markup.add(*items)
    await call.message.answer("<i>Здесь вы можете получить секретную информацию обо всех предметах в Живополисе</i>", parse_mode='html', reply_markup=markup)

async def itemsinfo_item(call: CallbackQuery, user_id: int):
    item = call.data.split('_')[1]

    if item not in ITEMS:
        return
    
    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]
    
    if rank < 2:
        return await call.answer("❌ Эта команда доступна только администраторам Живополиса", show_alert = True)
    
    if ITEMS[item][3] < 0:
        cost = 'не продается'
    else:
        cost = ITEMS[item][3]

    match (ITEMS[item][4][0]):
        case 'food':
            type = 'еда'
        case 'mask':
            type = 'маска'
        case 'car':
            type = 'машина'
        case _:
            type = 'undefined'

    await call.answer(f'{ITEMS[item][0]}{ITEMS[item][2]}\nКод: {item}\nТип: {type}\nСтоимость: ${cost}', show_alert = True)

async def adminhelp(call: CallbackQuery, user_id: int):
    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if rank < 2:
        return await call.answer("❌ Эта команда доступна только администраторам Живополиса", show_alert = True)
        
    return await call.message.answer("<i><b>Статьи для админов</b>\nАдминская документация: https://telegra.ph/Administratorskaya-dokumentaciya-ZHivopolisa-01-03\nПособие по использованию /sqlrun: https://telegra.ph/Administratorskaya-dokumentaciya-ZHivopolisa-Komanda-sqlrun-07-25</i>", parse_mode='html')