from ... import bot
from ...misc import ITEMS
import sqlite3
from ...database import cur
from ...database.functions import tglog, get_embedded_link

from aiogram.utils.deep_linking import get_start_link
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)


async def set_user_bio(call: CallbackQuery) -> None:
    cur.update("userdata").set(process="setbio").where(
        user_id=call.from_user.id).commit()

    await bot.send_message(
        call.message.chat.id,
        "<i>📝 Введите новое описание профиля:</i>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="🚫 Отмена",
                callback_data="cancel_process"
            )
        )
    )


async def put_mask_off(
    call: CallbackQuery,
    user_id: int,
    anon: bool = False
) -> None:
    if mask := cur.execute(
        f"SELECT mask FROM userdata WHERE user_id={user_id}"
    ).fetchone()[0]:
        if mask is None:
            return

        for item in ITEMS:
            if ITEMS[item].emoji == mask and ITEMS[item].type == "mask":
                mask = item

        cur.update("userdata").set(mask="NULL").where(user_id=user_id).commit()
        try:
            cur.update("userdata").add(**{mask: 1}).where(
                user_id=user_id).commit()
        except sqlite3.OperationalError:
            await call.message.answer("‼️ Your mask does not exist")
        if not anon:
            return await call.answer("🦹🏼 Ваша маска снята.", show_alert=True)


async def put_mask_on(call: CallbackQuery, item: str) -> None:
    user_id = call.from_user.id

    await put_mask_off(call, user_id, True)
    itemcount = cur.select(item, "userdata").where(user_id=user_id).one()

    if itemcount > 0:
        cur.update("userdata").add(**{item: -1}).where(
            user_id=user_id).commit()

        cur.update("userdata").set(mask=ITEMS[item].emoji).where(
            user_id=user_id).commit()

        return await call.answer(
            f"Отличный выбор! Ваша маска: {ITEMS[item].emoji}",
            show_alert=True
        )
        # await achieve(a, message.chat.id, "msqrd")
    else:
        await call.answer(
            "🚫 У вас нет этого предмета",
            show_alert=True
        )


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
            f"https://api.qrserver.com/v1/create-qr-code/?data={reflink}&"
            "size=512x512&charset-source=UTF-8&charset-target=UTF-8"
            f"&ecc=L&color={color}&bgcolor={bgcolor}&margin=1&qzone=1&format="
            "png"
        ),
        caption=(
            f"<i>Ваша реферальная ссылка: <b>{reflink}</b>\n\n"
            "За каждого приглашённого пользователя вы получаете 1 "
            "<b>📦 Лутбокс</b></i>"
        ),
    )


async def privacy_settings(call: CallbackQuery):
    markup = InlineKeyboardMarkup(row_width=1)
    user_id = call.from_user.id
    profile_type = cur.select("profile_type", "userdata").where(
        user_id=user_id).one()
    markup.add(
        InlineKeyboardButton(
            f"🔐 Тип профиля: {'Открытый' if profile_type == 'public' else 'Закрытый'}",  # noqa
            callback_data="toggle_profile_type"
        ),
        InlineKeyboardButton(
            "🔑 Ключ доступа",
            callback_data="access-key"
        ),
        InlineKeyboardButton(
            "🔙 Выйти из аккаунта",
            callback_data="log-out"
        ),
        InlineKeyboardButton(
            "🗑 Удалить аккаунт",
            callback_data="delete-account",
        ),
        InlineKeyboardButton(
            "◀ Назад",
            callback_data="cancel_action",
        )
    )
    await call.message.answer(
        '🔏<i><b>Настройки конфиденциальности</b></i>',
        reply_markup=markup
    )


async def delete_account(call: CallbackQuery):
    """
    Callback for account deleting menu

    :param call - callback:
    """

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='✅ Подтвердить',
            callback_data='delete_account_confirm'
        ),
        InlineKeyboardButton(
            text='❌ Отмена',
            callback_data='cancel_action'
        )
    )

    await call.message.answer(
        '<i>😨 Вы точно хотите удалить ваш аккаунт вместе со всеми его '
        'деньгами, ресурсами, достижениями? Это действие невозможно '
        'отменить</i>',
        reply_markup=markup
    )


async def delete_account_confirm(call: CallbackQuery):
    """
    Callback for account removal

    :param call - callback:
    """
    user_id = call.from_user.id

    embedded_link = await get_embedded_link(user_id)
    cur.execute(
        f"DELETE FROM userdata WHERE user_id={user_id}"
    ).commit()

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='😪 Хорошо',
            callback_data='cancel_action'
        ),
        InlineKeyboardButton(
            text='➕ Создать новый',
            callback_data='sign_up'
        )
    )
    await call.message.answer(
        '<i>😥 Вот и всё... Ваш аккаунт удалён. Вернуть его невозможно</i>',
        reply_markup=markup
    )

    await tglog(
            message=(
                f"😪 <b>{embedded_link}</b> удалил свой аккаунт"
            ),
            tag='#delete_account'
    )


async def log_out(call: CallbackQuery):
    """
    Callback for logging out

    :param call - callback:
    """
    user_id = call.from_user.id

    embedded_link = await get_embedded_link(user_id)
    id = cur.select("id", "userdata").where(user_id=user_id).one()
    cur.update("userdata").set(user_id=0).where(id=id).commit()

    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(
            text='😪 Хорошо',
            callback_data='cancel_action'
        )
    )
    await call.message.answer(
        '<i>🥱 Вы вышли из аккаунта. Надеемся, что вы вспомните свой ключ'
        ' доступа, если вдруг вам захочется вернуть свой аккаунт</i>',
        reply_markup=markup
    )

    await tglog(
            message=(
                f"➡ <b>{embedded_link}</b> вышел из аккаунта"
            ),
            tag='#log_out'
    )
