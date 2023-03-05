from ...database.functions import cur, conn, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, bot, ITEMS

async def set_user_bio(call: CallbackQuery):    
    cur.execute(f"UPDATE userdata SET process=\"setbio\" WHERE user_id={call.from_user.id}")
    conn.commit()

    return await bot.send_message(call.message.chat.id, "<i>📝 Введите новое описание профиля:</i>", reply_markup = InlineKeyboardMarkup().\
        add(InlineKeyboardButton(text="🚫 Отмена", callback_data="cancel_process")))

async def put_mask_off(call: CallbackQuery, user_id: int, anon: bool = False):
    mask = cur.execute(f"SELECT mask FROM userdata WHERE user_id={user_id}").fetchone()[0]

    if mask:
        for item in ITEMS:
            if ITEMS[item][0] == mask:
                mask = item

        cur.execute(f"UPDATE userdata SET mask = NULL WHERE user_id = {user_id}")
        conn.commit()

        cur.execute(f"UPDATE userdata SET {mask} = {mask} + 1 WHERE user_id = {user_id}")
        conn.commit()
        if not anon:
            return call.answer("🦹🏼 Ваша маска снята.", show_alert=True)
        else: return
    else: return

async def put_mask_on(call: CallbackQuery, item: str):
    user_id = call.from_user.id

    await put_mask_off(call, user_id, True)
    itemcount = cur.execute(f"SELECT {item} FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    
    if itemcount > 0:
        cur.execute(f"UPDATE userdata SET {item}={item}-1 WHERE user_id={user_id}")
        conn.commit()

        cur.execute(f"UPDATE userdata SET mask=\"{ITEMS[item][0]}\" WHERE user_id={user_id}")
        conn.commit()
    
        return await call.answer(f"Отличный выбор! Ваша маска: {ITEMS[item][0]}", show_alert = True)
        # await achieve(a, message.chat.id, "msqrd")
    else:
        await call.answer("🚫 У вас нет этого предмета", show_alert = True)