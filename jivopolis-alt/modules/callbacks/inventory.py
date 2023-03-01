import random
from math import ceil
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from ...database.sqlitedb import cur, conn
from ...config import ITEMS, limeteds
from ...database.functions import itemdata, current_time

async def itemdesc(call: CallbackQuery, user_id: int):
    item = call.data

    count = cur.execute(f"SELECT {item} FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if count < 1:
        return await call.message.answer('<i>&#10060; У вас нет этого предмета</i>', reply_markup = markup, parse_mode = 'html')
    try:
        mask = cur.execute(f"SELECT mask FROM userdata WHERE user_id={user_id}").fetchone()[0]
    except TypeError:
        mask = None

    status = ITEMS[item][4][0]

    markup = InlineKeyboardMarkup()

    if status == 'food': #todo match case
        markup.add(InlineKeyboardButton(text='🍖 Съесть', callback_data=f'eat_{item}'))
    elif status == 'medicine':
        markup.add(InlineKeyboardButton(text='💊 Выпить', callback_data='drink_medicine'))
    elif status == 'car':
        markup.add(InlineKeyboardButton(text='🚗 В путь!', callback_data='cardrive'))
    elif status == 'lootbox':
        markup.add(InlineKeyboardButton(text='📦 Открыть', callback_data='open_lootbox'))
    elif status == 'rob':
        markup.add(InlineKeyboardButton(text='🏦 Ограбить банк', callback_data='rob_bank'))
    elif status == 'mask':
        if ITEMS[item][0] == mask:
            markup.add(InlineKeyboardButton(text='❎ Снять', callback_data='putoff'))
        else:
            markup.add(InlineKeyboardButton(text='👺 Надеть', callback_data=f'puton_{item}'))
    elif status == 'key':
        markup.add(InlineKeyboardButton(text='🔐 Чёрный рынок', callback_data='darkweb'))
    elif status == 'phone':
        markup.add(InlineKeyboardButton(text='📱 Использовать', callback_data='smartphone'))
    rem = ''
    if call.data in limeteds:
        cur.execute(f"SELECT {item} FROM globaldata")
        itemrem = cur.fetchone()[0]
        rem = "\n\n&#127978; В круглосуточном осталось <b>{0}</b> единиц этого товара".format(itemrem)
    return await call.message.answer('<i><b>{0} {1}</b> - {2}{3}\n\nУ вас <b>{4}</b> единиц этого предмета</i>'.format(ITEMS[item][0], ITEMS[item][2], ITEMS[item][5], rem, count), reply_markup = markup, parse_mode = 'html')

async def inventory(call: CallbackQuery):
    user_id = call.from_user.id
    markup = InlineKeyboardMarkup(row_width = 6)

    itemlist = []
    item: str

    for item in ITEMS:
        if await itemdata(user_id, item) != 'emptyslot':
            itemlist.append(await itemdata(user_id, item))

    if itemlist != []:
        markup.add(*itemlist)
    else:
        markup.add(InlineKeyboardButton('🙈 Нет предметов', callback_data='no_items_in_inventory'))
    
    try:
        mask = cur.execute(f"SELECT mask FROM userdata WHERE user_id={user_id}").fetchone()[0]
        print(mask)
    except TypeError:
        mask = ''
    if not mask:
        mask = ''
        
    if mask != '':
        markup.add(InlineKeyboardButton(text='❎ Снять маску', callback_data='put_mask_off'))

    markup.add(InlineKeyboardButton(text='🏪 Круглосуточный магазин', callback_data='shop_24'))
    
    await call.message.answer('<i>Ваш инвентарь</i>', reply_markup = markup, parse_mode = 'html')

async def put_mask_off(call: CallbackQuery, user_id: int):
    mask = cur.execute(f"SELECT mask FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if mask:
        for item in ITEMS:
            if ITEMS[item][0] == mask:
                mask = item

        cur.execute(f"UPDATE userdata SET mask = NULL WHERE user_id = {user_id}")
        conn.commit()

        cur.execute(f"UPDATE userdata SET {mask} = {mask} + 1 WHERE user_id = {user_id}")
        conn.commit()

        return call.answer('🦹🏼 Ваша маска снята.', show_alert=True)
    else:
        return

async def open_lootbox(user_id: int, message: Message): #todo: NEW BOXES
    mailbox = cur.execute(f"SELECT last_box FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    difference: float = current_time() - mailbox
    lootbox: int = cur.execute(f"SELECT lootbox FROM userdata WHERE user_id={user_id}").fetchone()[0]
    if difference >= 86400:
        cur.execute(f"UPDATE userdata SET last_box = {current_time()} WHERE user_id = {user_id}")
        conn.commit()
    elif lootbox > 0:
        cur.execute(f"UPDATE userdata SET lootbox = lootbox - 1 WHERE user_id = {user_id}")
        conn.commit()
    else:
        h = int(24-ceil(difference/3600))
        m = int(60-ceil(difference%3600/60))
        s = int(60-ceil(difference%3600%60))
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text='🖇 Пригласить пользователей', callback_data='reflink'))
        return await message.answer(f'<i>&#10060; Проверять почтовый ящик можно только 1 раз в 24 часа. До следующей проверки осталось {h} часов {m} минут {s} секунд.\n\nЧтобы получать внеочередные ящики, приглашайте пользователей в Живополис. За каждого приглашённого пользователя вы получаете лутбокс, с помощью которого можно открыть ящик в любое время</i>', parse_mode='html', reply_markup=markup)
    
    situation = random.uniform(0, 1)

    if situation>=0.2:
        rand = random.randint(1,26)

        cur.execute(f"UPDATE userdata SET balance = balance + {rand} WHERE user_id = {user_id}")
        conn.commit()
        return await message.answer(f'<i><b>Поздравляем!</b>\nВы заработали <b>${rand}</b></i>', parse_mode = 'html')
    else:
        return await message.answer('<i>В ящике вы нашли только старую газету, которая теперь не стоит ни гроша</i>', parse_mode = 'html')