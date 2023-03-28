from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from ...database.functions import cur, conn
from ...config import ITEMS, TESTCHAT, JIVADMCHAT, LOGCHATLINK, BAFFUADM, MEGACHATLINK
from ... import bot
import os, sys

async def adminpanel(call: CallbackQuery, user_id: int):
    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if rank < 2:
        return await call.answer("❌ Эта команда доступна только администраторам Живополиса", show_alert = True)
        
    markup = InlineKeyboardMarkup(row_width = 1)
    markup.add(InlineKeyboardButton(text = '❓ Помощь', callback_data='adminhelp'), 
               InlineKeyboardButton(text = '💼 Информация по предметам', callback_data='itemsinfo_table'), 
               InlineKeyboardButton(text = '📁 Файлы Живополиса', callback_data='backup'), 
               InlineKeyboardButton(text = '💬 Админские чаты', callback_data='adminchats'))

    if rank > 2:
        markup.add(InlineKeyboardButton(text='♻️ Перезапустить бота', callback_data='restart_bot'))
    await call.message.answer("<i>Эти функции доступны админам. Только тсс</i>", parse_mode='html', reply_markup=markup)
        
async def itemsinfo_table(call: CallbackQuery, user_id: int):
    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if rank < 2:
        return await call.answer("❌ Эта команда доступна только администраторам Живополиса", show_alert = True)

    markup = InlineKeyboardMarkup(row_width = 10)
    items = [
        InlineKeyboardButton(
            text=ITEMS[item][0], callback_data=f'iteminfo_{item}'
        )
        for item in ITEMS
    ]
    markup.add(*items)
    await call.message.answer("<i>Здесь вы можете получить секретную информацию обо всех предметах в Живополисе</i>", parse_mode='html', reply_markup=markup)

async def itemsinfo_item(call: CallbackQuery, user_id: int):
    item = call.data.split('_')[1]

    if item not in ITEMS:
        return

    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if rank < 2:
        return await call.answer("❌ Эта команда доступна только администраторам Живополиса", show_alert = True)

    cost = 'не продается' if ITEMS[item][3] < 0 else ITEMS[item][3]
    match (ITEMS[item][4][0]):
        case 'food':
            itemtype = 'еда'
        case 'mask':
            itemtype = 'маска'
        case 'car':
            itemtype = 'машина'
        case _:
            itemtype = 'undefined'

    await call.answer(f'{ITEMS[item][0]}{ITEMS[item][2]}\nКод: {item}\nТип: {itemtype}\nСтоимость: ${cost}', show_alert = True)

async def adminhelp(call: CallbackQuery, user_id: int):
    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if rank < 2:
        return await call.answer("👨‍⚖️ Сударь, эта команда доступна только администраторам. ", show_alert = True)
        
    return await call.message.answer("<i><b>Статьи для админов</b>\nАдминская документация: https://telegra.ph/Administratorskaya-dokumentaciya-ZHivopolisa-01-03\nПособие по использованию /sqlrun: https://telegra.ph/Administratorskaya-dokumentaciya-ZHivopolisa-Komanda-sqlrun-07-25</i>", parse_mode='html')

async def sqlapprove(call: CallbackQuery):
    try:
        request_user_id = call.data.split(':')[2]
        user_id = call.from_user.id
        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]

        if rank < 3:
            return call.answer('👨‍⚖️ Сударь, эта команда доступна только администраторам.', show_alert=True)
        
        request: str = cur.execute(f"SELECT sql FROM userdata WHERE user_id={request_user_id}").fetchone()[0]

        if not request:
            return call.answer("404: request not found")
        
        cur.execute(f"UPDATE userdata SET sql=NULL WHERE user_id={request_user_id}")
        conn.commit()

        await bot.send_message(user_id, f'✅ <i>Ваш запрос был подтверждёn:\n\n<code>{request}</code></i>')
        
        cur.execute(request)
        if "select" in request.lower():
            try:
                rval = ''
                for row in cur.fetchall():
                    for slot in row:
                        rval = rval+'\n'+str(slot)
                await call.message.answer(f'<i><b>Значения: \n</b>{rval}</i>', parse_mode='html')
                if request_user_id  !=  user_id:
                    await bot.send_message(request_user_id, f'<i><b>Значения: \n</b>{rval}</i>', parse_mode='html')
            except Exception as e:
                await call.message.answer(f'<i><b>Произошла незначительная ошибка при обработке запроса:</b> {e}</i>', parse_mode='html')
                await call.message.answer('<i>Запрос обработан</i>', parse_mode='html')
                if request_user_id!=user_id:
                    await bot.send_message(request_user_id, '<i>Запрос обработан</i>')
        else:
            conn.commit()
        
    except Exception as e:
        await call.message.answer(f'<i><b>Запрос не обработан: \n</b>{e}</i>', parse_mode = 'html')
        if request_user_id!=user_id:
            await bot.send_message(request_user_id, f'<i><b>Запрос не обработан: \n</b>{e}</i>')

async def sqldecline(call: CallbackQuery):
    try:
        request_user_id = call.data.split(':')[2]
        user_id = call.from_user.id
        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]
        
        if rank < 3:
            return call.answer('👨‍⚖️ Сударь, эта команда доступна только администраторам.', show_alert=True)

        request = cur.execute(f"SELECT sql FROM userdata WHERE user_id={request_user_id}").fetchone()[0]
       
        cur.execute(f"UPDATE userdata SET sql=NULL WHERE user_id={request_user_id}")
        conn.commit()

        await call.answer('Запрос отклонён', show_alert=True)
        await bot.send_message(request_user_id, f'❌ <i>Ваш запрос был отклонён создателем:\n\n<code>{request}</code></i>', parse_mode='html')
        return await bot.delete_message(call.message.chat.id, call.message.message_id)
    
    except Exception as e:
        return await call.message.answer(f'<i><b>&#10060; Ошибка: </b>{e}</i>', parse_mode = 'html')

async def adminchats(call: CallbackQuery):
    user_id = call.from_user.id
    rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id={user_id}").fetchone()[0]

    markup = InlineKeyboardMarkup(row_width=1)

    if rank < 1:
        return await call.answer("👨‍⚖️ Сударь, эта команда доступна только администраторам.", show_alert = True)
    if rank > 0:
        markup.add(InlineKeyboardButton('👾 Тестирование Живополиса', TESTCHAT),
        InlineKeyboardButton('📣 Администрация Живополиса', JIVADMCHAT),
        InlineKeyboardButton('👨‍🔧 LOG CHAT', LOGCHATLINK))
    if rank > 1:
        markup.add(InlineKeyboardButton('🧞 Администрация Baffu', BAFFUADM))
    if rank > 2:
        markup.add(InlineKeyboardButton('🦹🏼 МегаЧат', MEGACHATLINK))

    await call.message.answer_sticker('CAACAgIAAxkBAAIEN2QE3dP0FVb2HNOHw1QC2TMpUEpsAAK7IAACEkDwSZtWAAEk41obpC4E')
    await call.message.answer("<i><b>🧑‍💻 Админские чаты живополиса:</b>\n💻 Разработка Живополиса: https://t.me/+k2LZEIyZtpRiMjcy</i>", parse_mode='html', reply_markup=markup)

async def restart(call: CallbackQuery):
    try:
        rank = cur.execute(f"SELECT rank FROM userdata WHERE user_id = {call.from_user.id}").fetchone()[0]
        
        if rank < 3:
            return await call.answer("👨‍⚖️ Сударь, эта команда доступна только администраторам.", show_alert = True)
            
        await call.answer("🌀 Перезагрузка...")
        os.execv(sys.executable, ['python3'] + sys.argv)
        
    except Exception as e:
        await call.message.answer(f'<i><b>♨️ Ошибка: </b>{e}</i>', parse_mode = 'html')