from ...database.functions import cur, conn, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, bot

async def set_user_bio(call: CallbackQuery):    
    cur.execute(f"UPDATE userdata SET process='setbio' WHERE user_id={call.from_user.id}")
    conn.commit()

    return await bot.send_message(call.message.chat.id, '<i>📝 Введите новое описание профиля:</i>', reply_markup = InlineKeyboardMarkup().\
        add(InlineKeyboardButton(text='🚫 Отмена', callback_data='cancel_process')))

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
        
async def put_mask_on(call: CallbackQuery):
    user_id = call.from_user.id
    message = call.message

    await putoff(user_id, message)
    cursor.execute('SELECT {0} FROM userdata WHERE user_id = ?'.format(code), (a,))
    itm = cursor.fetchone()[0]
    if itm>=1:
        cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
        rasa = cursor.fetchone()[0]
        cursor.execute('UPDATE userdata SET temp = ? WHERE user_id = ?', (rasa, a,))
        conn.commit()
        cursor.execute('UPDATE userdata SET rasa = ? WHERE user_id = ?', (emoji, a,))
        conn.commit()
        cursor.execute('UPDATE userdata SET mask = ? WHERE user_id = ?', (code, a,))
        conn.commit()
        cursor.execute('UPDATE userdata SET {0} = ? WHERE user_id = ?'.format(code), (itm-1, a,))
        conn.commit()
        cursor.execute('SELECT rasa FROM userdata WHERE user_id = ?', (a,))
        rasa = cursor.fetchone()[0]
        if rasa in ITEMS[6]:
            await call.answer(text='Отличный выбор! Ваша маска: {0}'.format(ITEMS[0][ITEMS[6].index(rasa)]), show_alert = True)
        else:
            await message.answer('<i>Ваша маска: {0}</i>'.format(rasa), parse_mode='html')
        await achieve(a, message.chat.id, 'msqrd')
    else:
        await call.answer(text='❌ У вас нет этого предмета', show_alert = True)