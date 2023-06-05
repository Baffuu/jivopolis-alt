from ... import bot
from ...misc import ITEMS

from ...database import cur, conn

from aiogram.utils.deep_linking import get_start_link
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

async def set_user_bio(call: CallbackQuery) -> None:    
    cur.execute(f"UPDATE userdata SET process=\"setbio\" WHERE user_id={call.from_user.id}")
    conn.commit()

    return await bot.send_message(call.message.chat.id, "<i>📝 Введите новое описание профиля:</i>", reply_markup = InlineKeyboardMarkup().\
        add(InlineKeyboardButton(text="🚫 Отмена", callback_data="cancel_process")))


async def put_mask_off(call: CallbackQuery, user_id: int, anon: bool = False) -> None:
    if mask := cur.execute(
        f"SELECT mask FROM userdata WHERE user_id={user_id}"
    ).fetchone()[0]:
        if mask is None:
            return
        for item in ITEMS:
            if ITEMS[item].emoji == mask:
                mask = item

        cur.execute(f"UPDATE userdata SET mask = NULL WHERE user_id = {user_id}")
        conn.commit()

        cur.execute(f"UPDATE userdata SET {mask} = {mask} + 1 WHERE user_id = {user_id}")
        conn.commit()

        if not anon:
            return await call.answer("🦹🏼 Ваша маска снята.", show_alert=True)


async def put_mask_on(call: CallbackQuery, item: str) -> None:
    user_id = call.from_user.id

    await put_mask_off(call, user_id, True)
    itemcount = cur.execute(f"SELECT {item} FROM userdata WHERE user_id = {user_id}").fetchone()[0]
    
    if itemcount > 0:
        cur.execute(f"UPDATE userdata SET {item}={item}-1 WHERE user_id={user_id}")
        conn.commit()

        cur.execute(f"UPDATE userdata SET mask=\"{ITEMS[item].emoji}\" WHERE user_id={user_id}")
        conn.commit()
    
        return await call.answer(f"Отличный выбор! Ваша маска: {ITEMS[item].emoji}", show_alert = True)
        # await achieve(a, message.chat.id, "msqrd")
    else:
        await call.answer("🚫 У вас нет этого предмета", show_alert = True)


async def my_reflink(call: CallbackQuery) -> None:
    color = '0-0-0'
    bgcolor = '255-255-255'

    reflink = await get_start_link(
        payload=str(call.from_user.id),
        encode=True
    )

    await bot.send_photo(
        call.message.chat.id,
        photo=(
            f"https://api.qrserver.com/v1/create-qr-code/?data={reflink}&size=512x512&charset-source=UTF-8&charset-target=UTF-8"
            f"&ecc=L&color={color}&bgcolor={bgcolor}&margin=1&qzone=1&format=png"
        ),
        caption=(
            f"<i>Ваша реферальная ссылка: <b>{reflink}</b>\n\n"
            "За каждого приглашённого пользователя вы получаете 1 <b>📦 Лутбокс</b></i>"
        ), 
    )
