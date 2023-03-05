from ...database.functions import cur, conn, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, bot

async def set_user_bio(call: CallbackQuery):    
    cur.execute(f"UPDATE userdata SET process='setbio' WHERE user_id={call.from_user.id}")
    conn.commit()

    return await bot.send_message(call.message.chat.id, '<i>📝 Введите новое описание профиля:</i>', reply_markup = InlineKeyboardMarkup().\
        add(InlineKeyboardButton(text='🚫 Отмена', callback_data='cancel_process')))